"""
Pydantic schemas for RouteNode (telemetry) validation and serialization.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

from app.schemas.outlet import GPSCoordinates


class NodeStatusEnum(str, Enum):
    """Node status for API."""
    PENDING = "pending"
    EN_ROUTE = "en_route"
    ARRIVED = "arrived"
    SERVICING = "servicing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DeliveryResultEnum(str, Enum):
    """Delivery outcome for API."""
    SUCCESS = "success"
    PARTIAL = "partial"
    RECIPIENT_ABSENT = "recipient_absent"
    REFUSED = "refused"
    WRONG_ADDRESS = "wrong_address"
    ACCESS_DENIED = "access_denied"
    OTHER_FAILURE = "other_failure"


class RouteNodeBase(BaseModel):
    """Base schema for route node fields."""
    route_id: int = Field(..., gt=0)
    outlet_id: int = Field(..., gt=0)
    sequence_order: int = Field(..., ge=1)
    planned_arrival_time: Optional[datetime] = None


class RouteNodeCreate(RouteNodeBase):
    """Schema for creating a route node."""
    planned_location: Optional[GPSCoordinates] = None


class RouteNodeUpdate(BaseModel):
    """Schema for updating a route node."""
    sequence_order: Optional[int] = Field(default=None, ge=1)
    planned_arrival_time: Optional[datetime] = None
    status: Optional[NodeStatusEnum] = None
    delivery_result: Optional[DeliveryResultEnum] = None
    boxes_delivered: Optional[int] = Field(default=None, ge=0)
    boxes_returned: Optional[int] = Field(default=None, ge=0)
    driver_notes: Optional[str] = None
    recipient_name: Optional[str] = Field(default=None, max_length=255)
    signature_captured: Optional[bool] = None
    photo_captured: Optional[bool] = None


class ArrivalRecord(BaseModel):
    """Schema for recording driver arrival."""
    coordinates: GPSCoordinates
    timestamp: Optional[datetime] = None
    odometer_km: Optional[Decimal] = Field(default=None, ge=0)


class DepartureRecord(BaseModel):
    """Schema for recording driver departure."""
    coordinates: GPSCoordinates
    timestamp: Optional[datetime] = None
    odometer_km: Optional[Decimal] = Field(default=None, ge=0)
    boxes_delivered: int = Field(default=0, ge=0)
    boxes_returned: int = Field(default=0, ge=0)
    delivery_result: DeliveryResultEnum
    recipient_name: Optional[str] = Field(default=None, max_length=255)
    signature_captured: bool = Field(default=False)
    photo_captured: bool = Field(default=False)
    driver_notes: Optional[str] = None


class FuelRecord(BaseModel):
    """Schema for fuel consumption at a node."""
    fuel_consumed_liters: Decimal = Field(..., ge=0)
    distance_from_previous_km: Optional[Decimal] = Field(default=None, ge=0)


class RouteNodeResponse(BaseModel):
    """Schema for route node API response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    route_id: int
    outlet_id: int
    sequence_order: int
    planned_arrival_time: Optional[datetime]
    arrival_time: Optional[datetime]
    departure_time: Optional[datetime]
    service_time_minutes: Optional[int]
    arrival_lat: Optional[float]
    arrival_long: Optional[float]
    distance_from_previous_km: Optional[Decimal]
    cumulative_distance_km: Optional[Decimal]
    fuel_consumed_liters: Optional[Decimal]
    odometer_arrival_km: Optional[Decimal]
    odometer_departure_km: Optional[Decimal]
    boxes_delivered: int
    boxes_returned: int
    status: str
    delivery_result: Optional[str]
    driver_notes: Optional[str]
    recipient_name: Optional[str]
    signature_captured: bool
    photo_captured: bool
    is_within_geofence: Optional[bool]
    geofence_distance_meters: Optional[Decimal]
    created_at: datetime
    updated_at: datetime


class RouteNodeListResponse(BaseModel):
    """List of route nodes."""
    items: List[RouteNodeResponse]
    total: int


class TelemetrySummary(BaseModel):
    """Summary of route telemetry."""
    route_id: int
    total_stops: int
    completed_stops: int
    failed_stops: int
    skipped_stops: int
    total_service_time_minutes: int
    avg_service_time_minutes: float
    total_distance_km: Decimal
    total_fuel_liters: Decimal
    fuel_efficiency_km_per_liter: Optional[float]
    on_time_count: int
    late_count: int
    on_time_percentage: float


class ServiceTimeAnalysis(BaseModel):
    """Service time analytics for an outlet or route."""
    outlet_id: Optional[int] = None
    route_id: Optional[int] = None
    min_service_time_minutes: int
    max_service_time_minutes: int
    avg_service_time_minutes: float
    median_service_time_minutes: float
    std_dev_minutes: float
    sample_count: int


class GPSTrackPoint(BaseModel):
    """Single GPS track point for route visualization."""
    timestamp: datetime
    latitude: float
    longitude: float
    node_id: Optional[int] = None
    event_type: str  # "arrival", "departure", "tracking"
