# Pydantic Schemas
from app.schemas.outlet import (
    OutletCreate,
    OutletUpdate,
    OutletResponse,
    OutletListResponse,
    GPSCoordinates,
)
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
)
from app.schemas.box import (
    BoxCreate,
    BoxUpdate,
    BoxResponse,
    BoxListResponse,
    BoxSequenceUpdate,
)
from app.schemas.route import (
    RouteCreate,
    RouteUpdate,
    RouteResponse,
    RouteListResponse,
    DriverAssignment,
    VehicleAssignment,
)
from app.schemas.route_node import (
    RouteNodeCreate,
    RouteNodeUpdate,
    RouteNodeResponse,
    RouteNodeListResponse,
    ArrivalRecord,
    DepartureRecord,
    TelemetrySummary,
)

__all__ = [
    # Outlet
    "OutletCreate",
    "OutletUpdate", 
    "OutletResponse",
    "OutletListResponse",
    "GPSCoordinates",
    # Order
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderListResponse",
    # Box
    "BoxCreate",
    "BoxUpdate",
    "BoxResponse",
    "BoxListResponse",
    "BoxSequenceUpdate",
    # Route
    "RouteCreate",
    "RouteUpdate",
    "RouteResponse",
    "RouteListResponse",
    "DriverAssignment",
    "VehicleAssignment",
    # RouteNode
    "RouteNodeCreate",
    "RouteNodeUpdate",
    "RouteNodeResponse",
    "RouteNodeListResponse",
    "ArrivalRecord",
    "DepartureRecord",
    "TelemetrySummary",
]
