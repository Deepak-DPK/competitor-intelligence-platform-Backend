"""
app/auth/router.py
------------------
FastAPI router for authentication endpoints.

Prefix:  /auth   (mounted under /api/v1 → full path: /api/v1/auth/...)
Tag:     Auth

Endpoints:
    POST   /auth/register      — create new account
    POST   /auth/login         — obtain tokens
    POST   /auth/refresh       — exchange refresh token for new access token
    POST   /auth/logout        — invalidate session on Supabase
    GET    /auth/me            — return current user profile
    PATCH  /auth/me            — update current user profile

All endpoints use dependency injection from app/auth/dependencies.py.
No database or Supabase logic lives in this file — pure routing + HTTP.

Refactor notes (Phase 3 review):
  - Removed unused imports (Request, Depends, get_auth_service, get_current_user).
  - Removed stray `from uuid import UUID` inside update_me body.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Header, status

from app.auth.dependencies import AuthSvc, CurrentUser
from app.core.constants import AUTH_TAG
from app.core.logging import get_logger
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

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=[AUTH_TAG])


# ------------------------------------------------------------------ #
# POST /auth/register
# ------------------------------------------------------------------ #

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
    description=(
        "Creates a new user account via Supabase Auth and mirrors the profile "
        "into the local database. Returns tokens immediately if email confirmation "
        "is disabled; otherwise returns an empty token pair until confirmed."
    ),
)
async def register(
    payload: RegisterRequest,
    service: AuthSvc,
) -> AuthResponse:
    return await service.register(payload)


# ------------------------------------------------------------------ #
# POST /auth/login
# ------------------------------------------------------------------ #

@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    description="Authenticates the user against Supabase Auth and returns a token pair.",
)
async def login(
    payload: LoginRequest,
    service: AuthSvc,
) -> AuthResponse:
    return await service.login(payload)


# ------------------------------------------------------------------ #
# POST /auth/refresh
# ------------------------------------------------------------------ #

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description=(
        "Exchanges a valid Supabase refresh token for a new access token + "
        "rotated refresh token. The old refresh token is immediately invalidated."
    ),
)
async def refresh_token(
    payload: RefreshTokenRequest,
    service: AuthSvc,
) -> TokenResponse:
    return await service.refresh_token(payload)


# ------------------------------------------------------------------ #
# POST /auth/logout
# ------------------------------------------------------------------ #

@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout — invalidate session",
    description=(
        "Revokes the Supabase session server-side. The client should also "
        "discard both tokens from local storage."
    ),
)
async def logout(
    payload: LogoutRequest,
    service: AuthSvc,
    authorization: Annotated[Optional[str], Header()] = None,
) -> MessageResponse:
    token = ""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    return await service.logout(payload, access_token=token)


# ------------------------------------------------------------------ #
# GET /auth/me
# ------------------------------------------------------------------ #

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns the authenticated user's full profile. Requires a valid Bearer token.",
)
async def get_me(
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse.model_validate(current_user)


# ------------------------------------------------------------------ #
# PATCH /auth/me
# ------------------------------------------------------------------ #

@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description=(
        "Updates mutable profile fields (full_name, avatar_url) "
        "for the authenticated user."
    ),
)
async def update_me(
    payload: UpdateProfileRequest,
    current_user: CurrentUser,
    service: AuthSvc,
) -> UserResponse:
    return await service.update_profile(current_user.id, payload)
