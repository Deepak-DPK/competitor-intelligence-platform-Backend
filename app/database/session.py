"""
app/database/session.py
-----------------------
SQLAlchemy 2 async engine and session factory.

Design choices:
- asyncpg driver for maximum async performance with PostgreSQL.
- pool_pre_ping=True: validates connections before use (important for
  Supabase which may terminate idle connections).
- Async sessions used throughout; no sync session exposed.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------ #
# Engine
# ------------------------------------------------------------------ #

def _make_engine() -> AsyncEngine:
    """Build the SQLAlchemy async engine from the DATABASE_URL config."""
    connect_args: dict = {}

    # Supabase / Render environments may require SSL
    if settings.is_production:
        connect_args["ssl"] = "require"

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,           # log SQL in debug mode
        pool_pre_ping=True,            # heartbeat before every checkout
        pool_size=5,                   # suitable for Render starter tier
        max_overflow=10,               # burst headroom
        pool_recycle=1800,             # recycle connections every 30 min
        connect_args=connect_args,
    )
    logger.info("Database engine created", extra={"url": settings.DATABASE_URL[:40] + "..."})
    return engine


# Module-level engine singleton
engine: AsyncEngine = _make_engine()


# ------------------------------------------------------------------ #
# Session factory
# ------------------------------------------------------------------ #

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,    # objects remain accessible after commit
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
)


# ------------------------------------------------------------------ #
# Dependency / context manager
# ------------------------------------------------------------------ #

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session.

    Usage in route:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
