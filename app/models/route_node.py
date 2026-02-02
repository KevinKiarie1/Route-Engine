"""
RouteNode model for telemetry logs with arrival/departure timestamps.
Designed for TimescaleDB hypertable for efficient time-series queries.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer, String, DateTime, Numeric, Text, Boolean,
    ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point
import enum

from app.core.database import Base
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.route import Route
    from app.models.outlet import Outlet


class NodeStatus(enum.Enum):
    """Delivery node status."""
    PENDING = "pending"       # Not yet visited
    EN_ROUTE = "en_route"     # Driver heading to this stop
    ARRIVED = "arrived"       # Driver at location
    SERVICING = "servicing"   # Delivery in progress
    COMPLETED = "completed"   # Delivery successful
    FAILED = "failed"         # Delivery failed
    SKIPPED = "skipped"       # Stop skipped


class DeliveryResult(enum.Enum):
    """Outcome of delivery attempt."""
    SUCCESS = "success"
    PARTIAL = "partial"           # Partial delivery
    RECIPIENT_ABSENT = "recipient_absent"
    REFUSED = "refused"
    WRONG_ADDRESS = "wrong_address"
    ACCESS_DENIED = "access_denied"
    OTHER_FAILURE = "other_failure"


class RouteNode(Base):
    """
    Route node entity for telemetry and delivery tracking.
    
    Each node represents a stop on a route with:
    - GPS coordinates
    - Arrival/departure timestamps for service time calculation
    - Delivery status and outcome
    - Real-time telemetry data
    
    Designed as a TimescaleDB hypertable partitioned by arrival_time
    for efficient time-series queries and automatic data retention.
    """
    __tablename__ = "route_nodes"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    route_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    outlet_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("outlets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Sequence (order in route)
    sequence_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Stop order in route (1-based)"
    )
    
    # GPS Coordinates - Planned vs Actual
    planned_location: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=settings.SRID),
        nullable=True,
        comment="Expected outlet location"
    )
    arrival_location: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=settings.SRID),
        nullable=True,
        comment="Actual GPS at arrival"
    )
    departure_location: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=settings.SRID),
        nullable=True,
        comment="Actual GPS at departure"
    )
    
    # Timestamps - Core Telemetry
    planned_arrival_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        comment="ETA at this stop"
    )
    arrival_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        comment="Actual arrival timestamp - TimescaleDB partition key"
    )
    departure_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        comment="Actual departure timestamp"
    )
    
    # Service Time (derived from arrival/departure)
    service_time_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Calculated time spent at stop"
    )
    
    # Distance & Fuel Telemetry
    distance_from_previous_km: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=True,
        comment="Distance from previous stop"
    )
    cumulative_distance_km: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Total distance from route start"
    )
    fuel_consumed_liters: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="Fuel used since previous stop"
    )
    
    # Odometer Readings
    odometer_arrival_km: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    odometer_departure_km: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    # Delivery Metrics
    boxes_delivered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    boxes_returned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    status: Mapped[NodeStatus] = mapped_column(
        SQLEnum(NodeStatus),
        default=NodeStatus.PENDING,
        nullable=False
    )
    delivery_result: Mapped[DeliveryResult] = mapped_column(
        SQLEnum(DeliveryResult),
        nullable=True
    )
    
    # Notes & Signatures
    driver_notes: Mapped[str] = mapped_column(Text, nullable=True)
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=True)
    signature_captured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    photo_captured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Geofence Validation
    is_within_geofence: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        comment="Whether arrival GPS was within outlet geofence"
    )
    geofence_distance_meters: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=True,
        comment="Distance from outlet center at arrival"
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
    route: Mapped["Route"] = relationship("Route", back_populates="route_nodes")
    outlet: Mapped["Outlet"] = relationship("Outlet")
    
    __table_args__ = (
        # Composite indexes for common queries
        Index("idx_route_node_route_sequence", route_id, sequence_order),
        Index("idx_route_node_arrival_time", arrival_time),
        Index("idx_route_node_outlet_time", outlet_id, arrival_time),
        Index("idx_route_node_status", status),
        
        # Spatial index for arrival location
        Index("idx_route_node_arrival_location", arrival_location, postgresql_using="gist"),
        
        # Unique constraint: one stop per outlet per route
        UniqueConstraint("route_id", "outlet_id", name="uq_route_outlet"),
    )
    
    @classmethod
    def create_point(cls, latitude: float, longitude: float):
        """Create a PostGIS point from coordinates."""
        point = Point(longitude, latitude)
        return from_shape(point, srid=settings.SRID)
    
    @property
    def arrival_lat(self) -> float | None:
        """Get arrival latitude."""
        if self.arrival_location:
            return to_shape(self.arrival_location).y
        return None
    
    @property
    def arrival_long(self) -> float | None:
        """Get arrival longitude."""
        if self.arrival_location:
            return to_shape(self.arrival_location).x
        return None
    
    @property
    def calculated_service_time(self) -> int | None:
        """Calculate service time from timestamps."""
        if self.arrival_time and self.departure_time:
            delta = self.departure_time - self.arrival_time
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def arrival_delay_minutes(self) -> int | None:
        """Calculate delay from planned arrival."""
        if self.planned_arrival_time and self.arrival_time:
            delta = self.arrival_time - self.planned_arrival_time
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def is_on_time(self) -> bool | None:
        """Check if arrival was on time (within 15 min tolerance)."""
        delay = self.arrival_delay_minutes
        if delay is not None:
            return delay <= 15
        return None
    
    def record_arrival(
        self,
        latitude: float,
        longitude: float,
        timestamp: datetime | None = None
    ) -> None:
        """Record driver arrival at this stop."""
        self.arrival_time = timestamp or datetime.utcnow()
        self.arrival_location = self.create_point(latitude, longitude)
        self.status = NodeStatus.ARRIVED
    
    def record_departure(
        self,
        latitude: float,
        longitude: float,
        timestamp: datetime | None = None
    ) -> None:
        """Record driver departure from this stop."""
        self.departure_time = timestamp or datetime.utcnow()
        self.departure_location = self.create_point(latitude, longitude)
        
        # Calculate service time
        if self.arrival_time:
            delta = self.departure_time - self.arrival_time
            self.service_time_minutes = int(delta.total_seconds() / 60)
    
    def __repr__(self) -> str:
        return f"<RouteNode(id={self.id}, route={self.route_id}, outlet={self.outlet_id}, seq={self.sequence_order}, status={self.status.value})>"
