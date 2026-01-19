"""
Pydantic schemas for Route validation and serialization.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class RouteStatusEnum(str, Enum):
    """Route status for API."""
    DRAFT = "draft"
    PLANNED = "planned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class VehicleTypeEnum(str, Enum):
    """Vehicle types for API."""
    MOTORCYCLE = "motorcycle"
    VAN = "van"
    TRUCK_SMALL = "truck_small"
    TRUCK_MEDIUM = "truck_medium"
    TRUCK_LARGE = "truck_large"
    REFRIGERATED = "refrigerated"


class DriverAssignment(BaseModel):
    """Driver assignment details."""
    driver_id: str = Field(..., max_length=50)
    driver_name: Optional[str] = Field(default=None, max_length=255)
    driver_phone: Optional[str] = Field(default=None, max_length=50)


class VehicleAssignment(BaseModel):
    """Vehicle assignment details."""
    vehicle_id: str = Field(..., max_length=50)
    vehicle_plate: Optional[str] = Field(default=None, max_length=20)
    vehicle_type: VehicleTypeEnum = Field(default=VehicleTypeEnum.VAN)
    max_weight_kg: Optional[Decimal] = Field(default=None, gt=0)
    max_volume_cm3: Optional[Decimal] = Field(default=None, gt=0)


class RouteBase(BaseModel):
    """Base schema for route fields."""
    route_code: str = Field(..., min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    planned_date: date
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    planned_distance_km: Optional[Decimal] = Field(default=None, ge=0)


class RouteCreate(RouteBase):
    """Schema for creating a new route."""
    driver: Optional[DriverAssignment] = None
    vehicle: Optional[VehicleAssignment] = None


class RouteUpdate(BaseModel):
    """Schema for updating a route."""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    status: Optional[RouteStatusEnum] = None
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    planned_distance_km: Optional[Decimal] = Field(default=None, ge=0)
    actual_distance_km: Optional[Decimal] = Field(default=None, ge=0)
    fuel_start_liters: Optional[Decimal] = Field(default=None, ge=0)
    fuel_end_liters: Optional[Decimal] = Field(default=None, ge=0)
    fuel_consumed_liters: Optional[Decimal] = Field(default=None, ge=0)


class RouteAssignmentUpdate(BaseModel):
    """Schema for assigning driver/vehicle to route."""
    driver: Optional[DriverAssignment] = None
    vehicle: Optional[VehicleAssignment] = None


class RouteResponse(BaseModel):
    """Schema for route API response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    route_code: str
    name: Optional[str]
    description: Optional[str]
    driver_id: Optional[str]
    driver_name: Optional[str]
    driver_phone: Optional[str]
    vehicle_id: Optional[str]
    vehicle_plate: Optional[str]
    vehicle_type: Optional[str]
    max_weight_kg: Optional[Decimal]
    max_volume_cm3: Optional[Decimal]
    planned_date: date
    planned_start_time: Optional[datetime]
    planned_end_time: Optional[datetime]
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    planned_distance_km: Optional[Decimal]
    actual_distance_km: Optional[Decimal]
    planned_stops: int
    completed_stops: int
    total_boxes: int
    total_weight_kg: Decimal
    fuel_start_liters: Optional[Decimal]
    fuel_end_liters: Optional[Decimal]
    fuel_consumed_liters: Optional[Decimal]
    status: str
    created_at: datetime
    updated_at: datetime
    
    @property
    def completion_percentage(self) -> float:
        if self.planned_stops == 0:
            return 0.0
        return (self.completed_stops / self.planned_stops) * 100
    
    @property
    def fuel_efficiency(self) -> Optional[float]:
        if self.fuel_consumed_liters and self.actual_distance_km:
            if self.fuel_consumed_liters > 0:
                return float(self.actual_distance_km / self.fuel_consumed_liters)
        return None


class RouteListResponse(BaseModel):
    """Paginated route list."""
    items: List[RouteResponse]
    total: int
    page: int
    page_size: int
    pages: int


class RouteMetrics(BaseModel):
    """Route performance metrics."""
    route_id: int
    total_distance_km: Decimal
    total_duration_minutes: int
    avg_service_time_minutes: float
    fuel_efficiency_km_per_liter: Optional[float]
    on_time_delivery_percentage: float
    completion_percentage: float
