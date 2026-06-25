from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.order import Order
from app.schemas.order_schema import (
    OrderCreate,
    OrderCustomerUpdate,
    OrderResponse,
    OrderStatusUpdate,
)
from app.services.order_service import OrderService


router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)

order_service = OrderService()


def get_order_or_404(order_id: int, db: Session) -> Order:
    order = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found."
        )

    return order


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    for item in order.items:
        product = order_service.get_product_for_order_item(db, item.model_dump())

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found or unavailable: {item.product_name}"
            )

    new_order = order_service.create_manual_order(db, order.model_dump())
    return new_order


@router.get("/", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return (
        db.query(Order)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
        .all()
    )


@router.get("/session/{session_id}", response_model=List[OrderResponse])
def get_orders_by_session(session_id: str, db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.session_id == session_id)
        .order_by(Order.created_at.desc())
        .all()
    )

    if not orders:
        raise HTTPException(
            status_code=404,
            detail="No orders found for this session."
        )

    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    return get_order_or_404(order_id, db)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    if status_update.status not in order_service.ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed statuses are: {order_service.ALLOWED_STATUSES}"
        )

    order = get_order_or_404(order_id, db)
    return order_service.update_order_status(db, order, status_update.status)


@router.patch("/{order_id}/customer", response_model=OrderResponse)
def update_order_customer_details(
    order_id: int,
    customer_update: OrderCustomerUpdate,
    db: Session = Depends(get_db)
):
    order = get_order_or_404(order_id, db)
    update_data = customer_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one customer or delivery field to update."
        )

    return order_service.update_order_details(db, order, update_data)
