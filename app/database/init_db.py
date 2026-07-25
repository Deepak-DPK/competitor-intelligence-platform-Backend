"""
app/database/init_db.py
-----------------------
Database initialisation utilities.

Provides two functions:
- ``init_db()``     — creates all tables that don't already exist (dev / test only).
- ``check_db()``    — verifies database connectivity (used by health check + startup).

In production, always use Alembic migrations (``alembic upgrade head``).
Never call ``init_db()`` in production — it bypasses Alembic's migration history.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.logging import get_logger
from app.database.base import Base
from app.database.session import engine

# Import all models to ensure they are registered on Base.metadata
import app.models  # noqa: F401

logger = get_logger(__name__)


async def init_db(db_engine: AsyncEngine = engine) -> None:
    """
    Create all tables defined in Base.metadata if they do not yet exist.

    WARNING: For DEVELOPMENT and TESTING only.
    In production, run: ``alembic upgrade head``

    This function is intentionally idempotent: running it multiple times
    will not drop or recreate existing tables.
    """
    logger.warning(
        "init_db() called — this creates tables directly and bypasses Alembic. "
        "Use only in development or testing."
    )
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialised via Base.metadata.create_all()")


async def drop_db(db_engine: AsyncEngine = engine) -> None:
    """
    Drop ALL tables (reverse order to respect FK constraints).

    DANGER: Irreversible data loss.  Use only in test teardown.
    """
    logger.warning("drop_db() called — dropping all tables!")
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("All database tables dropped.")


async def check_db(db_engine: AsyncEngine = engine) -> bool:
    """
    Verify that the database is reachable by executing a trivial query.

    Returns True on success, False on failure.
    Does NOT raise exceptions so callers can decide how to handle failures.
    """
    try:
        async with db_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.debug("Database connectivity check passed.")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Database connectivity check failed: %s", exc)
        return False
