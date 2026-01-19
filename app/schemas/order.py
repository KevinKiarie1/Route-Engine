"""
Pydantic schemas for Order validation and serialization.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class OrderStatusEnum(str, Enum):
    """Order status for API."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PACKING = "packing"
    PACKED = "packed"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class OrderPriorityEnum(str, Enum):
    """Order priority for API."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class OrderBase(BaseModel):
    """Base schema for order fields."""
    order_number: str = Field(..., min_length=1, max_length=50)
    outlet_id: int = Field(..., gt=0)
    description: Optional[str] = None
    total_volume_cm3: Decimal = Field(default=Decimal("0"), ge=0)
    total_weight_kg: Decimal = Field(default=Decimal("0"), ge=0)
    item_count: int = Field(default=1, ge=1)
    order_value: Optional[Decimal] = Field(default=None, ge=0)
    priority: OrderPriorityEnum = Field(default=OrderPriorityEnum.NORMAL)
    requested_delivery_date: Optional[date] = None


class OrderCreate(OrderBase):
    """Schema for creating a new order."""
    pass


class OrderUpdate(BaseModel):
    """Schema for updating an order."""
    description: Optional[str] = None
    total_volume_cm3: Optional[Decimal] = Field(default=None, ge=0)
    total_weight_kg: Optional[Decimal] = Field(default=None, ge=0)
    item_count: Optional[int] = Field(default=None, ge=1)
    order_value: Optional[Decimal] = Field(default=None, ge=0)
    priority: Optional[OrderPriorityEnum] = None
    status: Optional[OrderStatusEnum] = None
    requested_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None


class OrderResponse(BaseModel):
    """Schema for order API response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_number: str
    outlet_id: int
    description: Optional[str]
    total_volume_cm3: Decimal
    total_weight_kg: Decimal
    item_count: int
    order_value: Optional[Decimal]
    status: str
    priority: str
    order_date: date
    requested_delivery_date: Optional[date]
    actual_delivery_date: Optional[date]
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    """Paginated order list."""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    pages: int
