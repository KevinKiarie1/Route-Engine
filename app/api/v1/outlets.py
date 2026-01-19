"""
Outlet API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.outlet import OutletPriority, OutletStatus
from app.schemas.outlet import (
    OutletCreate,
    OutletUpdate,
    OutletResponse,
    OutletListResponse,
    OutletNearbyQuery,
)
from app.repositories.outlet_repository import OutletRepository

router = APIRouter(prefix="/outlets", tags=["Outlets"])


def get_repository(session: AsyncSession = Depends(get_db)) -> OutletRepository:
    """Dependency to get outlet repository."""
    return OutletRepository(session)


@router.post(
    "/",
    response_model=OutletResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new outlet"
)
async def create_outlet(
    outlet_data: OutletCreate,
    repo: OutletRepository = Depends(get_repository)
) -> OutletResponse:
    """
    Create a new retail outlet with GPS coordinates and priority.
    
    - **code**: Unique outlet identifier
    - **name**: Outlet display name
    - **gps_coordinates**: Latitude and longitude
    - **priority**: Delivery priority (critical, high, medium, low, deferred)
    """
    # Check for duplicate code
    existing = await repo.get_by_code(outlet_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Outlet with code '{outlet_data.code}' already exists"
        )
    
    outlet = await repo.create(outlet_data)
    return _to_response(outlet)


@router.get(
    "/",
    response_model=OutletListResponse,
    summary="List all outlets"
)
async def list_outlets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    repo: OutletRepository = Depends(get_repository)
) -> OutletListResponse:
    """Get paginated list of outlets with optional filters."""
    # Convert string filters to enums
    status_enum = OutletStatus(status) if status else None
    priority_enum = OutletPriority[priority.upper()] if priority else None
    
    outlets, total = await repo.get_all(
        page=page,
        page_size=page_size,
        status=status_enum,
        priority=priority_enum
    )
    
    pages = (total + page_size - 1) // page_size
    
    return OutletListResponse(
        items=[_to_response(o) for o in outlets],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get(
    "/nearby",
    response_model=list,
    summary="Find nearby outlets"
)
async def find_nearby_outlets(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10.0, gt=0, le=100),
    limit: int = Query(10, ge=1, le=100),
    priority: Optional[str] = Query(None),
    repo: OutletRepository = Depends(get_repository)
):
    """
    Find outlets within a radius of the given coordinates.
    
    Uses PostGIS spatial indexing for efficient queries.
    Returns outlets sorted by distance.
    """
    priority_enum = OutletPriority[priority.upper()] if priority else None
    
    results = await repo.find_nearby(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit,
        priority=priority_enum
    )
    
    return [
        {
            "outlet": _to_response(outlet),
            "distance_km": round(distance, 2)
        }
        for outlet, distance in results
    ]


@router.get(
    "/{outlet_id}",
    response_model=OutletResponse,
    summary="Get outlet by ID"
)
async def get_outlet(
    outlet_id: int,
    repo: OutletRepository = Depends(get_repository)
) -> OutletResponse:
    """Get a specific outlet by its ID."""
    outlet = await repo.get_by_id(outlet_id)
    if not outlet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outlet with ID {outlet_id} not found"
        )
    return _to_response(outlet)


@router.get(
    "/code/{code}",
    response_model=OutletResponse,
    summary="Get outlet by code"
)
async def get_outlet_by_code(
    code: str,
    repo: OutletRepository = Depends(get_repository)
) -> OutletResponse:
    """Get a specific outlet by its unique code."""
    outlet = await repo.get_by_code(code)
    if not outlet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outlet with code '{code}' not found"
        )
    return _to_response(outlet)


@router.patch(
    "/{outlet_id}",
    response_model=OutletResponse,
    summary="Update an outlet"
)
async def update_outlet(
    outlet_id: int,
    update_data: OutletUpdate,
    repo: OutletRepository = Depends(get_repository)
) -> OutletResponse:
    """Update outlet details. Only provided fields will be updated."""
    outlet = await repo.update(outlet_id, update_data)
    if not outlet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outlet with ID {outlet_id} not found"
        )
    return _to_response(outlet)


@router.delete(
    "/{outlet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an outlet"
)
async def delete_outlet(
    outlet_id: int,
    repo: OutletRepository = Depends(get_repository)
):
    """Delete an outlet by ID."""
    deleted = await repo.delete(outlet_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outlet with ID {outlet_id} not found"
        )


def _to_response(outlet) -> OutletResponse:
    """Convert Outlet model to response schema."""
    return OutletResponse(
        id=outlet.id,
        code=outlet.code,
        name=outlet.name,
        address=outlet.address,
        contact_name=outlet.contact_name,
        contact_phone=outlet.contact_phone,
        gps_lat=outlet.gps_lat,
        gps_long=outlet.gps_long,
        priority=outlet.priority.name.lower(),
        status=outlet.status.value,
        delivery_window_start=outlet.delivery_window_start,
        delivery_window_end=outlet.delivery_window_end,
        avg_service_time=outlet.avg_service_time,
        created_at=outlet.created_at,
        updated_at=outlet.updated_at
    )
