"""
Repository for Outlet data access with PostGIS spatial queries.
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_MakePoint, ST_SetSRID

from app.models.outlet import Outlet, OutletPriority, OutletStatus
from app.schemas.outlet import OutletCreate, OutletUpdate, OutletPriorityEnum
from app.core.config import settings


class OutletRepository:
    """
    Data access layer for Outlet entities.
    Provides CRUD operations and spatial queries using PostGIS.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, outlet_data: OutletCreate) -> Outlet:
        """Create a new outlet."""
        # Convert priority enum from API to database enum
        db_priority = OutletPriority[outlet_data.priority.name]
        
        # Create PostGIS point from coordinates
        location = Outlet.create_location(
            latitude=outlet_data.gps_coordinates.latitude,
            longitude=outlet_data.gps_coordinates.longitude
        )
        
        outlet = Outlet(
            code=outlet_data.code,
            name=outlet_data.name,
            address=outlet_data.address,
            contact_name=outlet_data.contact_name,
            contact_phone=outlet_data.contact_phone,
            location=location,
            priority=db_priority,
            delivery_window_start=outlet_data.delivery_window.start_minutes,
            delivery_window_end=outlet_data.delivery_window.end_minutes,
            avg_service_time=outlet_data.avg_service_time,
        )
        
        self.session.add(outlet)
        await self.session.flush()
        await self.session.refresh(outlet)
        return outlet
    
    async def get_by_id(self, outlet_id: int) -> Optional[Outlet]:
        """Get outlet by ID."""
        result = await self.session.execute(
            select(Outlet).where(Outlet.id == outlet_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Outlet]:
        """Get outlet by unique code."""
        result = await self.session.execute(
            select(Outlet).where(Outlet.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[OutletStatus] = None,
        priority: Optional[OutletPriority] = None
    ) -> Tuple[List[Outlet], int]:
        """
        Get paginated list of outlets with optional filters.
        Returns (outlets, total_count).
        """
        # Base query
        query = select(Outlet)
        count_query = select(func.count(Outlet.id))
        
        # Apply filters
        filters = []
        if status:
            filters.append(Outlet.status == status)
        if priority:
            filters.append(Outlet.priority == priority)
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Outlet.priority, Outlet.name)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.session.execute(query)
        outlets = result.scalars().all()
        
        return list(outlets), total
    
    async def update(self, outlet_id: int, update_data: OutletUpdate) -> Optional[Outlet]:
        """Update an existing outlet."""
        outlet = await self.get_by_id(outlet_id)
        if not outlet:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Handle GPS coordinates update
        if "gps_coordinates" in update_dict and update_dict["gps_coordinates"]:
            coords = update_dict.pop("gps_coordinates")
            outlet.location = Outlet.create_location(
                latitude=coords["latitude"],
                longitude=coords["longitude"]
            )
        
        # Handle priority conversion
        if "priority" in update_dict and update_dict["priority"]:
            outlet.priority = OutletPriority[update_dict.pop("priority").upper()]
        
        # Handle status conversion
        if "status" in update_dict and update_dict["status"]:
            outlet.status = OutletStatus(update_dict.pop("status"))
        
        # Handle delivery window
        if "delivery_window" in update_dict and update_dict["delivery_window"]:
            window = update_dict.pop("delivery_window")
            outlet.delivery_window_start = window["start_minutes"]
            outlet.delivery_window_end = window["end_minutes"]
        
        # Apply remaining updates
        for field, value in update_dict.items():
            if value is not None:
                setattr(outlet, field, value)
        
        await self.session.flush()
        await self.session.refresh(outlet)
        return outlet
    
    async def delete(self, outlet_id: int) -> bool:
        """Delete an outlet. Returns True if deleted."""
        outlet = await self.get_by_id(outlet_id)
        if not outlet:
            return False
        
        await self.session.delete(outlet)
        await self.session.flush()
        return True
    
    async def find_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 10,
        priority: Optional[OutletPriority] = None,
        status: OutletStatus = OutletStatus.ACTIVE
    ) -> List[Tuple[Outlet, float]]:
        """
        Find outlets within a given radius using PostGIS spatial query.
        Returns list of (outlet, distance_km) tuples ordered by distance.
        
        Uses ST_DWithin for efficient spatial index utilization.
        """
        # Convert radius to meters (PostGIS geography uses meters)
        radius_meters = radius_km * 1000
        
        # Create reference point
        ref_point = ST_SetSRID(ST_MakePoint(longitude, latitude), settings.SRID)
        
        # Build query with distance calculation
        distance_expr = ST_Distance(
            func.cast(Outlet.location, func.geography),
            func.cast(ref_point, func.geography)
        )
        
        query = (
            select(Outlet, (distance_expr / 1000).label("distance_km"))
            .where(
                ST_DWithin(
                    func.cast(Outlet.location, func.geography),
                    func.cast(ref_point, func.geography),
                    radius_meters
                )
            )
            .where(Outlet.status == status)
        )
        
        if priority:
            query = query.where(Outlet.priority == priority)
        
        query = query.order_by(distance_expr).limit(limit)
        
        result = await self.session.execute(query)
        return [(row.Outlet, row.distance_km) for row in result.all()]
    
    async def get_by_priority_order(
        self,
        outlet_ids: List[int]
    ) -> List[Outlet]:
        """
        Get outlets ordered by priority (for route sequencing).
        CRITICAL priority first, then HIGH, etc.
        """
        if not outlet_ids:
            return []
        
        result = await self.session.execute(
            select(Outlet)
            .where(Outlet.id.in_(outlet_ids))
            .order_by(Outlet.priority, Outlet.name)
        )
        return list(result.scalars().all())
