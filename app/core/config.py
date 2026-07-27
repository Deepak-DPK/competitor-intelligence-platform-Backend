"""
app/core/config.py
------------------
Central application configuration loaded from environment variables.
Uses Pydantic Settings v2 for type-safe, validated settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All application settings sourced from environment variables.
    Mirrors the variables defined in the Project Constitution.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_NAME: str = Field(default="Competitor Intelligence", description="Application name")
    ENVIRONMENT: str = Field(default="development", description="Runtime environment: development | staging | production")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    VERSION: str = Field(default="1.0.0", description="API version string")
    API_V1_PREFIX: str = Field(default="/api/v1", description="Global API v1 route prefix")

    # ------------------------------------------------------------------ #
    # Security / JWT
    # ------------------------------------------------------------------ #
    SECRET_KEY: str = Field(..., description="Long random secret used for JWT signing")
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="JWT expiry in minutes (default 24 h)")

    # ------------------------------------------------------------------ #
    # Database  (Supabase PostgreSQL)
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = Field(
        ...,
        description="Async PostgreSQL connection string. "
        "Format: postgresql+asyncpg://USER:PASSWORD@HOST:5432/postgres",
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # ------------------------------------------------------------------ #
    # Supabase
    # ------------------------------------------------------------------ #
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase service-role key (backend only)")
    SUPABASE_JWT_SECRET: str = Field(..., description="Supabase JWT secret for token verification")

    # ------------------------------------------------------------------ #
    # External AI / Scraping Services
    # ------------------------------------------------------------------ #
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")
    FIRECRAWL_API_KEY: str = Field(default="fc-local-test-key", description="Firecrawl Cloud API key")

    # ------------------------------------------------------------------ #
    # CORS
    # ------------------------------------------------------------------ #
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Allowed origin for CORS (production: Vercel URL)",
    )

    @field_validator("FRONTEND_URL", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str) -> str:
        # Strip trailing slash to keep origin clean
        return v.rstrip("/")

    @property
    def cors_origins(self) -> List[str]:
        """Returns the list of allowed CORS origins."""
        origins = [
            self.FRONTEND_URL,
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        return list(dict.fromkeys(origins))  # deduplicate while preserving order

    # ------------------------------------------------------------------ #
    # Playwright
    # ------------------------------------------------------------------ #
    PLAYWRIGHT_BROWSERS_PATH: Optional[str] = Field(
        default="0",
        description="Path for Playwright browser binaries (0 = use system default on Render)",
    )

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    LOG_LEVEL: str = Field(default="INFO", description="Python logging level")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings singleton.
    Use this function everywhere instead of instantiating Settings directly.
    """
    return Settings()  # type: ignore[call-arg]


# Module-level convenience export
settings: Settings = get_settings()
