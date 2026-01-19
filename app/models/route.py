"""
Route model with Driver/Vehicle assignment.
"""
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Integer, String, DateTime, Date, Numeric, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class RouteStatus(enum.Enum):
    """Route lifecycle status."""
    DRAFT = "draft"               # Route being planned
    PLANNED = "planned"           # Route finalized, not started
    ASSIGNED = "assigned"         # Driver/vehicle assigned
    IN_PROGRESS = "in_progress"   # Route currently active
    COMPLETED = "completed"       # All deliveries done
    CANCELLED = "cancelled"       # Route cancelled
    PARTIAL = "partial"           # Partially completed


class VehicleType(enum.Enum):
    """Types of delivery vehicles."""
    MOTORCYCLE = "motorcycle"     # Small parcels, urban
    VAN = "van"                   # Standard deliveries
    TRUCK_SMALL = "truck_small"   # 3.5 ton
    TRUCK_MEDIUM = "truck_medium" # 7.5 ton
    TRUCK_LARGE = "truck_large"   # 18+ ton
    REFRIGERATED = "refrigerated" # Cold chain


class Route(Base):
    """
    Delivery route entity with driver and vehicle assignment.
    
    A route represents a planned delivery journey covering
    multiple outlets in an optimized sequence.
    """
    __tablename__ = "routes"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Route Identification
    route_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Driver Assignment
    driver_id: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="External driver system ID"
    )
    driver_name: Mapped[str] = mapped_column(String(255), nullable=True)
    driver_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Vehicle Assignment
    vehicle_id: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="External vehicle/fleet system ID"
    )
    vehicle_plate: Mapped[str] = mapped_column(String(20), nullable=True)
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SQLEnum(VehicleType),
        default=VehicleType.VAN,
        nullable=True
    )
    
    # Vehicle Capacity
    max_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Vehicle max payload in kg"
    )
    max_volume_cm3: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="Vehicle cargo volume in cm³"
    )
    
    # Route Planning
    planned_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )
    planned_start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    planned_end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Actual Times
    actual_start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    actual_end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Route Metrics
    planned_distance_km: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Planned total distance"
    )
    actual_distance_km: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Actual GPS-tracked distance"
    )
    planned_stops: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    completed_stops: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Load Summary
    total_boxes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False
    )
    
    # Fuel Tracking
    fuel_start_liters: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=True
    )
    fuel_end_liters: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=True
    )
    fuel_consumed_liters: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=True
    )
    
    # Status
    status: Mapped[RouteStatus] = mapped_column(
        SQLEnum(RouteStatus),
        default=RouteStatus.DRAFT,
        nullable=False
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
    boxes: Mapped[list["Box"]] = relationship(
        "Box",
        back_populates="route",
        order_by="Box.sequence_index"
    )
    route_nodes: Mapped[list["RouteNode"]] = relationship(
        "RouteNode",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteNode.sequence_order"
    )
    
    __table_args__ = (
        Index("idx_route_date_status", planned_date, status),
        Index("idx_route_driver_date", driver_id, planned_date),
        Index("idx_route_vehicle_date", vehicle_id, planned_date),
    )
    
    @property
    def fuel_efficiency_km_per_liter(self) -> float | None:
        """Calculate fuel efficiency."""
        if self.fuel_consumed_liters and self.actual_distance_km:
            if self.fuel_consumed_liters > 0:
                return float(self.actual_distance_km / self.fuel_consumed_liters)
        return None
    
    @property
    def duration_minutes(self) -> int | None:
        """Calculate actual route duration in minutes."""
        if self.actual_start_time and self.actual_end_time:
            delta = self.actual_end_time - self.actual_start_time
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def completion_percentage(self) -> float:
        """Calculate route completion percentage."""
        if self.planned_stops == 0:
            return 0.0
        return (self.completed_stops / self.planned_stops) * 100
    
    def __repr__(self) -> str:
        return f"<Route(id={self.id}, code='{self.route_code}', driver='{self.driver_id}', status={self.status.value})>"
