"""
Dashboard schemas for analytics and metrics.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# Summary Statistics
# ============================================================================

class OverviewStats(BaseModel):
    """High-level system statistics."""
    total_outlets: int = Field(..., description="Total number of outlets")
    active_outlets: int = Field(..., description="Number of active outlets")
    total_orders: int = Field(..., description="Total orders in system")
    pending_orders: int = Field(..., description="Orders pending delivery")
    orders_in_transit: int = Field(..., description="Orders currently in transit")
    delivered_orders: int = Field(..., description="Successfully delivered orders")
    total_routes: int = Field(..., description="Total routes created")
    active_routes: int = Field(..., description="Routes currently in progress")
    completed_routes: int = Field(..., description="Completed routes")
    total_boxes: int = Field(..., description="Total boxes in system")


class DeliveryMetrics(BaseModel):
    """Delivery performance metrics."""
    delivery_success_rate: float = Field(..., description="Percentage of successful deliveries")
    avg_delivery_time_minutes: Optional[float] = Field(None, description="Average delivery time")
    on_time_delivery_rate: float = Field(..., description="Percentage of on-time deliveries")
    orders_delivered_today: int = Field(..., description="Orders delivered today")
    orders_pending_today: int = Field(..., description="Orders pending for today")


class RouteMetrics(BaseModel):
    """Route performance metrics."""
    avg_stops_per_route: float = Field(..., description="Average stops per route")
    avg_route_completion: float = Field(..., description="Average route completion percentage")
    avg_distance_km: Optional[float] = Field(None, description="Average route distance")
    avg_fuel_efficiency: Optional[float] = Field(None, description="Average fuel efficiency km/L")
    routes_in_progress: int = Field(..., description="Routes currently active")
    routes_completed_today: int = Field(..., description="Routes completed today")


class BoxMetrics(BaseModel):
    """Box and packing metrics."""
    total_weight_kg: float = Field(..., description="Total weight in transit")
    avg_box_weight_kg: float = Field(..., description="Average box weight")
    avg_fill_percentage: float = Field(..., description="Average box fill percentage")
    boxes_in_transit: int = Field(..., description="Boxes currently in transit")
    fragile_boxes: int = Field(..., description="Fragile boxes count")
    refrigerated_boxes: int = Field(..., description="Refrigerated boxes count")


# ============================================================================
# Charts Data
# ============================================================================

class TimeSeriesDataPoint(BaseModel):
    """Single data point for time series charts."""
    label: str = Field(..., description="Time label (date/hour)")
    value: float = Field(..., description="Metric value")


class OrderStatusDistribution(BaseModel):
    """Order distribution by status."""
    status: str
    count: int
    percentage: float


class RouteStatusDistribution(BaseModel):
    """Route distribution by status."""
    status: str
    count: int
    percentage: float


class OutletPriorityDistribution(BaseModel):
    """Outlet distribution by priority."""
    priority: str
    count: int
    percentage: float


class VehicleTypeDistribution(BaseModel):
    """Routes distribution by vehicle type."""
    vehicle_type: str
    count: int
    total_capacity_kg: float


class DeliveryTrend(BaseModel):
    """Daily delivery trend data."""
    date: str
    delivered: int
    pending: int
    cancelled: int


class RouteEfficiency(BaseModel):
    """Route efficiency data point."""
    route_code: str
    planned_stops: int
    completed_stops: int
    completion_rate: float
    distance_km: Optional[float]


# ============================================================================
# Dashboard Response Models
# ============================================================================

class DashboardOverview(BaseModel):
    """Complete dashboard overview response."""
    stats: OverviewStats
    delivery_metrics: DeliveryMetrics
    route_metrics: RouteMetrics
    box_metrics: BoxMetrics
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ChartsData(BaseModel):
    """Charts data for visualization."""
    order_status_distribution: list[OrderStatusDistribution]
    route_status_distribution: list[RouteStatusDistribution]
    outlet_priority_distribution: list[OutletPriorityDistribution]
    vehicle_type_distribution: list[VehicleTypeDistribution]
    delivery_trends: list[DeliveryTrend]
    top_routes: list[RouteEfficiency]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class RecentActivity(BaseModel):
    """Recent system activity item."""
    id: int
    type: str  # order, route, outlet
    action: str  # created, updated, completed
    description: str
    timestamp: datetime


class RecentActivitiesResponse(BaseModel):
    """Recent activities response."""
    activities: list[RecentActivity]
    total: int
