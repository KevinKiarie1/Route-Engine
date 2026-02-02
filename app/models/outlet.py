"""
Outlet model with PostGIS geospatial support.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, Enum as SQLEnum, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point
import enum

from app.core.database import Base
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.order import Order


class OutletPriority(enum.Enum):
    """Priority levels for outlet delivery scheduling."""
    CRITICAL = 1      # Must be delivered first (e.g., hospitals, schools)
    HIGH = 2          # Important retail partners
    MEDIUM = 3        # Standard outlets
    LOW = 4           # Flexible delivery window
    DEFERRED = 5      # Can be postponed if needed


class OutletStatus(enum.Enum):
    """Operational status of an outlet."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Outlet(Base):
    """
    Retail outlet entity with geospatial coordinates.
    
    Uses PostGIS POINT geometry for GPS location storage,
    enabling efficient spatial queries (nearest neighbor, radius search, etc.)
    """
    __tablename__ = "outlets"
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Outlet Information
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Contact Information
    contact_name: Mapped[str] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Geospatial - PostGIS POINT with SRID 4326 (WGS 84)
    # Stored as POINT(longitude latitude) - note: longitude comes first in PostGIS
    location: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=settings.SRID),
        nullable=False
    )
    
    # Priority & Status
    priority: Mapped[OutletPriority] = mapped_column(
        SQLEnum(OutletPriority),
        default=OutletPriority.MEDIUM,
        nullable=False
    )
    status: Mapped[OutletStatus] = mapped_column(
        SQLEnum(OutletStatus),
        default=OutletStatus.ACTIVE,
        nullable=False
    )
    
    # Delivery Window (in minutes from midnight)
    delivery_window_start: Mapped[int] = mapped_column(Integer, default=480, nullable=False)  # 8:00 AM
    delivery_window_end: Mapped[int] = mapped_column(Integer, default=1080, nullable=False)   # 6:00 PM
    
    # Average service time in minutes (for route optimization)
    avg_service_time: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    
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
    
    # Relationships (to be added as other models are created)
    # orders: Mapped[list["Order"]] = relationship("Order", back_populates="outlet")
    
    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="outlet")
    
    # Spatial index for efficient geospatial queries
    __table_args__ = (
        Index("idx_outlet_location", location, postgresql_using="gist"),
        Index("idx_outlet_priority_status", priority, status),
    )
    
    @property
    def gps_lat(self) -> float:
        """Get latitude from PostGIS point."""
        if self.location is not None:
            point = to_shape(self.location)
            return point.y
        return None
    
    @property
    def gps_long(self) -> float:
        """Get longitude from PostGIS point."""
        if self.location is not None:
            point = to_shape(self.location)
            return point.x
        return None
    
    @classmethod
    def create_location(cls, latitude: float, longitude: float) -> str:
        """
        Create a PostGIS-compatible WKT point from lat/long.
        Note: PostGIS uses (longitude, latitude) order.
        """
        point = Point(longitude, latitude)
        return from_shape(point, srid=settings.SRID)
    
    def __repr__(self) -> str:
        return f"<Outlet(id={self.id}, code='{self.code}', name='{self.name}', priority={self.priority.name})>"
