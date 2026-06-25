from sqlalchemy import inspect, text

from app.database import engine


ORDER_COLUMN_MIGRATIONS = {
    "customer_name": "VARCHAR",
    "customer_email": "VARCHAR",
    "customer_phone": "VARCHAR",
    "delivery_method": "VARCHAR DEFAULT 'pickup'",
    "delivery_address": "VARCHAR",
    "notes": "VARCHAR",
    "subtotal": "FLOAT DEFAULT 0.0",
    "total_price": "FLOAT DEFAULT 0.0",
    "updated_at": "DATETIME",
}


STAGE3_ORDER_COLUMNS = [
    "id",
    "session_id",
    "status",
    "customer_name",
    "customer_email",
    "customer_phone",
    "delivery_method",
    "delivery_address",
    "notes",
    "subtotal",
    "total_price",
    "created_at",
    "updated_at",
]


LEGACY_ORDER_COLUMNS = {"product_name", "quantity"}


def get_table_names():
    inspector = inspect(engine)
    return set(inspector.get_table_names())


def get_column_names(table_name: str):
    inspector = inspect(engine)
    return {column["name"] for column in inspector.get_columns(table_name)}


def add_missing_order_columns():
    inspector = inspect(engine)

    if "orders" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("orders")}

    with engine.begin() as connection:
        for column_name, column_type in ORDER_COLUMN_MIGRATIONS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE orders ADD COLUMN {column_name} {column_type}")
                )


def migrate_legacy_order_rows_to_items():
    """Convert Stage 1/2 order rows into Stage 3 order item rows.

    Older versions stored product_name and quantity directly on orders.
    Stage 3 stores products inside order_items. This keeps old local data useful
    instead of forcing the user to delete chatbot.db.
    """
    table_names = get_table_names()

    if "orders" not in table_names or "order_items" not in table_names:
        return

    order_columns = get_column_names("orders")

    if "product_name" not in order_columns or "quantity" not in order_columns:
        return

    with engine.begin() as connection:
        legacy_orders = connection.execute(
            text(
                """
                SELECT id, product_name, quantity
                FROM orders
                WHERE product_name IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM order_items WHERE order_items.order_id = orders.id
                )
                """
            )
        ).mappings().all()

        for legacy_order in legacy_orders:
            product = connection.execute(
                text(
                    """
                    SELECT id, price
                    FROM products
                    WHERE lower(name) = lower(:product_name)
                    LIMIT 1
                    """
                ),
                {"product_name": legacy_order["product_name"]},
            ).mappings().first()

            unit_price = float(product["price"]) if product else 0.0
            quantity = int(legacy_order["quantity"] or 1)
            line_total = round(quantity * unit_price, 2)

            connection.execute(
                text(
                    """
                    INSERT INTO order_items (
                        order_id,
                        product_id,
                        product_name,
                        quantity,
                        unit_price,
                        line_total,
                        created_at
                    )
                    VALUES (
                        :order_id,
                        :product_id,
                        :product_name,
                        :quantity,
                        :unit_price,
                        :line_total,
                        CURRENT_TIMESTAMP
                    )
                    """
                ),
                {
                    "order_id": legacy_order["id"],
                    "product_id": product["id"] if product else None,
                    "product_name": legacy_order["product_name"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": line_total,
                },
            )

            connection.execute(
                text(
                    """
                    UPDATE orders
                    SET subtotal = :line_total,
                        total_price = :line_total,
                        updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
                    WHERE id = :order_id
                    """
                ),
                {
                    "line_total": line_total,
                    "order_id": legacy_order["id"],
                },
            )


def rebuild_orders_table_without_legacy_columns():
    """Remove old NOT NULL product_name/quantity columns from the orders table.

    SQLite does not reliably remove old NOT NULL constraints from an existing
    table. Stage 1/2 created orders.product_name as NOT NULL, but Stage 3 no
    longer inserts product_name directly into orders. Without rebuilding this
    table, creating a new pending cart order raises:

        sqlite3.IntegrityError: NOT NULL constraint failed: orders.product_name

    This migration rebuilds the orders table using the Stage 3 schema and keeps
    existing order IDs, statuses, customer details, timestamps, and totals.
    """
    table_names = get_table_names()

    if "orders" not in table_names:
        return

    order_columns = get_column_names("orders")

    if not LEGACY_ORDER_COLUMNS.intersection(order_columns):
        return

    temporary_table = "orders_stage3_migration"

    def select_expression(column_name: str) -> str:
        if column_name in order_columns:
            if column_name == "delivery_method":
                return "COALESCE(delivery_method, 'pickup') AS delivery_method"
            if column_name in {"subtotal", "total_price"}:
                return f"COALESCE({column_name}, 0.0) AS {column_name}"
            if column_name in {"created_at", "updated_at"}:
                return f"COALESCE({column_name}, CURRENT_TIMESTAMP) AS {column_name}"
            return column_name

        defaults = {
            "status": "'pending' AS status",
            "customer_name": "NULL AS customer_name",
            "customer_email": "NULL AS customer_email",
            "customer_phone": "NULL AS customer_phone",
            "delivery_method": "'pickup' AS delivery_method",
            "delivery_address": "NULL AS delivery_address",
            "notes": "NULL AS notes",
            "subtotal": "0.0 AS subtotal",
            "total_price": "0.0 AS total_price",
            "created_at": "CURRENT_TIMESTAMP AS created_at",
            "updated_at": "CURRENT_TIMESTAMP AS updated_at",
        }
        return defaults[column_name]

    select_columns = ",\n            ".join(select_expression(column) for column in STAGE3_ORDER_COLUMNS)
    insert_columns = ", ".join(STAGE3_ORDER_COLUMNS)

    with engine.begin() as connection:
        connection.execute(text("PRAGMA foreign_keys=OFF"))
        connection.execute(text(f"DROP TABLE IF EXISTS {temporary_table}"))
        connection.execute(
            text(
                f"""
                CREATE TABLE {temporary_table} (
                    id INTEGER NOT NULL PRIMARY KEY,
                    session_id VARCHAR NOT NULL,
                    status VARCHAR,
                    customer_name VARCHAR,
                    customer_email VARCHAR,
                    customer_phone VARCHAR,
                    delivery_method VARCHAR,
                    delivery_address VARCHAR,
                    notes VARCHAR,
                    subtotal FLOAT,
                    total_price FLOAT,
                    created_at DATETIME,
                    updated_at DATETIME
                )
                """
            )
        )
        connection.execute(
            text(
                f"""
                INSERT INTO {temporary_table} ({insert_columns})
                SELECT
                    {select_columns}
                FROM orders
                """
            )
        )
        connection.execute(text("DROP TABLE orders"))
        connection.execute(text(f"ALTER TABLE {temporary_table} RENAME TO orders"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_session_id ON orders (session_id)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_status ON orders (status)"))
        connection.execute(text("PRAGMA foreign_keys=ON"))


def run_lightweight_migrations():
    # Step 1: Add the new Stage 3 columns to old databases so existing data can
    # be copied safely.
    add_missing_order_columns()

    # Step 2: Preserve old Stage 1/2 order rows by converting their product_name
    # and quantity values into order_items.
    migrate_legacy_order_rows_to_items()

    # Step 3: Rebuild the orders table to remove the old product_name/quantity
    # columns and their NOT NULL constraints.
    rebuild_orders_table_without_legacy_columns()
