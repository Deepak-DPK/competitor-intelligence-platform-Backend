"""
app/auth/repository.py
-----------------------
Authentication data-access layer.

All database reads/writes for the auth module are concentrated here.
The service layer calls this repository; routes never touch the DB directly.

Design rules (from Database Design Document):
- Never hardcode SQL — use SQLAlchemy ORM only.
- Use async sessions exclusively.
- Repository/service pattern: repository = DB, service = business logic.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)


class AuthRepository:
    """
    Encapsulates all User-related database operations needed for auth.

    Injected into AuthService — never used directly from routes.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------ #
    # Reads
    # ------------------------------------------------------------------ #

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Fetch a user by primary key. Returns None if not found."""
        result = await self._db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email (case-insensitive). Returns None if not found."""
        result = await self._db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Return True if the email is already registered."""
        result = await self._db.execute(
            select(User.id).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none() is not None

    # ------------------------------------------------------------------ #
    # Writes
    # ------------------------------------------------------------------ #

    async def create(
        self,
        *,
        email: str,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        role: str = "member",
        supabase_id: Optional[UUID] = None,
    ) -> User:
        """
        Persist a new User row.

        When Supabase Auth creates the auth.users record, we mirror
        the same UUID via ``supabase_id`` so the two tables stay in sync.
        If supabase_id is None (e.g. dev/test), PostgreSQL generates a UUID.
        """
        user = User(
            email=email.lower().strip(),
            full_name=full_name,
            avatar_url=avatar_url,
            role=role,
        )
        if supabase_id is not None:
            user.id = supabase_id

        self._db.add(user)
        await self._db.flush()   # flush to get DB-generated values without committing
        await self._db.refresh(user)
        logger.info("User created", extra={"user_id": str(user.id), "email": user.email})
        return user

    async def update_profile(
        self,
        user: User,
        *,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> User:
        """Update mutable profile fields and return the updated object."""
        if full_name is not None:
            user.full_name = full_name
        if avatar_url is not None:
            user.avatar_url = avatar_url

        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        logger.info("User profile updated", extra={"user_id": str(user.id)})
        return user
