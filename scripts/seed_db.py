"""
Database seed script - Add sample data for development.
Run after tables are created by SQLAlchemy.
"""
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker, engine, Base
from app.models.outlet import Outlet, OutletPriority, OutletStatus
from app.models.order import Order, OrderStatus, OrderPriority
from app.models.route import Route, RouteStatus, VehicleType
from app.models.box import Box, BoxStatus
from app.models.route_node import RouteNode, NodeStatus


async def seed_outlets(db: AsyncSession):
    """Create sample outlets."""
    outlets = [
        Outlet(
            code="OUT-001",
            name="Downtown Supermarket",
            address="123 Main Street, Nairobi CBD",
            contact_name="John Kimani",
            contact_phone="+254 712 345 678",
            location=Outlet.create_location(-1.2921, 36.8219),
            priority=OutletPriority.HIGH,
            status=OutletStatus.ACTIVE,
            delivery_window_start=480,  # 8:00 AM
            delivery_window_end=1080,   # 6:00 PM
        ),
        Outlet(
            code="OUT-002",
            name="Westlands Mall",
            address="456 Westlands Road",
            contact_name="Mary Wanjiku",
            contact_phone="+254 723 456 789",
            location=Outlet.create_location(-1.2673, 36.8028),
            priority=OutletPriority.CRITICAL,
            status=OutletStatus.ACTIVE,
            delivery_window_start=540,  # 9:00 AM
            delivery_window_end=1260,   # 9:00 PM
        ),
        Outlet(
            code="OUT-003",
            name="Karen Shopping Center",
            address="789 Karen Road",
            contact_name="Peter Ochieng",
            contact_phone="+254 734 567 890",
            location=Outlet.create_location(-1.3187, 36.7123),
            priority=OutletPriority.MEDIUM,
            status=OutletStatus.ACTIVE,
            delivery_window_start=510,  # 8:30 AM
            delivery_window_end=1050,   # 5:30 PM
        ),
        Outlet(
            code="OUT-004",
            name="Eastleigh Market",
            address="321 1st Avenue",
            contact_name="Fatima Hassan",
            contact_phone="+254 745 678 901",
            location=Outlet.create_location(-1.2744, 36.8572),
            priority=OutletPriority.HIGH,
            status=OutletStatus.ACTIVE,
            delivery_window_start=360,  # 6:00 AM
            delivery_window_end=1140,   # 7:00 PM
        ),
        Outlet(
            code="OUT-005",
            name="Kilimani Grocers",
            address="654 Argwings Kodhek",
            contact_name="David Mwangi",
            contact_phone="+254 756 789 012",
            location=Outlet.create_location(-1.2890, 36.7876),
            priority=OutletPriority.MEDIUM,
            status=OutletStatus.ACTIVE,
            delivery_window_start=420,  # 7:00 AM
            delivery_window_end=1200,   # 8:00 PM
        ),
        Outlet(
            code="OUT-006",
            name="Lavington Fresh",
            address="987 James Gichuru Road",
            contact_name="Grace Njeri",
            contact_phone="+254 767 890 123",
            location=Outlet.create_location(-1.2756, 36.7654),
            priority=OutletPriority.LOW,
            status=OutletStatus.ACTIVE,
            delivery_window_start=480,  # 8:00 AM
            delivery_window_end=1080,   # 6:00 PM
        ),
        Outlet(
            code="OUT-007",
            name="Industrial Area Depot",
            address="147 Enterprise Road",
            contact_name="James Kamau",
            contact_phone="+254 778 901 234",
            location=Outlet.create_location(-1.3089, 36.8512),
            priority=OutletPriority.CRITICAL,
            status=OutletStatus.ACTIVE,
            delivery_window_start=360,  # 6:00 AM
            delivery_window_end=1320,   # 10:00 PM
        ),
        Outlet(
            code="OUT-008",
            name="South B Mart",
            address="258 Mombasa Road",
            contact_name="Lucy Akinyi",
            contact_phone="+254 789 012 345",
            location=Outlet.create_location(-1.3156, 36.8345),
            priority=OutletPriority.MEDIUM,
            status=OutletStatus.ACTIVE,
            delivery_window_start=450,  # 7:30 AM
            delivery_window_end=1170,   # 7:30 PM
        ),
    ]
    
    for outlet in outlets:
        db.add(outlet)
    
    await db.commit()
    print(f"✅ Created {len(outlets)} outlets")
    return outlets


async def seed_orders(db: AsyncSession, outlets: list[Outlet]):
    """Create sample orders."""
    today = date.today()
    orders = [
        Order(
            order_number="ORD-2026-001",
            outlet_id=outlets[0].id,
            status=OrderStatus.DELIVERED,
            priority=OrderPriority.NORMAL,
            total_weight_kg=Decimal("45.5"),
            item_count=15,
            order_date=today - timedelta(days=2),
            actual_delivery_date=today - timedelta(days=2),
        ),
        Order(
            order_number="ORD-2026-002",
            outlet_id=outlets[1].id,
            status=OrderStatus.DELIVERED,
            priority=OrderPriority.HIGH,
            total_weight_kg=Decimal("68.0"),
            item_count=22,
            order_date=today - timedelta(days=1),
            actual_delivery_date=today - timedelta(days=1),
        ),
        Order(
            order_number="ORD-2026-003",
            outlet_id=outlets[2].id,
            status=OrderStatus.IN_TRANSIT,
            priority=OrderPriority.NORMAL,
            total_weight_kg=Decimal("52.3"),
            item_count=18,
            order_date=today,
            requested_delivery_date=today,
        ),
        Order(
            order_number="ORD-2026-004",
            outlet_id=outlets[3].id,
            status=OrderStatus.PACKED,
            priority=OrderPriority.URGENT,
            total_weight_kg=Decimal("95.0"),
            item_count=30,
            order_date=today,
            requested_delivery_date=today,
        ),
        Order(
            order_number="ORD-2026-005",
            outlet_id=outlets[4].id,
            status=OrderStatus.PENDING,
            priority=OrderPriority.NORMAL,
            total_weight_kg=Decimal("35.7"),
            item_count=12,
            order_date=today,
            requested_delivery_date=today + timedelta(days=1),
        ),
        Order(
            order_number="ORD-2026-006",
            outlet_id=outlets[5].id,
            status=OrderStatus.CONFIRMED,
            priority=OrderPriority.LOW,
            total_weight_kg=Decimal("24.2"),
            item_count=8,
            order_date=today,
            requested_delivery_date=today + timedelta(days=1),
        ),
        Order(
            order_number="ORD-2026-007",
            outlet_id=outlets[6].id,
            status=OrderStatus.PACKING,
            priority=OrderPriority.URGENT,
            total_weight_kg=Decimal("142.0"),
            item_count=45,
            order_date=today,
            requested_delivery_date=today,
        ),
        Order(
            order_number="ORD-2026-008",
            outlet_id=outlets[0].id,
            status=OrderStatus.PENDING,
            priority=OrderPriority.NORMAL,
            total_weight_kg=Decimal("58.5"),
            item_count=20,
            order_date=today,
            requested_delivery_date=today + timedelta(days=2),
        ),
    ]
    
    for order in orders:
        db.add(order)
    
    await db.commit()
    print(f"✅ Created {len(orders)} orders")
    return orders


async def seed_routes(db: AsyncSession):
    """Create sample routes."""
    today = date.today()
    now = datetime.utcnow()
    
    routes = [
        Route(
            route_code="RT-2026-001",
            name="CBD Morning Run",
            status=RouteStatus.COMPLETED,
            vehicle_type=VehicleType.VAN,
            driver_name="John Kamau",
            driver_phone="+254 700 111 111",
            planned_date=today - timedelta(days=1),
            actual_start_time=now - timedelta(days=1, hours=8),
            actual_end_time=now - timedelta(days=1, hours=5),
            planned_distance_km=Decimal("45.2"),
            planned_stops=6,
            completed_stops=6,
        ),
        Route(
            route_code="RT-2026-002",
            name="Westlands Express",
            status=RouteStatus.IN_PROGRESS,
            vehicle_type=VehicleType.TRUCK_SMALL,
            driver_name="Peter Ochieng",
            driver_phone="+254 700 222 222",
            planned_date=today,
            actual_start_time=now - timedelta(hours=2),
            planned_distance_km=Decimal("32.8"),
            planned_stops=5,
            completed_stops=2,
        ),
        Route(
            route_code="RT-2026-003",
            name="South Route",
            status=RouteStatus.PLANNED,
            vehicle_type=VehicleType.VAN,
            driver_name="Mary Wanjiku",
            driver_phone="+254 700 333 333",
            planned_date=today,
            planned_distance_km=Decimal("28.5"),
            planned_stops=4,
            completed_stops=0,
        ),
        Route(
            route_code="RT-2026-004",
            name="Industrial Delivery",
            status=RouteStatus.ASSIGNED,
            vehicle_type=VehicleType.TRUCK_MEDIUM,
            driver_name="James Mwangi",
            driver_phone="+254 700 444 444",
            planned_date=today,
            planned_distance_km=Decimal("55.0"),
            planned_stops=8,
            completed_stops=0,
        ),
    ]
    
    for route in routes:
        db.add(route)
    
    await db.commit()
    print(f"✅ Created {len(routes)} routes")
    return routes


async def seed_boxes(db: AsyncSession, orders: list[Order], routes: list[Route]):
    """Create sample boxes."""
    boxes = [
        Box(barcode="BOX-001", order_id=orders[0].id, route_id=routes[0].id, weight_kg=Decimal("15.2"), max_weight_kg=Decimal("50.0"), status=BoxStatus.DELIVERED),
        Box(barcode="BOX-002", order_id=orders[0].id, route_id=routes[0].id, weight_kg=Decimal("18.3"), max_weight_kg=Decimal("50.0"), is_fragile=True, status=BoxStatus.DELIVERED),
        Box(barcode="BOX-003", order_id=orders[0].id, route_id=routes[0].id, weight_kg=Decimal("12.0"), max_weight_kg=Decimal("50.0"), requires_refrigeration=True, status=BoxStatus.DELIVERED),
        Box(barcode="BOX-004", order_id=orders[1].id, route_id=routes[0].id, weight_kg=Decimal("22.5"), max_weight_kg=Decimal("50.0"), status=BoxStatus.DELIVERED),
        Box(barcode="BOX-005", order_id=orders[1].id, route_id=routes[0].id, weight_kg=Decimal("25.0"), max_weight_kg=Decimal("50.0"), requires_refrigeration=True, status=BoxStatus.DELIVERED),
        Box(barcode="BOX-006", order_id=orders[1].id, route_id=routes[0].id, weight_kg=Decimal("20.5"), max_weight_kg=Decimal("50.0"), is_fragile=True, status=BoxStatus.DELIVERED),
        Box(barcode="BOX-007", order_id=orders[2].id, route_id=routes[1].id, weight_kg=Decimal("17.8"), max_weight_kg=Decimal("50.0"), status=BoxStatus.IN_TRANSIT),
        Box(barcode="BOX-008", order_id=orders[2].id, route_id=routes[1].id, weight_kg=Decimal("18.5"), max_weight_kg=Decimal("50.0"), requires_refrigeration=True, status=BoxStatus.IN_TRANSIT),
        Box(barcode="BOX-009", order_id=orders[2].id, route_id=routes[1].id, weight_kg=Decimal("16.0"), max_weight_kg=Decimal("50.0"), status=BoxStatus.IN_TRANSIT),
        Box(barcode="BOX-010", order_id=orders[3].id, weight_kg=Decimal("30.0"), max_weight_kg=Decimal("50.0"), is_fragile=True, status=BoxStatus.SEALED),
        Box(barcode="BOX-011", order_id=orders[3].id, weight_kg=Decimal("32.5"), max_weight_kg=Decimal("50.0"), requires_refrigeration=True, status=BoxStatus.SEALED),
        Box(barcode="BOX-012", order_id=orders[3].id, weight_kg=Decimal("32.5"), max_weight_kg=Decimal("50.0"), status=BoxStatus.SEALED),
    ]
    
    for box in boxes:
        db.add(box)
    
    await db.commit()
    print(f"✅ Created {len(boxes)} boxes")
    return boxes


async def seed_route_nodes(db: AsyncSession, routes: list[Route], outlets: list[Outlet]):
    """Create sample route nodes (stops)."""
    nodes = [
        RouteNode(route_id=routes[0].id, outlet_id=outlets[0].id, sequence_order=1, status=NodeStatus.COMPLETED),
        RouteNode(route_id=routes[0].id, outlet_id=outlets[3].id, sequence_order=2, status=NodeStatus.COMPLETED),
        RouteNode(route_id=routes[0].id, outlet_id=outlets[4].id, sequence_order=3, status=NodeStatus.COMPLETED),
        RouteNode(route_id=routes[1].id, outlet_id=outlets[1].id, sequence_order=1, status=NodeStatus.COMPLETED),
        RouteNode(route_id=routes[1].id, outlet_id=outlets[5].id, sequence_order=2, status=NodeStatus.SERVICING),
        RouteNode(route_id=routes[1].id, outlet_id=outlets[2].id, sequence_order=3, status=NodeStatus.PENDING),
        RouteNode(route_id=routes[2].id, outlet_id=outlets[7].id, sequence_order=1, status=NodeStatus.PENDING),
        RouteNode(route_id=routes[2].id, outlet_id=outlets[6].id, sequence_order=2, status=NodeStatus.PENDING),
    ]
    
    for node in nodes:
        db.add(node)
    
    await db.commit()
    print(f"✅ Created {len(nodes)} route nodes")


async def seed_database():
    """Main function to seed all tables."""
    print("🌱 Creating tables and seeding database with sample data...")
    
    # First, create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    
    async with async_session_maker() as db:
        # Check if data already exists
        try:
            result = await db.execute(text("SELECT COUNT(*) FROM outlets"))
            count = result.scalar()
            
            if count > 0:
                print("ℹ️ Database already has data, skipping seed")
                return
        except Exception:
            # Table might not exist yet
            pass
        
        outlets = await seed_outlets(db)
        orders = await seed_orders(db, outlets)
        routes = await seed_routes(db)
        await seed_boxes(db, orders, routes)
        await seed_route_nodes(db, routes, outlets)
        
        print("✅ Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_database())
