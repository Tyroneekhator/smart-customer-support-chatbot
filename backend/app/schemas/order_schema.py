from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    quantity: int = Field(default=1, ge=1)


class OrderCreate(BaseModel):
    session_id: str
    items: List[OrderItemCreate] = Field(..., min_length=1)
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    delivery_method: str = Field(default="pickup", pattern="^(pickup|delivery)$")
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: str


class OrderCustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    delivery_method: Optional[str] = Field(default=None, pattern="^(pickup|delivery)$")
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    product_id: Optional[int]
    product_name: str
    quantity: int
    unit_price: float
    line_total: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    session_id: str
    status: str
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_phone: Optional[str]
    delivery_method: Optional[str]
    delivery_address: Optional[str]
    notes: Optional[str]
    subtotal: float
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
