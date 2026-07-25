"""
app/middleware/request_id.py
----------------------------
ASGI middleware that attaches a unique request ID and correlation ID to
every incoming request.

Headers honoured (in order of priority):
    X-Correlation-ID   — upstream/client provided trace ID
    X-Request-ID       — request-level unique ID generated if missing

Both headers are echoed back in the response so clients can correlate
logs across services.
"""

import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.constants import CORRELATION_ID_HEADER, REQUEST_ID_HEADER
from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Attaches X-Request-ID and X-Correlation-ID to every request/response.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id: str = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        correlation_id: str = request.headers.get(CORRELATION_ID_HEADER) or request_id

        # Make IDs available to the request state (accessible in routes/deps)
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        logger.debug(
            "Incoming request",
            extra={
                "request_id": request_id,
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
            },
        )

        response: Response = await call_next(request)

        # Echo IDs in the response
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response
