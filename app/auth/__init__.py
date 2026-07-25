"""
app/auth/__init__.py
--------------------
Authentication module package.

Public API — import from here in the rest of the codebase:

    from app.auth.dependencies import CurrentUser, CurrentUserId, require_role
    from app.auth.router import router as auth_router
"""

from app.auth.dependencies import (   # noqa: F401
    AuthSvc,
    CurrentUser,
    CurrentUserId,
    OptionalUser,
    get_auth_service,
    get_current_user,
    get_current_user_id,
    get_optional_user,
    require_role,
)
from app.auth.router import router as auth_router   # noqa: F401

__all__ = [
    # Router
    "auth_router",
    # Dependencies
    "AuthSvc",
    "CurrentUser",
    "CurrentUserId",
    "OptionalUser",
    "get_auth_service",
    "get_current_user",
    "get_current_user_id",
    "get_optional_user",
    "require_role",
]
