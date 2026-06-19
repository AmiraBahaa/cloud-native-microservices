from pydantic import BaseModel
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderCreate(BaseModel):
    product: str
    quantity: int
    price: float


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    product: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
