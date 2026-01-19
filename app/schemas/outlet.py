"""
Pydantic schemas for Outlet validation and serialization.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class OutletPriorityEnum(str, Enum):
    """Priority levels for API representation."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"


class OutletStatusEnum(str, Enum):
    """Outlet status for API representation."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class GPSCoordinates(BaseModel):
    """GPS coordinate validation schema."""
    latitude: float = Field(
        ..., 
        ge=-90.0, 
        le=90.0, 
        description="Latitude in decimal degrees (-90 to 90)"
    )
    longitude: float = Field(
        ..., 
        ge=-180.0, 
        le=180.0, 
        description="Longitude in decimal degrees (-180 to 180)"
    )
    
    @field_validator("latitude", "longitude")
    @classmethod
    def validate_precision(cls, v: float) -> float:
        """Ensure reasonable precision (6 decimal places ≈ 0.1m accuracy)."""
        return round(v, 6)


class DeliveryWindow(BaseModel):
    """Delivery time window specification."""
    start_minutes: int = Field(
        default=480,  # 8:00 AM
        ge=0,
        le=1440,
        description="Start time in minutes from midnight"
    )
    end_minutes: int = Field(
        default=1080,  # 6:00 PM
        ge=0,
        le=1440,
        description="End time in minutes from midnight"
    )
    
    @field_validator("end_minutes")
    @classmethod
    def validate_window(cls, v: int, info) -> int:
        """Ensure end time is after start time."""
        start = info.data.get("start_minutes", 0)
        if v <= start:
            raise ValueError("Delivery window end must be after start")
        return v
    
    @property
    def start_time(self) -> str:
        """Format start time as HH:MM."""
        hours, minutes = divmod(self.start_minutes, 60)
        return f"{hours:02d}:{minutes:02d}"
    
    @property
    def end_time(self) -> str:
        """Format end time as HH:MM."""
        hours, minutes = divmod(self.end_minutes, 60)
        return f"{hours:02d}:{minutes:02d}"


class OutletBase(BaseModel):
    """Base schema with common outlet fields."""
    code: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Unique outlet identifier code"
    )
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Outlet name"
    )
    address: Optional[str] = Field(
        default=None, 
        description="Full address"
    )
    contact_name: Optional[str] = Field(
        default=None, 
        max_length=255,
        description="Primary contact person"
    )
    contact_phone: Optional[str] = Field(
        default=None, 
        max_length=50,
        description="Contact phone number"
    )
    gps_coordinates: GPSCoordinates = Field(
        ..., 
        description="GPS location of the outlet"
    )
    priority: OutletPriorityEnum = Field(
        default=OutletPriorityEnum.MEDIUM,
        description="Delivery priority level"
    )
    avg_service_time: int = Field(
        default=15,
        ge=1,
        le=180,
        description="Average service time in minutes"
    )


class OutletCreate(OutletBase):
    """Schema for creating a new outlet."""
    delivery_window: Optional[DeliveryWindow] = Field(
        default_factory=DeliveryWindow,
        description="Delivery time window"
    )


class OutletUpdate(BaseModel):
    """Schema for updating an outlet (all fields optional)."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    address: Optional[str] = None
    contact_name: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    gps_coordinates: Optional[GPSCoordinates] = None
    priority: Optional[OutletPriorityEnum] = None
    status: Optional[OutletStatusEnum] = None
    avg_service_time: Optional[int] = Field(default=None, ge=1, le=180)
    delivery_window: Optional[DeliveryWindow] = None


class OutletResponse(BaseModel):
    """Schema for outlet API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    code: str
    name: str
    address: Optional[str]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    gps_lat: float
    gps_long: float
    priority: str
    status: str
    delivery_window_start: int
    delivery_window_end: int
    avg_service_time: int
    created_at: datetime
    updated_at: datetime
    
    @property
    def delivery_window_formatted(self) -> dict:
        """Return formatted delivery window."""
        start_h, start_m = divmod(self.delivery_window_start, 60)
        end_h, end_m = divmod(self.delivery_window_end, 60)
        return {
            "start": f"{start_h:02d}:{start_m:02d}",
            "end": f"{end_h:02d}:{end_m:02d}"
        }


class OutletListResponse(BaseModel):
    """Paginated list of outlets."""
    items: List[OutletResponse]
    total: int
    page: int
    page_size: int
    pages: int


class OutletNearbyQuery(BaseModel):
    """Query schema for finding nearby outlets."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    radius_km: float = Field(
        default=10.0,
        gt=0,
        le=100,
        description="Search radius in kilometers"
    )
    limit: int = Field(default=10, ge=1, le=100)
    priority: Optional[OutletPriorityEnum] = None
