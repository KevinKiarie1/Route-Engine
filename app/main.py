"""
Farmer's Choice - Logistics Management System
Main FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import api_router

# Frontend build directory
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("⚠️ Running without database - some endpoints will not work")
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Logistics Management System for production and transport to retail outlets",
    lifespan=lifespan,
)

# CORS middleware - allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - redirects to docs."""
    return {
        "message": "Welcome to Farmer's Choice Logistics API",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Serve frontend static files in production
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    
    @app.get("/dashboard", response_class=FileResponse, tags=["Dashboard"])
    async def serve_dashboard():
        """Serve the React dashboard."""
        return FileResponse(FRONTEND_DIR / "index.html")

