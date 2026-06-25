from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.product import Product


DEFAULT_PRODUCTS = [
    {
        "name": "Chocolate Chip Cookie",
        "description": "Classic cookie with chocolate chips.",
        "price": 2.00,
        "available": True,
    },
    {
        "name": "Shortbread Cookie",
        "description": "Rich buttery shortbread cookie.",
        "price": 2.00,
        "available": True,
    },
    {
        "name": "Macaron Cookie",
        "description": "Colourful French-style macaron.",
        "price": 2.50,
        "available": True,
    },
    {
        "name": "Macaroon Cookie",
        "description": "Sweet coconut macaroon cookie.",
        "price": 2.00,
        "available": True,
    },
    {
        "name": "Biscotti Cookie",
        "description": "Crunchy Italian-style biscotti.",
        "price": 2.00,
        "available": True,
    },
    {
        "name": "Sugar Cookie",
        "description": "Simple sweet sugar cookie.",
        "price": 2.00,
        "available": True,
    },
    {
        "name": "Oatmeal Raisin Cookie",
        "description": "Oatmeal cookie with raisins.",
        "price": 2.00,
        "available": True,
    },
    {
        "name": "Gingerbread Cookie",
        "description": "Spiced gingerbread cookie.",
        "price": 2.00,
        "available": True,
    },
]


def seed_products(db: Session):
    existing_products = db.query(Product).count()

    if existing_products > 0:
        return

    products = [Product(**product_data) for product_data in DEFAULT_PRODUCTS]
    db.add_all(products)
    db.commit()


def seed_database():
    db = SessionLocal()

    try:
        seed_products(db)
    finally:
        db.close()
