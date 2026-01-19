# API v1
from fastapi import APIRouter
from app.api.v1.outlets import router as outlets_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(outlets_router)
api_router.include_router(dashboard_router)
