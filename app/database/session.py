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
    db_url = settings.DATABASE_URL
    connect_args: dict = {}
    kwargs: dict = {
        "echo": settings.DEBUG,
    }

    if db_url.startswith("postgresql"):
        try:
            import asyncpg  # noqa: F401
        except ImportError:
            logger.warning("asyncpg not installed, falling back to SQLite in-memory database for testing.")
            db_url = "sqlite+aiosqlite:///:memory:"
        else:
            if settings.is_production:
                connect_args["ssl"] = "require"
            connect_args["statement_cache_size"] = 0
            connect_args["prepared_statement_cache_size"] = 0
            kwargs["pool_pre_ping"] = True
            kwargs["pool_recycle"] = 1800
            kwargs["pool_size"] = 5
            kwargs["max_overflow"] = 10

    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    kwargs["connect_args"] = connect_args

    engine = create_async_engine(
        db_url,
        **kwargs,
    )
    logger.info("Database engine created", extra={"url": db_url[:40] + "..."})
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
