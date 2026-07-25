"""
app/schemas/user.py
-------------------
Pydantic v2 schemas for User responses used across multiple routers.

Kept separate from auth.py so Projects / Competitors routers can import
UserResponse without pulling in the full auth schema tree.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublicSchema(BaseModel):
    """Minimal public user representation (e.g. for project member lists)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: str


class UserDetailSchema(UserPublicSchema):
    """Full user detail including timestamps — used for /auth/me."""

    created_at: datetime
    updated_at: datetime
