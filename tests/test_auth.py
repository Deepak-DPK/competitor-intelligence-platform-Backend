"""
tests/test_auth.py
------------------
Integration tests for the authentication endpoints.

Uses httpx AsyncClient wired to the FastAPI test app.
External Supabase calls are mocked so tests run without real credentials.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


# ------------------------------------------------------------------ #
# Helpers — mock Supabase responses
# ------------------------------------------------------------------ #

def _mock_supabase_user(email: str, user_id=None):
    uid = user_id or uuid4()
    user = MagicMock()
    user.id = str(uid)
    user.email = email
    user.user_metadata = {}
    return user, uid


def _mock_supabase_session(access: str = "mock_access", refresh: str = "mock_refresh"):
    session = MagicMock()
    session.access_token = access
    session.refresh_token = refresh
    return session


# ------------------------------------------------------------------ #
# Register
# ------------------------------------------------------------------ #

class TestRegister:
    @pytest.mark.asyncio
    async def test_register_missing_body(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/register", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "user@test.com", "password": "weakpass"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "Strong1pass"},
        )
        assert resp.status_code == 422


# ------------------------------------------------------------------ #
# Login
# ------------------------------------------------------------------ #

class TestLogin:
    @pytest.mark.asyncio
    async def test_login_missing_body(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/login", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient) -> None:
        """
        Without mocking Supabase, a real call would fail.
        We verify the endpoint exists and returns 401 on bad credentials.
        """
        with patch(
            "app.auth.service._get_supabase",
            new_callable=AsyncMock,
        ) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.sign_in_with_password = AsyncMock(
                side_effect=Exception("Invalid login credentials")
            )
            mock_sb.return_value = supabase_client

            resp = await client.post(
                "/api/v1/auth/login",
                json={"email": "wrong@test.com", "password": "WrongPass1"},
            )
        assert resp.status_code == 401


# ------------------------------------------------------------------ #
# /auth/me — protected route
# ------------------------------------------------------------------ #

class TestProtectedRoutes:
    @pytest.mark.asyncio
    async def test_me_no_token(self, client: AsyncClient) -> None:
        """GET /auth/me without a token must return 401."""
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_invalid_token(self, client: AsyncClient) -> None:
        """GET /auth/me with a garbage token must return 401."""
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer totally.invalid.token"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_malformed_scheme(self, client: AsyncClient) -> None:
        """GET /auth/me with Basic scheme must return 401."""
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert resp.status_code == 401


# ------------------------------------------------------------------ #
# Refresh
# ------------------------------------------------------------------ #

class TestRefreshToken:
    @pytest.mark.asyncio
    async def test_refresh_missing_body(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/refresh", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient) -> None:
        with patch(
            "app.auth.service._get_supabase",
            new_callable=AsyncMock,
        ) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.refresh_session = AsyncMock(
                side_effect=Exception("Invalid refresh token")
            )
            mock_sb.return_value = supabase_client

            resp = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "bad_token"},
            )
        assert resp.status_code == 401


# ------------------------------------------------------------------ #
# Logout
# ------------------------------------------------------------------ #

class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_no_token(self, client: AsyncClient) -> None:
        """Logout without a bearer token — service handles gracefully."""
        with patch(
            "app.auth.service._get_supabase",
            new_callable=AsyncMock,
        ) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.set_session = AsyncMock()
            supabase_client.auth.sign_out = AsyncMock()
            mock_sb.return_value = supabase_client

            resp = await client.post("/api/v1/auth/logout", json={})
        # No auth token → 200 because logout is idempotent
        assert resp.status_code == 200
        assert resp.json()["success"] is True
