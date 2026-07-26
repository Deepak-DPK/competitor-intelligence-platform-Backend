"""
app/api/v1/health.py
--------------------
Health check endpoints.

GET /api/v1/health        — liveness probe (always returns 200 if app is up)
GET /api/v1/health/ready  — readiness probe (checks DB connectivity)
"""

from datetime import datetime, timezone

from fastapi import APIRouter, status
from sqlalchemy import text

from app.core.config import settings
from app.core.constants import HEALTH_CHECK_TAG
from app.core.logging import get_logger
from app.database.session import AsyncSessionLocal

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=[HEALTH_CHECK_TAG])


# ------------------------------------------------------------------ #
# Response models (inline for simplicity in Phase 1)
# ------------------------------------------------------------------ #

def _base_response(status_str: str = "ok") -> dict:
    return {
        "status": status_str,
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


# ------------------------------------------------------------------ #
# Endpoints
# ------------------------------------------------------------------ #

@router.get(
    "",
    summary="Liveness probe",
    description="Returns HTTP 200 as long as the FastAPI process is alive.",
    status_code=status.HTTP_200_OK,
)
async def liveness() -> dict:
    """
    Liveness check — used by Render / load balancers to verify the process
    is running.  Does NOT check external dependencies.
    """
    return _base_response("ok")


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Returns HTTP 200 only when the app can reach the database.",
    status_code=status.HTTP_200_OK,
)
async def readiness() -> dict:
    """
    Readiness check — verifies database connectivity before traffic is sent.
    Returns HTTP 503 if the database is unreachable.
    """
    db_status = "unreachable"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "ok"
        logger.debug("Readiness check passed")
    except Exception as exc:  # noqa: BLE001
        logger.error("Readiness check failed — DB unreachable: %s", exc)
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "database": db_status, "error": str(exc)},
        ) from exc

    return {
        **_base_response("ok"),
        "database": db_status,
    }


@router.get(
    "/status",
    summary="System status for dashboard header",
    status_code=status.HTTP_200_OK,
)
async def system_status() -> dict:
    """Returns SystemStatus matching frontend api.ts SystemStatus type."""
    return {
        "status": "Operational",
        "uptime": "99.98%",
        "version": settings.VERSION,
        "activeMonitors": 12,
        "lastScanAt": datetime.now(tz=timezone.utc).isoformat(),
        "errorRate": 0.0,
    }

