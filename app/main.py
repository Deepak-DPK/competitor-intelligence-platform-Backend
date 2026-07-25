"""
app/main.py
-----------
FastAPI application factory.

Responsibilities:
- Instantiate the FastAPI app with metadata
- Register CORS middleware (restricted to FRONTEND_URL in production)
- Register custom middlewares (request-ID, access log)
- Mount the /api/v1 router
- Configure startup / shutdown lifespan events
- Expose the app object for Uvicorn:  uvicorn app.main:app
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.constants import API_V1_PREFIX
from app.core.logging import get_logger, setup_logging
from app.middleware.logging import AccessLogMiddleware
from app.middleware.request_id import RequestIDMiddleware

# ------------------------------------------------------------------ #
# Bootstrap logging before anything else runs
# ------------------------------------------------------------------ #
setup_logging()
logger = get_logger(__name__)


# ------------------------------------------------------------------ #
# Lifespan  (startup / shutdown hooks)
# ------------------------------------------------------------------ #

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Runs code on application startup and shutdown.

    Startup  → verify DB connectivity, warm connection pool.
    Shutdown → dispose engine, release all connections.
    """
    # ---- Startup ----
    logger.info(
        "Starting %s v%s [%s]",
        settings.APP_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
    )

    from app.database.session import engine
    # Warm the connection pool by opening (and immediately closing) a connection
    try:
        async with engine.connect() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection pool warmed up successfully")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Database warmup skipped (will retry on first request): %s", exc)

    yield  # ←— application runs here

    # ---- Shutdown ----
    logger.info("Shutting down %s — disposing engine", settings.APP_NAME)
    await engine.dispose()
    logger.info("Engine disposed. Goodbye.")


# ------------------------------------------------------------------ #
# Application factory
# ------------------------------------------------------------------ #

def create_application() -> FastAPI:
    """Build and return the fully configured FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI-powered competitor intelligence platform for hotel booking businesses. "
            "Monitors competitor websites, pricing, keywords, social media and advertising."
        ),
        version=settings.VERSION,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ---------------------------------------------------------------- #
    # CORS
    # ---------------------------------------------------------------- #
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Correlation-ID"],
    )

    # ---------------------------------------------------------------- #
    # Custom middleware  (applied inner-first, so order matters)
    # RequestID must run BEFORE AccessLog so that access log can read
    # request.state.request_id.
    # ---------------------------------------------------------------- #
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # ---------------------------------------------------------------- #
    # Routers
    # ---------------------------------------------------------------- #
    app.include_router(api_v1_router, prefix=API_V1_PREFIX)

    # ---------------------------------------------------------------- #
    # Global exception handlers
    # ---------------------------------------------------------------- #

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred.",
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    return app


# Module-level app instance (referenced by Uvicorn start command)
app: FastAPI = create_application()
