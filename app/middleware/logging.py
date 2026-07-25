"""
app/middleware/logging.py
-------------------------
ASGI middleware for structured HTTP access logging.

Logs method, path, status code, and elapsed time for every request.
Sensitive paths (auth tokens in query params) are not logged.
"""

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Emits a structured log line for every completed HTTP request."""

    # Paths excluded from access logs to reduce noise
    _SKIP_PATHS: frozenset[str] = frozenset({"/api/v1/health"})

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self._SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        request_id = getattr(request.state, "request_id", "-")

        logger.info(
            "%s %s %d",
            request.method,
            request.url.path,
            response.status_code,
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
                "request_id": request_id,
                "client_ip": (request.client.host if request.client else "unknown"),
            },
        )
        return response
