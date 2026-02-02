"""
Box model linked to Orders with weight and sequence_index for LIFO loading.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer, String, DateTime, Numeric, Boolean,
    ForeignKey, Enum as SQLEnum, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.route import Route


class BoxSize(enum.Enum):
    """Standard box size categories."""
    SMALL = "small"       # 30x20x15 cm
    MEDIUM = "medium"     # 40x30x25 cm
    LARGE = "large"       # 60x40x35 cm
    XLARGE = "xlarge"     # 80x60x50 cm
    CUSTOM = "custom"     # Custom dimensions


class BoxStatus(enum.Enum):
    """Box lifecycle status."""
    EMPTY = "empty"           # Box created, not packed
    PACKING = "packing"       # Currently being packed
    SEALED = "sealed"         # Packed and sealed
    LOADED = "loaded"         # Loaded onto vehicle
    IN_TRANSIT = "in_transit" # On delivery route
    DELIVERED = "delivered"   # Successfully delivered
    RETURNED = "returned"     # Returned to warehouse


class Box(Base):
    """
    Box entity for order packing and LIFO route sequencing.
    
    Boxes are the physical units loaded onto vehicles.
    sequence_index determines LIFO unloading order:
    - Higher sequence_index = loaded first, unloaded last
    - Lower sequence_index = loaded last, unloaded first
    
    This enables efficient route delivery where the first
    delivery stop's boxes are on top (loaded last).
    """
    __tablename__ = "boxes"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Box Identification
    barcode: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique barcode/QR code for scanning"
    )
    
    # Foreign Key - Link to Order
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Foreign Key - Link to Route (optional, assigned during route planning)
    route_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("routes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Box Dimensions (in centimeters)
    size_category: Mapped[BoxSize] = mapped_column(
        SQLEnum(BoxSize),
        default=BoxSize.MEDIUM,
        nullable=False
    )
    length_cm: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
        default=40.0
    )
    width_cm: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
        default=30.0
    )
    height_cm: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
        default=25.0
    )
    
    # Weight
    weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(8, 3),
        nullable=False,
        default=0,
        comment="Total weight including contents in kilograms"
    )
    max_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(8, 3),
        nullable=False,
        default=25.0,
        comment="Maximum allowed weight"
    )
    
    # LIFO Sequence Index for Route Loading
    # Lower index = unload first (top of stack)
    # Higher index = unload last (bottom of stack)
    sequence_index: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="LIFO sequence: lower index = unload first"
    )
    
    # Packing Efficiency
    volume_used_cm3: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        comment="Volume of contents"
    )
    
    # Status
    status: Mapped[BoxStatus] = mapped_column(
        SQLEnum(BoxStatus),
        default=BoxStatus.EMPTY,
        nullable=False
    )
    
    # Flags
    is_fragile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_refrigeration: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_stackable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    packed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
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
    order: Mapped["Order"] = relationship("Order", back_populates="boxes")
    route: Mapped["Route"] = relationship("Route", back_populates="boxes")
    
    __table_args__ = (
        Index("idx_box_route_sequence", route_id, sequence_index),
        Index("idx_box_order_status", order_id, status),
        CheckConstraint("weight_kg <= max_weight_kg", name="check_weight_limit"),
        CheckConstraint("sequence_index >= 0", name="check_sequence_positive"),
    )
    
    @property
    def volume_cm3(self) -> Decimal:
        """Calculate box volume in cubic centimeters."""
        return self.length_cm * self.width_cm * self.height_cm
    
    @property
    def fill_percentage(self) -> float:
        """Calculate how full the box is."""
        if self.volume_cm3 == 0:
            return 0.0
        return float(self.volume_used_cm3 / self.volume_cm3 * 100)
    
    @property
    def remaining_capacity_cm3(self) -> Decimal:
        """Calculate remaining volume capacity."""
        return self.volume_cm3 - self.volume_used_cm3
    
    @property
    def remaining_weight_kg(self) -> Decimal:
        """Calculate remaining weight capacity."""
        return self.max_weight_kg - self.weight_kg
    
    def __repr__(self) -> str:
        return f"<Box(id={self.id}, barcode='{self.barcode}', order_id={self.order_id}, sequence={self.sequence_index})>"
