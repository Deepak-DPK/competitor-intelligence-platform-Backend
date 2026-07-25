"""
app/auth/dependencies.py
------------------------
FastAPI dependency functions for the authentication layer.

Provides:
- get_auth_service()     — injects AuthService (with repo + db)
- get_current_user()     — resolves JWT → full User ORM object
- get_current_user_id()  — resolves JWT → UUID only (lightweight)
- require_role()         — role-based access control factory
- require_admin()        — shortcut: admin-only protected routes
- OptionalUser           — annotated type for optional auth

All routes import their dependencies from this module or from
app/api/deps.py (which re-exports the common ones).

Refactor notes (Phase 3 review):
  - Removed unused ForbiddenException / UnauthorizedException imports.
  - Fixed require_admin() return type (returns a Depends() call, not User).
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.auth.service import AuthService
from app.core.constants import UserRole
from app.core.logging import get_logger
from app.core.security import verify_supabase_jwt
from app.database.session import get_db
from app.models.user import User

logger = get_logger(__name__)


# ------------------------------------------------------------------ #
# Internal helpers
# ------------------------------------------------------------------ #

def _credentials_exception(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _extract_bearer_token(authorization: Optional[str]) -> str:
    """
    Parse 'Bearer <token>' from the Authorization header.
    Raises HTTP 401 if missing or malformed.
    """
    if not authorization:
        raise _credentials_exception("Authorization header missing.")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise _credentials_exception("Invalid authorization scheme. Use 'Bearer <token>'.")
    return token


def _decode_and_get_user_id(token: str) -> UUID:
    """Verify Supabase JWT and return the subject UUID."""
    try:
        payload = verify_supabase_jwt(token)
        user_id_str: Optional[str] = payload.get("sub")
        if not user_id_str:
            raise _credentials_exception("Token has no subject claim.")
        return UUID(user_id_str)
    except (ExpiredSignatureError,):
        raise _credentials_exception("Token has expired.")
    except (InvalidTokenError, ValueError) as exc:
        logger.warning("JWT decode failed: %s", exc)
        raise _credentials_exception() from exc


# ------------------------------------------------------------------ #
# Service injection
# ------------------------------------------------------------------ #

async def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    """
    Dependency that constructs AuthService with a DB-session-scoped repository.
    Called once per request; the session is shared with the unit-of-work.
    """
    repo = AuthRepository(db)
    return AuthService(repo)


# ------------------------------------------------------------------ #
# Current user (UUID only — cheap, no DB hit)
# ------------------------------------------------------------------ #

async def get_current_user_id(
    authorization: Annotated[Optional[str], Header()] = None,
) -> UUID:
    """
    Extracts and verifies the Supabase JWT from the Authorization header.
    Returns the user UUID (``sub`` claim) without hitting the database.

    Use this dependency when you only need the user ID (e.g., ownership checks
    that join on user_id without needing the full User object).
    """
    token = _extract_bearer_token(authorization)
    return _decode_and_get_user_id(token)


# ------------------------------------------------------------------ #
# Current user (full ORM object — requires DB hit)
# ------------------------------------------------------------------ #

async def get_current_user(
    authorization: Annotated[Optional[str], Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Resolves the JWT to a fully hydrated User ORM object.

    Use when route logic needs the user's role, email, or other profile fields.
    Raises HTTP 401 if the token is invalid.
    Raises HTTP 401 if the user no longer exists in the local DB.
    """
    token = _extract_bearer_token(authorization)
    user_id = _decode_and_get_user_id(token)

    repo = AuthRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise _credentials_exception("User not found.")
    return user


# ------------------------------------------------------------------ #
# Optional auth — for routes that work for both anon and authenticated users
# ------------------------------------------------------------------ #

async def get_optional_user(
    authorization: Annotated[Optional[str], Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Like get_current_user but returns None instead of raising 401
    when no valid token is present.
    """
    if not authorization:
        return None
    try:
        token = _extract_bearer_token(authorization)
        user_id = _decode_and_get_user_id(token)
        repo = AuthRepository(db)
        return await repo.get_by_id(user_id)
    except HTTPException:
        return None


# ------------------------------------------------------------------ #
# Role-based access control
# ------------------------------------------------------------------ #

def require_role(*allowed_roles: UserRole):
    """
    Dependency factory — returns a dependency that enforces role membership.

    Usage in route:
        @router.get("/admin-only")
        async def admin_route(user: User = Depends(require_role(UserRole.ADMIN))):
            ...

        @router.get("/admin-or-member")
        async def shared_route(
            user: User = Depends(require_role(UserRole.ADMIN, UserRole.MEMBER))
        ):
            ...
    """
    async def _check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"This action requires one of the following roles: "
                    f"{', '.join(r.value for r in allowed_roles)}."
                ),
            )
        return current_user

    return _check_role


# ------------------------------------------------------------------ #
# Convenience shortcuts
# ------------------------------------------------------------------ #

def require_admin():
    """Shortcut: restrict route to admin users only.
    
    Usage:
        @router.get("/admin")
        async def admin_route(user: User = require_admin()):
            ...
    """
    return Depends(require_role(UserRole.ADMIN))


# ------------------------------------------------------------------ #
# Annotated type aliases — import these in route files for clean signatures
# ------------------------------------------------------------------ #

CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
OptionalUser = Annotated[Optional[User], Depends(get_optional_user)]
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
