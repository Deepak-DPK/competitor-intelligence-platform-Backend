"""
app/api/deps.py
---------------
Shared FastAPI dependency functions — single source of truth.

Phase 3 update: re-exports auth dependencies from app.auth.dependencies
so all route files can import from one place.

Import pattern in route files:
    from app.api.deps import DBSession, CurrentUser, CurrentUserId, Pagination
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (   # noqa: F401 — re-exported
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
from app.database.session import get_db

# ------------------------------------------------------------------ #
# DB session type alias
# ------------------------------------------------------------------ #

DBSession = Annotated[AsyncSession, Depends(get_db)]


from app.utils.exceptions import ValidationException

# ------------------------------------------------------------------ #
# Pagination, Searching, Sorting
# ------------------------------------------------------------------ #

class PaginationParams:
    """Common pagination query parameters for list endpoints."""

    def __init__(self, page: int = 1, page_size: int = 20) -> None:
        if page < 1:
            raise ValidationException(detail="page must be >= 1")
        if not (1 <= page_size <= 100):
            raise ValidationException(detail="page_size must be between 1 and 100")
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

Pagination = Annotated[PaginationParams, Depends(PaginationParams)]

class SearchParams:
    """Common search query parameters."""
    def __init__(self, q: Optional[str] = None) -> None:
        self.q = q

Search = Annotated[SearchParams, Depends(SearchParams)]

class SortParams:
    """Common sort query parameters."""
    def __init__(self, sort_by: Optional[str] = "created_at", sort_desc: bool = True) -> None:
        self.sort_by = sort_by
        self.sort_desc = sort_desc

Sort = Annotated[SortParams, Depends(SortParams)]

# ------------------------------------------------------------------ #
# Public re-exports (everything routes should need from this file)
# ------------------------------------------------------------------ #

__all__ = [
    # DB
    "DBSession",
    "get_db",
    # Auth
    "AuthSvc",
    "CurrentUser",
    "CurrentUserId",
    "OptionalUser",
    "get_auth_service",
    "get_current_user",
    "get_current_user_id",
    "get_optional_user",
    "require_role",
    # Pagination
    "Pagination",
    "PaginationParams",
    # Search
    "Search",
    "SearchParams",
    # Sort
    "Sort",
    "SortParams",
]
