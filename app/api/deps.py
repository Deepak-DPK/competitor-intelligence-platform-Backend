"""
app/api/deps.py
---------------
Shared FastAPI dependency functions.

All route files import their dependencies from here to ensure a single
source of truth.  New dependencies (e.g. pagination, permissions) are
added here and nowhere else.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import verify_supabase_jwt
from app.database.session import get_db

logger = get_logger(__name__)


# ------------------------------------------------------------------ #
# Type aliases (for cleaner route signatures)
# ------------------------------------------------------------------ #

DBSession = Annotated[AsyncSession, Depends(get_db)]


# ------------------------------------------------------------------ #
# Auth dependency
# ------------------------------------------------------------------ #

async def get_current_user_id(
    authorization: Annotated[Optional[str], Header()] = None,
) -> UUID:
    """
    Extracts and verifies the Supabase JWT from the Authorization header.

    Returns the user UUID (`sub` claim) on success.
    Raises HTTP 401 on missing / invalid / expired tokens.

    Full user-object lookup will be wired in Phase 2 once the User model
    exists.  For now this returns the raw UUID.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise credentials_exception

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise credentials_exception

    try:
        payload = verify_supabase_jwt(token)
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise credentials_exception
        return UUID(user_id)
    except (ExpiredSignatureError, InvalidTokenError, ValueError) as exc:
        logger.warning("JWT verification failed: %s", exc)
        raise credentials_exception from exc


# ------------------------------------------------------------------ #
# Convenience annotated types for routes
# ------------------------------------------------------------------ #

CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]


# ------------------------------------------------------------------ #
# Pagination
# ------------------------------------------------------------------ #

class PaginationParams:
    """Common pagination query parameters."""

    def __init__(self, page: int = 1, page_size: int = 20) -> None:
        if page < 1:
            raise HTTPException(status_code=400, detail="page must be >= 1")
        if not (1 <= page_size <= 100):
            raise HTTPException(status_code=400, detail="page_size must be between 1 and 100")
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


Pagination = Annotated[PaginationParams, Depends(PaginationParams)]
