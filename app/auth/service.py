"""
app/auth/service.py
--------------------
Authentication business logic.

This layer sits between the router (HTTP) and the repository (DB).
It orchestrates:
  1. Supabase Auth API calls (sign-up, sign-in, refresh, sign-out)
  2. Local user record sync (mirror Supabase auth.users into public.users)
  3. JWT token management (for internal tokens)
  4. Password hashing (for non-Supabase flows if needed)

Architecture decision:
  Supabase Auth is the PRIMARY identity provider.
  - Supabase issues and manages the refresh token lifecycle.
  - We trust Supabase JWTs and mirror the user profile locally.
  - The local ``users`` table is a projection of Supabase's auth.users.
"""

from typing import Optional
from uuid import UUID

import httpx
from supabase import AsyncClient as SupabaseAsyncClient, create_async_client

from app.auth.repository import AuthRepository
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)
from app.utils.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)

logger = get_logger(__name__)


# ------------------------------------------------------------------ #
# Supabase async client factory
# ------------------------------------------------------------------ #

async def _get_supabase() -> SupabaseAsyncClient:
    """Build an async Supabase client from settings."""
    return await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# ------------------------------------------------------------------ #
# Helper: build TokenResponse from settings
# ------------------------------------------------------------------ #

def _build_tokens(user_id: UUID, supabase_access: str, supabase_refresh: str) -> TokenResponse:
    """
    Return a TokenResponse.

    We prefer Supabase's own access token (already signed with SUPABASE_JWT_SECRET)
    so the frontend can call Supabase Storage / RLS-protected tables directly.
    The refresh token is always Supabase-managed (opaque string).
    """
    return TokenResponse(
        access_token=supabase_access,
        refresh_token=supabase_refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ------------------------------------------------------------------ #
# AuthService
# ------------------------------------------------------------------ #

class AuthService:
    """
    Orchestrates authentication flows using Supabase Auth + local DB sync.

    Instantiated per-request via FastAPI dependency injection.
    """

    def __init__(self, repo: AuthRepository) -> None:
        self._repo = repo

    # ---------------------------------------------------------------- #
    # Register
    # ---------------------------------------------------------------- #

    async def register(self, payload: RegisterRequest) -> AuthResponse:
        """
        Register a new user.

        Flow:
          1. Check local DB for duplicate email.
          2. Call Supabase Auth sign-up (creates auth.users record).
          3. Mirror user into public.users with the Supabase UUID.
          4. Return AuthResponse with tokens + profile.
        """
        # 1. Duplicate check (fast — avoids round-trip to Supabase)
        if await self._repo.email_exists(payload.email):
            raise ConflictException("An account with this email already exists.")

        # 2. Supabase Auth sign-up
        supabase = await _get_supabase()
        try:
            resp = await supabase.auth.sign_up(
                {"email": payload.email, "password": payload.password}
            )
        except Exception as exc:
            logger.error("Supabase sign-up failed: %s", exc)
            raise UnauthorizedException(
                "Registration failed. Please check your email and try again."
            ) from exc

        if not resp.user:
            raise UnauthorizedException("Registration failed — no user returned by Supabase.")

        supabase_user_id = UUID(str(resp.user.id))

        # 3. Mirror into public.users
        user = await self._repo.create(
            email=payload.email,
            full_name=payload.full_name,
            supabase_id=supabase_user_id,
        )

        # 4. Build response
        #    Supabase may require email confirmation — if session is None, tokens are empty.
        session = resp.session
        if session:
            tokens = _build_tokens(user.id, session.access_token, session.refresh_token)
        else:
            # Email confirmation required — no tokens yet
            tokens = TokenResponse(
                access_token="",
                refresh_token="",
                token_type="bearer",
                expires_in=0,
            )

        logger.info("User registered", extra={"user_id": str(user.id)})
        return AuthResponse(user=UserResponse.model_validate(user), tokens=tokens)

    # ---------------------------------------------------------------- #
    # Login
    # ---------------------------------------------------------------- #

    async def login(self, payload: LoginRequest) -> AuthResponse:
        """
        Authenticate an existing user with email + password.

        Flow:
          1. Call Supabase Auth sign-in (validates password in Supabase).
          2. Upsert user in public.users (keeps profile in sync).
          3. Return AuthResponse.
        """
        supabase = await _get_supabase()
        try:
            resp = await supabase.auth.sign_in_with_password(
                {"email": payload.email, "password": payload.password}
            )
        except Exception as exc:
            logger.warning("Login failed for %s: %s", payload.email, exc)
            raise UnauthorizedException("Invalid email or password.") from exc

        if not resp.user or not resp.session:
            raise UnauthorizedException("Invalid email or password.")

        supabase_user_id = UUID(str(resp.user.id))

        # Upsert local user record
        user = await self._repo.get_by_id(supabase_user_id)
        if user is None:
            # First login after manual DB reset or migration — create local record
            user = await self._repo.create(
                email=payload.email,
                full_name=resp.user.user_metadata.get("full_name") if resp.user.user_metadata else None,
                supabase_id=supabase_user_id,
            )

        tokens = _build_tokens(user.id, resp.session.access_token, resp.session.refresh_token)
        logger.info("User logged in", extra={"user_id": str(user.id)})
        return AuthResponse(user=UserResponse.model_validate(user), tokens=tokens)

    # ---------------------------------------------------------------- #
    # Refresh token
    # ---------------------------------------------------------------- #

    async def refresh_token(self, payload: RefreshTokenRequest) -> TokenResponse:
        """
        Exchange a Supabase refresh token for a new access token.

        Supabase rotates the refresh token on each use (rolling refresh).
        """
        supabase = await _get_supabase()
        try:
            resp = await supabase.auth.refresh_session(payload.refresh_token)
        except Exception as exc:
            logger.warning("Token refresh failed: %s", exc)
            raise UnauthorizedException("Invalid or expired refresh token.") from exc

        if not resp.session:
            raise UnauthorizedException("Token refresh failed.")

        user_id = UUID(str(resp.user.id)) if resp.user else UUID(int=0)
        logger.info("Token refreshed", extra={"user_id": str(user_id)})
        return _build_tokens(user_id, resp.session.access_token, resp.session.refresh_token)

    # ---------------------------------------------------------------- #
    # Logout
    # ---------------------------------------------------------------- #

    async def logout(self, payload: LogoutRequest, access_token: str) -> MessageResponse:
        """
        Sign the user out by invalidating the session on Supabase.

        Supabase revokes the refresh token server-side so it cannot be reused.
        """
        supabase = await _get_supabase()
        try:
            # Set the user's session so Supabase knows which session to revoke
            await supabase.auth.set_session(access_token, payload.refresh_token or "")
            await supabase.auth.sign_out()
        except Exception as exc:
            # Log but don't fail — client should discard tokens regardless
            logger.warning("Supabase sign-out encountered an error: %s", exc)

        logger.info("User logged out")
        return MessageResponse(message="Successfully logged out.")

    # ---------------------------------------------------------------- #
    # Current user
    # ---------------------------------------------------------------- #

    async def get_current_user(self, user_id: UUID) -> UserResponse:
        """Return the full profile for the authenticated user."""
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")
        return UserResponse.model_validate(user)

    # ---------------------------------------------------------------- #
    # Update profile
    # ---------------------------------------------------------------- #

    async def update_profile(
        self, user_id: UUID, payload: UpdateProfileRequest
    ) -> UserResponse:
        """Update the current user's mutable profile fields."""
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")

        updated = await self._repo.update_profile(
            user,
            full_name=payload.full_name,
            avatar_url=payload.avatar_url,
        )
        return UserResponse.model_validate(updated)
