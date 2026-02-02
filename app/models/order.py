"""
Order model linked to Outlets.
"""
from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer, String, DateTime, Date, Numeric, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.outlet import Outlet
    from app.models.box import Box


class OrderStatus(enum.Enum):
    """Order lifecycle status."""
    PENDING = "pending"           # Order received, not processed
    CONFIRMED = "confirmed"       # Order confirmed, awaiting packing
    PACKING = "packing"           # Being packed into boxes
    PACKED = "packed"             # Packed, ready for dispatch
    IN_TRANSIT = "in_transit"     # On delivery route
    DELIVERED = "delivered"       # Successfully delivered
    PARTIAL = "partial"           # Partially delivered
    CANCELLED = "cancelled"       # Order cancelled
    RETURNED = "returned"         # Order returned


class OrderPriority(enum.Enum):
    """Order urgency level."""
    URGENT = 1        # Same-day delivery required
    HIGH = 2          # Next-day delivery
    NORMAL = 3        # Standard delivery window
    LOW = 4           # Flexible timing


class Order(Base):
    """
    Customer order entity linked to an Outlet.
    
    Orders contain products to be delivered to outlets.
    Multiple orders can be packed into boxes for efficient transport.
    """
    __tablename__ = "orders"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Order Identification
    order_number: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True
    )
    
    # Foreign Key - Link to Outlet
    outlet_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("outlets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Order Details
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Volume and Weight (for bin packing calculations)
    total_volume_cm3: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="Total volume in cubic centimeters"
    )
    total_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        default=0,
        comment="Total weight in kilograms"
    )
    
    # Item count
    item_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Financial
    order_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Order monetary value"
    )
    
    # Status and Priority
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False
    )
    priority: Mapped[OrderPriority] = mapped_column(
        SQLEnum(OrderPriority),
        default=OrderPriority.NORMAL,
        nullable=False
    )
    
    # Dates
    order_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False
    )
    requested_delivery_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )
    actual_delivery_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    outlet: Mapped["Outlet"] = relationship("Outlet", back_populates="orders")
    boxes: Mapped[list["Box"]] = relationship(
        "Box",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_order_outlet_status", outlet_id, status),
        Index("idx_order_delivery_date", requested_delivery_date),
        Index("idx_order_priority_status", priority, status),
    )
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, number='{self.order_number}', outlet_id={self.outlet_id}, status={self.status.value})>"
