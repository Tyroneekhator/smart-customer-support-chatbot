from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.chat_message import ChatMessage
from app.models.order import Order, OrderItem
from app.models.product import Product


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_messages = db.query(ChatMessage).count()
    total_user_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.sender == "user")
        .count()
    )
    total_bot_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.sender == "bot")
        .count()
    )

    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    confirmed_orders = db.query(Order).filter(Order.status == "confirmed").count()
    completed_orders = db.query(Order).filter(Order.status == "completed").count()
    cancelled_orders = db.query(Order).filter(Order.status == "cancelled").count()

    revenue_statuses = ["confirmed", "preparing", "out_for_delivery", "completed"]
    total_revenue = (
        db.query(func.coalesce(func.sum(Order.total_price), 0.0))
        .filter(Order.status.in_(revenue_statuses))
        .scalar()
    )

    total_products = db.query(Product).count()
    available_products = (
        db.query(Product)
        .filter(Product.available == True)  # noqa: E712
        .count()
    )

    popular_intents = (
        db.query(ChatMessage.intent, func.count(ChatMessage.intent))
        .filter(ChatMessage.intent.isnot(None))
        .group_by(ChatMessage.intent)
        .order_by(func.count(ChatMessage.intent).desc())
        .limit(5)
        .all()
    )

    popular_products = (
        db.query(
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.line_total).label("total_sales"),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status != "cancelled")
        .group_by(OrderItem.product_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    recent_orders = (
        db.query(Order)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_messages": total_messages,
        "total_user_messages": total_user_messages,
        "total_bot_messages": total_bot_messages,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "total_revenue": round(float(total_revenue or 0.0), 2),
        "total_products": total_products,
        "available_products": available_products,
        "popular_intents": [
            {
                "intent": intent,
                "count": count
            }
            for intent, count in popular_intents
        ],
        "popular_products": [
            {
                "product_name": product_name,
                "total_quantity": int(total_quantity or 0),
                "total_sales": round(float(total_sales or 0.0), 2),
            }
            for product_name, total_quantity, total_sales in popular_products
        ],
        "recent_orders": [
            {
                "id": order.id,
                "session_id": order.session_id,
                "status": order.status,
                "customer_name": order.customer_name,
                "delivery_method": order.delivery_method,
                "total_price": order.total_price,
                "created_at": order.created_at,
                "items": [
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "line_total": item.line_total,
                    }
                    for item in order.items
                ],
            }
            for order in recent_orders
        ]
    }
