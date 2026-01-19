"""
Dashboard API endpoints for analytics and metrics.
"""
import logging
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    DashboardOverview, ChartsData, RecentActivitiesResponse,
    OverviewStats, DeliveryMetrics, RouteMetrics, BoxMetrics,
    OrderStatusDistribution, RouteStatusDistribution,
    OutletPriorityDistribution, VehicleTypeDistribution,
    DeliveryTrend, RouteEfficiency, RecentActivity
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ============================================================================
# Mock Data for Demo Mode (when database is unavailable)
# ============================================================================

def get_mock_overview_stats() -> OverviewStats:
    """Return mock statistics for demo."""
    return OverviewStats(
        total_outlets=156,
        active_outlets=142,
        total_orders=2847,
        pending_orders=89,
        orders_in_transit=45,
        delivered_orders=2680,
        total_routes=312,
        active_routes=8,
        completed_routes=298,
        total_boxes=4521
    )

def get_mock_delivery_metrics() -> DeliveryMetrics:
    """Return mock delivery metrics for demo."""
    return DeliveryMetrics(
        delivery_success_rate=94.2,
        avg_delivery_time_minutes=18.5,
        on_time_delivery_rate=91.8,
        orders_delivered_today=67,
        orders_pending_today=23
    )

def get_mock_route_metrics() -> RouteMetrics:
    """Return mock route metrics for demo."""
    return RouteMetrics(
        avg_stops_per_route=12.4,
        avg_route_completion=96.8,
        avg_distance_km=45.2,
        avg_fuel_efficiency=8.5,
        routes_completed_today=6,
        routes_in_progress=3
    )

def get_mock_box_metrics() -> BoxMetrics:
    """Return mock box metrics for demo."""
    return BoxMetrics(
        total_weight_kg=2847.5,
        avg_box_weight_kg=12.4,
        avg_fill_percentage=82.3,
        boxes_in_transit=127,
        fragile_boxes=45,
        refrigerated_boxes=23
    )

def get_mock_charts_data() -> ChartsData:
    """Return mock charts data for demo."""
    today = date.today()
    return ChartsData(
        order_status_distribution=[
            OrderStatusDistribution(status="delivered", count=2680, percentage=94.1),
            OrderStatusDistribution(status="in_transit", count=45, percentage=1.6),
            OrderStatusDistribution(status="pending", count=89, percentage=3.1),
            OrderStatusDistribution(status="cancelled", count=33, percentage=1.2),
        ],
        route_status_distribution=[
            RouteStatusDistribution(status="completed", count=298, percentage=95.5),
            RouteStatusDistribution(status="in_progress", count=8, percentage=2.6),
            RouteStatusDistribution(status="planned", count=6, percentage=1.9),
        ],
        outlet_priority_distribution=[
            OutletPriorityDistribution(priority="high", count=34, percentage=21.8),
            OutletPriorityDistribution(priority="medium", count=78, percentage=50.0),
            OutletPriorityDistribution(priority="low", count=44, percentage=28.2),
        ],
        vehicle_type_distribution=[
            VehicleTypeDistribution(vehicle_type="truck", count=156, total_capacity_kg=15600.0),
            VehicleTypeDistribution(vehicle_type="van", count=98, total_capacity_kg=4900.0),
            VehicleTypeDistribution(vehicle_type="motorcycle", count=58, total_capacity_kg=580.0),
        ],
        delivery_trends=[
            DeliveryTrend(date=str(today - timedelta(days=6)), delivered=85, pending=4, cancelled=0),
            DeliveryTrend(date=str(today - timedelta(days=5)), delivered=97, pending=5, cancelled=0),
            DeliveryTrend(date=str(today - timedelta(days=4)), delivered=91, pending=4, cancelled=0),
            DeliveryTrend(date=str(today - timedelta(days=3)), delivered=112, pending=6, cancelled=0),
            DeliveryTrend(date=str(today - timedelta(days=2)), delivered=103, pending=4, cancelled=0),
            DeliveryTrend(date=str(today - timedelta(days=1)), delivered=119, pending=5, cancelled=0),
            DeliveryTrend(date=str(today), delivered=64, pending=3, cancelled=0),
        ],
        top_routes=[
            RouteEfficiency(route_code="RT-001", planned_stops=15, completed_stops=15, completion_rate=100.0, distance_km=45.2),
            RouteEfficiency(route_code="RT-002", planned_stops=12, completed_stops=12, completion_rate=98.5, distance_km=38.7),
            RouteEfficiency(route_code="RT-003", planned_stops=18, completed_stops=17, completion_rate=97.2, distance_km=52.1),
            RouteEfficiency(route_code="RT-004", planned_stops=10, completed_stops=10, completion_rate=96.8, distance_km=28.4),
            RouteEfficiency(route_code="RT-005", planned_stops=14, completed_stops=13, completion_rate=95.5, distance_km=41.9),
        ]
    )

def get_mock_recent_activities(limit: int = 20) -> RecentActivitiesResponse:
    """Return mock recent activities for demo."""
    now = datetime.now()
    activities = [
        RecentActivity(id=1, type="order", action="completed", description="Order #2847 delivered to Downtown Store", timestamp=now - timedelta(minutes=5)),
        RecentActivity(id=2, type="route", action="started", description="Route RT-001 started with 15 stops", timestamp=now - timedelta(minutes=12)),
        RecentActivity(id=3, type="order", action="created", description="High priority order #2848 from Premium Outlet", timestamp=now - timedelta(minutes=18)),
        RecentActivity(id=4, type="order", action="completed", description="Order #2845 delivered to Central Market", timestamp=now - timedelta(minutes=25)),
        RecentActivity(id=5, type="outlet", action="updated", description="Outlet Downtown Store contact updated", timestamp=now - timedelta(minutes=32)),
        RecentActivity(id=6, type="route", action="completed", description="Route RT-002 completed all 12 stops", timestamp=now - timedelta(minutes=45)),
        RecentActivity(id=7, type="order", action="updated", description="Order #2843 marked as failed - customer unavailable", timestamp=now - timedelta(hours=1)),
        RecentActivity(id=8, type="order", action="updated", description="Order #2844 confirmed and ready for packing", timestamp=now - timedelta(hours=1, minutes=15)),
        RecentActivity(id=9, type="order", action="completed", description="Order #2842 delivered to Eastgate Plaza", timestamp=now - timedelta(hours=1, minutes=30)),
        RecentActivity(id=10, type="route", action="started", description="Route RT-003 started with 18 stops", timestamp=now - timedelta(hours=2)),
    ]
    return RecentActivitiesResponse(activities=activities[:limit], total=len(activities))


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """
    Get complete dashboard overview with all metrics.
    
    Returns:
        - Overview statistics (outlets, orders, routes, boxes)
        - Delivery performance metrics
        - Route performance metrics
        - Box/packing metrics
    """
    try:
        service = DashboardService(db)
        return await service.get_dashboard_overview()
    except Exception as e:
        logger.warning(f"Database unavailable, returning mock data: {e}")
        return DashboardOverview(
            stats=get_mock_overview_stats(),
            delivery_metrics=get_mock_delivery_metrics(),
            route_metrics=get_mock_route_metrics(),
            box_metrics=get_mock_box_metrics()
        )


@router.get("/stats", response_model=OverviewStats)
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    """Get high-level system statistics."""
    try:
        service = DashboardService(db)
        return await service.get_overview_stats()
    except Exception as e:
        logger.warning(f"Database unavailable, returning mock data: {e}")
        return get_mock_overview_stats()


@router.get("/delivery-metrics", response_model=DeliveryMetrics)
async def get_delivery_metrics(db: AsyncSession = Depends(get_db)):
    """Get delivery performance metrics."""
    try:
        service = DashboardService(db)
        return await service.get_delivery_metrics()
    except Exception as e:
        logger.warning(f"Database unavailable, returning mock data: {e}")
        return get_mock_delivery_metrics()


@router.get("/route-metrics", response_model=RouteMetrics)
async def get_route_metrics(db: AsyncSession = Depends(get_db)):
    """Get route performance metrics."""
    try:
        service = DashboardService(db)
        return await service.get_route_metrics()
    except Exception as e:
        logger.warning(f"Database unavailable, returning mock data: {e}")
        return get_mock_route_metrics()


@router.get("/box-metrics", response_model=BoxMetrics)
async def get_box_metrics(db: AsyncSession = Depends(get_db)):
    """Get box and packing metrics."""
    try:
        service = DashboardService(db)
        return await service.get_box_metrics()
    except Exception as e:
        logger.warning(f"Database unavailable, returning mock data: {e}")
        return get_mock_box_metrics()


@router.get("/charts", response_model=ChartsData)
async def get_charts_data(db: AsyncSession = Depends(get_db)):
    """
    Get all chart data for visualization.
    
    Returns:
        - Order status distribution
        - Route status distribution
        - Outlet priority distribution
        - Vehicle type distribution
        - Delivery trends (7 days)
        - Top performing routes
    """
    try:
        service = DashboardService(db)
        return await service.get_charts_data()
    except Exception as e:
        logger.warning(f"Database unavailable, returning mock data: {e}")
        return get_mock_charts_data()


@router.get("/recent-activities", response_model=RecentActivitiesResponse)
async def get_recent_activities(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get recent system activities."""
    try:
        service = DashboardService(db)
        return await service.get_recent_activities(limit=limit)
    except Exception as e:
        logger.warning(f"Database unavailable, returning mock data: {e}")
        return get_mock_recent_activities(limit=limit)
