"""
Dashboard service for computing analytics and metrics.
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, func, case, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outlet import Outlet, OutletStatus, OutletPriority
from app.models.order import Order, OrderStatus, OrderPriority
from app.models.route import Route, RouteStatus, VehicleType
from app.models.box import Box, BoxStatus
from app.models.route_node import RouteNode, NodeStatus, DeliveryResult
from app.schemas.dashboard import (
    OverviewStats, DeliveryMetrics, RouteMetrics, BoxMetrics,
    DashboardOverview, ChartsData, OrderStatusDistribution,
    RouteStatusDistribution, OutletPriorityDistribution,
    VehicleTypeDistribution, DeliveryTrend, RouteEfficiency,
    RecentActivity, RecentActivitiesResponse
)


class DashboardService:
    """Service for computing dashboard analytics."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_overview_stats(self) -> OverviewStats:
        """Get high-level system statistics."""
        # Outlet counts
        total_outlets = await self.db.scalar(select(func.count(Outlet.id)))
        active_outlets = await self.db.scalar(
            select(func.count(Outlet.id)).where(Outlet.status == OutletStatus.ACTIVE)
        )
        
        # Order counts
        total_orders = await self.db.scalar(select(func.count(Order.id)))
        pending_orders = await self.db.scalar(
            select(func.count(Order.id)).where(
                Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PACKING, OrderStatus.PACKED])
            )
        )
        orders_in_transit = await self.db.scalar(
            select(func.count(Order.id)).where(Order.status == OrderStatus.IN_TRANSIT)
        )
        delivered_orders = await self.db.scalar(
            select(func.count(Order.id)).where(Order.status == OrderStatus.DELIVERED)
        )
        
        # Route counts
        total_routes = await self.db.scalar(select(func.count(Route.id)))
        active_routes = await self.db.scalar(
            select(func.count(Route.id)).where(Route.status == RouteStatus.IN_PROGRESS)
        )
        completed_routes = await self.db.scalar(
            select(func.count(Route.id)).where(Route.status == RouteStatus.COMPLETED)
        )
        
        # Box counts
        total_boxes = await self.db.scalar(select(func.count(Box.id)))
        
        return OverviewStats(
            total_outlets=total_outlets or 0,
            active_outlets=active_outlets or 0,
            total_orders=total_orders or 0,
            pending_orders=pending_orders or 0,
            orders_in_transit=orders_in_transit or 0,
            delivered_orders=delivered_orders or 0,
            total_routes=total_routes or 0,
            active_routes=active_routes or 0,
            completed_routes=completed_routes or 0,
            total_boxes=total_boxes or 0
        )
    
    async def get_delivery_metrics(self) -> DeliveryMetrics:
        """Get delivery performance metrics."""
        today = date.today()
        
        # Total delivered vs total orders (excluding cancelled)
        total_completed = await self.db.scalar(
            select(func.count(Order.id)).where(
                Order.status.in_([OrderStatus.DELIVERED, OrderStatus.PARTIAL])
            )
        ) or 0
        
        total_non_cancelled = await self.db.scalar(
            select(func.count(Order.id)).where(
                Order.status != OrderStatus.CANCELLED
            )
        ) or 1  # Avoid division by zero
        
        delivery_success_rate = (total_completed / total_non_cancelled) * 100
        
        # Average delivery time from route nodes
        avg_service_time = await self.db.scalar(
            select(func.avg(RouteNode.service_time_minutes)).where(
                RouteNode.status == NodeStatus.COMPLETED
            )
        )
        
        # On-time delivery rate
        on_time_count = await self.db.scalar(
            select(func.count(Order.id)).where(
                and_(
                    Order.status == OrderStatus.DELIVERED,
                    Order.actual_delivery_date <= Order.requested_delivery_date
                )
            )
        ) or 0
        
        total_with_deadline = await self.db.scalar(
            select(func.count(Order.id)).where(
                and_(
                    Order.status == OrderStatus.DELIVERED,
                    Order.requested_delivery_date.isnot(None)
                )
            )
        ) or 1
        
        on_time_rate = (on_time_count / total_with_deadline) * 100
        
        # Today's orders
        orders_delivered_today = await self.db.scalar(
            select(func.count(Order.id)).where(
                and_(
                    Order.status == OrderStatus.DELIVERED,
                    Order.actual_delivery_date == today
                )
            )
        ) or 0
        
        orders_pending_today = await self.db.scalar(
            select(func.count(Order.id)).where(
                and_(
                    Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.IN_TRANSIT]),
                    Order.requested_delivery_date == today
                )
            )
        ) or 0
        
        return DeliveryMetrics(
            delivery_success_rate=round(delivery_success_rate, 2),
            avg_delivery_time_minutes=float(avg_service_time) if avg_service_time else None,
            on_time_delivery_rate=round(on_time_rate, 2),
            orders_delivered_today=orders_delivered_today,
            orders_pending_today=orders_pending_today
        )
    
    async def get_route_metrics(self) -> RouteMetrics:
        """Get route performance metrics."""
        today = date.today()
        
        # Average stops per route
        avg_stops = await self.db.scalar(
            select(func.avg(Route.planned_stops)).where(Route.planned_stops > 0)
        ) or 0
        
        # Average completion percentage
        completed_routes = await self.db.execute(
            select(Route.completed_stops, Route.planned_stops).where(
                and_(Route.planned_stops > 0, Route.status != RouteStatus.DRAFT)
            )
        )
        routes_data = completed_routes.all()
        
        if routes_data:
            total_completion = sum(
                (r[0] / r[1] * 100) for r in routes_data if r[1] > 0
            )
            avg_completion = total_completion / len(routes_data)
        else:
            avg_completion = 0
        
        # Average distance
        avg_distance = await self.db.scalar(
            select(func.avg(Route.actual_distance_km)).where(
                Route.actual_distance_km.isnot(None)
            )
        )
        
        # Average fuel efficiency
        fuel_data = await self.db.execute(
            select(Route.actual_distance_km, Route.fuel_consumed_liters).where(
                and_(
                    Route.actual_distance_km.isnot(None),
                    Route.fuel_consumed_liters.isnot(None),
                    Route.fuel_consumed_liters > 0
                )
            )
        )
        fuel_routes = fuel_data.all()
        
        if fuel_routes:
            total_efficiency = sum(
                float(r[0] / r[1]) for r in fuel_routes
            )
            avg_fuel_efficiency = total_efficiency / len(fuel_routes)
        else:
            avg_fuel_efficiency = None
        
        # Routes in progress
        routes_in_progress = await self.db.scalar(
            select(func.count(Route.id)).where(Route.status == RouteStatus.IN_PROGRESS)
        ) or 0
        
        # Routes completed today
        routes_completed_today = await self.db.scalar(
            select(func.count(Route.id)).where(
                and_(
                    Route.status == RouteStatus.COMPLETED,
                    Route.planned_date == today
                )
            )
        ) or 0
        
        return RouteMetrics(
            avg_stops_per_route=round(float(avg_stops), 2),
            avg_route_completion=round(avg_completion, 2),
            avg_distance_km=round(float(avg_distance), 2) if avg_distance else None,
            avg_fuel_efficiency=round(avg_fuel_efficiency, 2) if avg_fuel_efficiency else None,
            routes_in_progress=routes_in_progress,
            routes_completed_today=routes_completed_today
        )
    
    async def get_box_metrics(self) -> BoxMetrics:
        """Get box and packing metrics."""
        # Total weight in transit
        total_weight = await self.db.scalar(
            select(func.sum(Box.weight_kg)).where(
                Box.status.in_([BoxStatus.LOADED, BoxStatus.IN_TRANSIT])
            )
        ) or Decimal(0)
        
        # Average box weight
        avg_weight = await self.db.scalar(
            select(func.avg(Box.weight_kg)).where(Box.weight_kg > 0)
        ) or Decimal(0)
        
        # Average fill percentage (volume_used / volume)
        box_data = await self.db.execute(
            select(Box.volume_used_cm3, Box.length_cm, Box.width_cm, Box.height_cm).where(
                Box.volume_used_cm3 > 0
            )
        )
        boxes = box_data.all()
        
        if boxes:
            total_fill = sum(
                float(b[0] / (b[1] * b[2] * b[3]) * 100) for b in boxes
            )
            avg_fill = total_fill / len(boxes)
        else:
            avg_fill = 0
        
        # Boxes in transit
        boxes_in_transit = await self.db.scalar(
            select(func.count(Box.id)).where(
                Box.status.in_([BoxStatus.LOADED, BoxStatus.IN_TRANSIT])
            )
        ) or 0
        
        # Fragile boxes
        fragile_boxes = await self.db.scalar(
            select(func.count(Box.id)).where(Box.is_fragile == True)
        ) or 0
        
        # Refrigerated boxes
        refrigerated_boxes = await self.db.scalar(
            select(func.count(Box.id)).where(Box.requires_refrigeration == True)
        ) or 0
        
        return BoxMetrics(
            total_weight_kg=round(float(total_weight), 2),
            avg_box_weight_kg=round(float(avg_weight), 2),
            avg_fill_percentage=round(avg_fill, 2),
            boxes_in_transit=boxes_in_transit,
            fragile_boxes=fragile_boxes,
            refrigerated_boxes=refrigerated_boxes
        )
    
    async def get_dashboard_overview(self) -> DashboardOverview:
        """Get complete dashboard overview."""
        stats = await self.get_overview_stats()
        delivery_metrics = await self.get_delivery_metrics()
        route_metrics = await self.get_route_metrics()
        box_metrics = await self.get_box_metrics()
        
        return DashboardOverview(
            stats=stats,
            delivery_metrics=delivery_metrics,
            route_metrics=route_metrics,
            box_metrics=box_metrics,
            generated_at=datetime.utcnow()
        )
    
    async def get_order_status_distribution(self) -> list[OrderStatusDistribution]:
        """Get order distribution by status."""
        result = await self.db.execute(
            select(Order.status, func.count(Order.id)).group_by(Order.status)
        )
        data = result.all()
        
        total = sum(d[1] for d in data) or 1
        
        return [
            OrderStatusDistribution(
                status=d[0].value,
                count=d[1],
                percentage=round((d[1] / total) * 100, 2)
            )
            for d in data
        ]
    
    async def get_route_status_distribution(self) -> list[RouteStatusDistribution]:
        """Get route distribution by status."""
        result = await self.db.execute(
            select(Route.status, func.count(Route.id)).group_by(Route.status)
        )
        data = result.all()
        
        total = sum(d[1] for d in data) or 1
        
        return [
            RouteStatusDistribution(
                status=d[0].value,
                count=d[1],
                percentage=round((d[1] / total) * 100, 2)
            )
            for d in data
        ]
    
    async def get_outlet_priority_distribution(self) -> list[OutletPriorityDistribution]:
        """Get outlet distribution by priority."""
        result = await self.db.execute(
            select(Outlet.priority, func.count(Outlet.id)).group_by(Outlet.priority)
        )
        data = result.all()
        
        total = sum(d[1] for d in data) or 1
        
        return [
            OutletPriorityDistribution(
                priority=d[0].name,
                count=d[1],
                percentage=round((d[1] / total) * 100, 2)
            )
            for d in data
        ]
    
    async def get_vehicle_type_distribution(self) -> list[VehicleTypeDistribution]:
        """Get routes distribution by vehicle type."""
        result = await self.db.execute(
            select(
                Route.vehicle_type,
                func.count(Route.id),
                func.sum(Route.max_weight_kg)
            ).where(
                Route.vehicle_type.isnot(None)
            ).group_by(Route.vehicle_type)
        )
        data = result.all()
        
        return [
            VehicleTypeDistribution(
                vehicle_type=d[0].value if d[0] else "unknown",
                count=d[1],
                total_capacity_kg=float(d[2] or 0)
            )
            for d in data
        ]
    
    async def get_delivery_trends(self, days: int = 7) -> list[DeliveryTrend]:
        """Get delivery trends for the past N days."""
        trends = []
        today = date.today()
        
        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            
            delivered = await self.db.scalar(
                select(func.count(Order.id)).where(
                    and_(
                        Order.status == OrderStatus.DELIVERED,
                        Order.actual_delivery_date == day
                    )
                )
            ) or 0
            
            pending = await self.db.scalar(
                select(func.count(Order.id)).where(
                    and_(
                        Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.IN_TRANSIT]),
                        Order.requested_delivery_date == day
                    )
                )
            ) or 0
            
            cancelled = await self.db.scalar(
                select(func.count(Order.id)).where(
                    and_(
                        Order.status == OrderStatus.CANCELLED,
                        func.date(Order.updated_at) == day
                    )
                )
            ) or 0
            
            trends.append(DeliveryTrend(
                date=day.isoformat(),
                delivered=delivered,
                pending=pending,
                cancelled=cancelled
            ))
        
        return trends
    
    async def get_top_routes(self, limit: int = 10) -> list[RouteEfficiency]:
        """Get top performing routes."""
        result = await self.db.execute(
            select(Route).where(
                Route.status.in_([RouteStatus.COMPLETED, RouteStatus.IN_PROGRESS])
            ).order_by(Route.planned_date.desc()).limit(limit)
        )
        routes = result.scalars().all()
        
        return [
            RouteEfficiency(
                route_code=r.route_code,
                planned_stops=r.planned_stops,
                completed_stops=r.completed_stops,
                completion_rate=round(r.completion_percentage, 2),
                distance_km=float(r.actual_distance_km) if r.actual_distance_km else None
            )
            for r in routes
        ]
    
    async def get_charts_data(self) -> ChartsData:
        """Get all chart data for visualization."""
        order_dist = await self.get_order_status_distribution()
        route_dist = await self.get_route_status_distribution()
        outlet_dist = await self.get_outlet_priority_distribution()
        vehicle_dist = await self.get_vehicle_type_distribution()
        trends = await self.get_delivery_trends()
        top_routes = await self.get_top_routes()
        
        return ChartsData(
            order_status_distribution=order_dist,
            route_status_distribution=route_dist,
            outlet_priority_distribution=outlet_dist,
            vehicle_type_distribution=vehicle_dist,
            delivery_trends=trends,
            top_routes=top_routes,
            generated_at=datetime.utcnow()
        )
    
    async def get_recent_activities(self, limit: int = 20) -> RecentActivitiesResponse:
        """Get recent system activities."""
        activities = []
        
        # Recent orders
        recent_orders = await self.db.execute(
            select(Order).order_by(Order.updated_at.desc()).limit(limit // 3)
        )
        for order in recent_orders.scalars().all():
            action = "created" if order.created_at == order.updated_at else "updated"
            if order.status == OrderStatus.DELIVERED:
                action = "delivered"
            activities.append(RecentActivity(
                id=order.id,
                type="order",
                action=action,
                description=f"Order {order.order_number} {action}",
                timestamp=order.updated_at
            ))
        
        # Recent routes
        recent_routes = await self.db.execute(
            select(Route).order_by(Route.updated_at.desc()).limit(limit // 3)
        )
        for route in recent_routes.scalars().all():
            action = "created" if route.created_at == route.updated_at else "updated"
            if route.status == RouteStatus.COMPLETED:
                action = "completed"
            elif route.status == RouteStatus.IN_PROGRESS:
                action = "started"
            activities.append(RecentActivity(
                id=route.id,
                type="route",
                action=action,
                description=f"Route {route.route_code} {action}",
                timestamp=route.updated_at
            ))
        
        # Recent outlets
        recent_outlets = await self.db.execute(
            select(Outlet).order_by(Outlet.updated_at.desc()).limit(limit // 3)
        )
        for outlet in recent_outlets.scalars().all():
            action = "created" if outlet.created_at == outlet.updated_at else "updated"
            activities.append(RecentActivity(
                id=outlet.id,
                type="outlet",
                action=action,
                description=f"Outlet {outlet.name} {action}",
                timestamp=outlet.updated_at
            ))
        
        # Sort by timestamp
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        activities = activities[:limit]
        
        return RecentActivitiesResponse(
            activities=activities,
            total=len(activities)
        )
