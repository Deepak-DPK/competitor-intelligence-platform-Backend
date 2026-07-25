"""
app/schemas/auth.py
-------------------
Pydantic v2 schemas for authentication request and response bodies.

Conventions:
- Request schemas validate inbound data (strict types, field validators).
- Response schemas serialise outbound data (never expose hashed_password).
- All schemas use model_config = ConfigDict(from_attributes=True) so they
  can be hydrated directly from SQLAlchemy ORM objects.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ------------------------------------------------------------------ #
# Request schemas
# ------------------------------------------------------------------ #

class RegisterRequest(BaseModel):
    """Payload for POST /auth/register."""

    email: EmailStr = Field(..., description="Valid email address.")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password — minimum 8 characters.",
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User's display name.",
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Ensure the password has at least one digit and one letter."""
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_letter and has_digit):
            raise ValueError(
                "Password must contain at least one letter and one digit."
            )
        return v


class LoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    email: EmailStr = Field(..., description="Registered email address.")
    password: str = Field(..., min_length=1, description="Account password.")


class RefreshTokenRequest(BaseModel):
    """Payload for POST /auth/refresh."""

    refresh_token: str = Field(..., description="Opaque refresh token issued by Supabase.")


class LogoutRequest(BaseModel):
    """Payload for POST /auth/logout."""

    refresh_token: Optional[str] = Field(
        default=None,
        description="Refresh token to invalidate on Supabase. "
                    "If omitted, only the access token is discarded client-side.",
    )


class UpdateProfileRequest(BaseModel):
    """Payload for PATCH /auth/me — update current user profile."""

    full_name: Optional[str] = Field(default=None, max_length=255)
    avatar_url: Optional[str] = Field(default=None, max_length=2048)


# ------------------------------------------------------------------ #
# Response schemas
# ------------------------------------------------------------------ #

class UserResponse(BaseModel):
    """Public user object — never exposes sensitive fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """JWT token pair returned after login or token refresh."""

    access_token: str = Field(..., description="Short-lived JWT access token.")
    refresh_token: str = Field(..., description="Opaque refresh token (Supabase-managed).")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(..., description="Access token lifetime in seconds.")


class AuthResponse(BaseModel):
    """Combined auth response: tokens + user profile."""

    user: UserResponse
    tokens: TokenResponse


class MessageResponse(BaseModel):
    """Generic success message envelope."""

    message: str
    success: bool = True
