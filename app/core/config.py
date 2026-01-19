"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Farmer's Choice Logistics"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    
    # Database - Railway provides DATABASE_URL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/farmers_choice"
    DATABASE_ECHO: bool = False
    
    @property
    def database_url_sync(self) -> str:
        """Convert async URL to sync for Railway if needed."""
        url = self.DATABASE_URL
        # Railway uses postgres:// but SQLAlchemy async needs postgresql+asyncpg://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    
    # PostGIS SRID (WGS 84 - standard GPS coordinate system)
    SRID: int = 4326
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
