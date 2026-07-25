"""
app/auth/middleware.py
-----------------------
Role-enforcement ASGI middleware (Starlette BaseHTTPMiddleware).

Used for path-level role guards that apply to entire route prefixes
(e.g., everything under /api/v1/admin/* requires ADMIN role).

For individual route-level guards, use the ``require_role()`` dependency
from app/auth/dependencies.py instead.

NOTE: This middleware does NOT replace the dependency-based guards — it
provides a coarse-grained fallback for admin sub-applications that would
otherwise require adding Depends() to every single route.
"""

from typing import Callable, Optional, Set

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.constants import UserRole
from app.core.logging import get_logger
from app.core.security import verify_supabase_jwt

logger = get_logger(__name__)


class RoleMiddleware(BaseHTTPMiddleware):
    """
    Enforces a minimum role on a set of protected path prefixes.

    Configuration example (in main.py or a sub-application):
        app.add_middleware(
            RoleMiddleware,
            protected_prefixes={"/api/v1/admin"},
            required_role=UserRole.ADMIN,
        )
    """

    def __init__(
        self,
        app,
        protected_prefixes: Optional[Set[str]] = None,
        required_role: UserRole = UserRole.ADMIN,
    ) -> None:
        super().__init__(app)
        self._protected_prefixes: Set[str] = protected_prefixes or set()
        self._required_role: str = required_role.value

    def _is_protected(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self._protected_prefixes)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self._is_protected(request.url.path):
            return await call_next(request)

        # Extract bearer token
        auth_header: str = request.headers.get("authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header missing."},
            )

        token = auth_header.split(" ", 1)[1]
        try:
            payload = verify_supabase_jwt(token)
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token."},
            )

        # Check role claim — Supabase stores custom claims under app_metadata
        user_role: str = (
            (payload.get("app_metadata") or {}).get("role")
            or payload.get("role")
            or UserRole.MEMBER.value
        )

        if user_role != self._required_role:
            return JSONResponse(
                status_code=403,
                content={"detail": f"Role '{self._required_role}' required."},
            )

        return await call_next(request)
