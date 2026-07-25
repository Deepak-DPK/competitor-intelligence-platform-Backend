"""
tests/test_auth.py
------------------
Phase 3 test suite for the authentication module.

Test categories:
  A. Schema validation (422 on bad input) — no DB or Supabase
  B. Protected routes (401/403) — JWT guard, no Supabase
  C. Authenticated routes — valid JWT + real in-memory User row
  D. Supabase-dependent flows (register/login/refresh) — Supabase mocked

Fixtures (from conftest.py):
  client         — AsyncClient wired to test app
  mock_user      — User row inserted in in-memory SQLite
  auth_headers   — {'Authorization': 'Bearer <valid_jwt>'}
  expired_access_token — expired JWT string
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient


# ================================================================== #
# A. Schema validation tests  (no auth, no DB, no Supabase)
# ================================================================== #

class TestRegisterValidation:
    """POST /auth/register input validation."""

    @pytest.mark.asyncio
    async def test_missing_body_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/register", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_email_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "Strong1pass"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_password_too_short_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "user@test.com", "password": "S1"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_password_letters_only_returns_422(self, client: AsyncClient) -> None:
        """Password must have at least one digit."""
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "user@test.com", "password": "onlyletters"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_password_digits_only_returns_422(self, client: AsyncClient) -> None:
        """Password must have at least one letter."""
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "user@test.com", "password": "12345678"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_valid_payload_shape_accepted(self, client: AsyncClient) -> None:
        """
        A structurally valid payload reaches the service layer.
        We mock Supabase to avoid a real API call.
        """
        uid = uuid4()
        mock_supabase_user = MagicMock()
        mock_supabase_user.id = str(uid)
        mock_session = MagicMock()
        mock_session.access_token = "acc"
        mock_session.refresh_token = "ref"

        mock_resp = MagicMock()
        mock_resp.user = mock_supabase_user
        mock_resp.session = mock_session

        with patch("app.auth.service._get_supabase", new_callable=AsyncMock) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.sign_up = AsyncMock(return_value=mock_resp)
            mock_sb.return_value = supabase_client

            resp = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "Secure1pass",
                    "full_name": "New User",
                },
            )

        assert resp.status_code == 201
        body = resp.json()
        assert "user" in body
        assert "tokens" in body
        assert body["user"]["email"] == "newuser@example.com"


class TestLoginValidation:
    """POST /auth/login input validation."""

    @pytest.mark.asyncio
    async def test_missing_body_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/login", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_password_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@test.com"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_email_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "badformat", "password": "anything"},
        )
        assert resp.status_code == 422


class TestRefreshValidation:
    """POST /auth/refresh input validation."""

    @pytest.mark.asyncio
    async def test_missing_body_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/auth/refresh", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_refresh_token_returns_422(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": ""},
        )
        assert resp.status_code == 422


# ================================================================== #
# B. Protected route guard tests  (no valid token)
# ================================================================== #

class TestProtectedRouteGuards:
    """JWT guard must block unauthenticated requests."""

    @pytest.mark.asyncio
    async def test_me_no_token_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_garbage_token_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer totally.garbage.token"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_basic_scheme_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_expired_token_returns_401(
        self, client: AsyncClient, expired_access_token: str
    ) -> None:
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_access_token}"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_update_me_no_token_returns_401(self, client: AsyncClient) -> None:
        resp = await client.patch(
            "/api/v1/auth/me",
            json={"full_name": "Updated Name"},
        )
        assert resp.status_code == 401


# ================================================================== #
# C. Authenticated route tests  (valid token + real DB row)
# ================================================================== #

class TestAuthenticatedRoutes:
    """Tests that use a real JWT + in-memory DB user row."""

    @pytest.mark.asyncio
    async def test_get_me_returns_user_profile(
        self,
        client: AsyncClient,
        mock_user,
        auth_headers: dict,
    ) -> None:
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "testuser@example.com"
        assert body["full_name"] == "Test User"
        assert body["role"] == "member"
        assert "id" in body
        assert "created_at" in body

    @pytest.mark.asyncio
    async def test_patch_me_updates_full_name(
        self,
        client: AsyncClient,
        mock_user,
        auth_headers: dict,
    ) -> None:
        resp = await client.patch(
            "/api/v1/auth/me",
            json={"full_name": "Updated Name"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_patch_me_updates_avatar_url(
        self,
        client: AsyncClient,
        mock_user,
        auth_headers: dict,
    ) -> None:
        resp = await client.patch(
            "/api/v1/auth/me",
            json={"avatar_url": "https://example.com/avatar.jpg"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["avatar_url"] == "https://example.com/avatar.jpg"

    @pytest.mark.asyncio
    async def test_patch_me_empty_payload_is_noop(
        self,
        client: AsyncClient,
        mock_user,
        auth_headers: dict,
    ) -> None:
        """PATCH with no fields — should return the unchanged profile."""
        resp = await client.patch(
            "/api/v1/auth/me",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == "testuser@example.com"


# ================================================================== #
# D. Supabase-dependent flows  (mocked Supabase client)
# ================================================================== #

class TestLoginWithMockedSupabase:
    @pytest.mark.asyncio
    async def test_login_wrong_credentials_returns_401(
        self, client: AsyncClient
    ) -> None:
        with patch("app.auth.service._get_supabase", new_callable=AsyncMock) as mock_sb:
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

    @pytest.mark.asyncio
    async def test_login_existing_user_returns_tokens(
        self,
        client: AsyncClient,
        mock_user,
    ) -> None:
        """Login for a user that already exists in the local DB."""
        uid = mock_user.id
        mock_sb_user = MagicMock()
        mock_sb_user.id = str(uid)
        mock_sb_user.user_metadata = {}
        mock_session = MagicMock()
        mock_session.access_token = "supabase_access"
        mock_session.refresh_token = "supabase_refresh"
        mock_resp = MagicMock()
        mock_resp.user = mock_sb_user
        mock_resp.session = mock_session

        with patch("app.auth.service._get_supabase", new_callable=AsyncMock) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.sign_in_with_password = AsyncMock(return_value=mock_resp)
            mock_sb.return_value = supabase_client

            resp = await client.post(
                "/api/v1/auth/login",
                json={"email": "testuser@example.com", "password": "Secure1pass"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["tokens"]["access_token"] == "supabase_access"
        assert body["tokens"]["refresh_token"] == "supabase_refresh"
        assert body["user"]["email"] == "testuser@example.com"


class TestRefreshWithMockedSupabase:
    @pytest.mark.asyncio
    async def test_refresh_invalid_token_returns_401(
        self, client: AsyncClient
    ) -> None:
        with patch("app.auth.service._get_supabase", new_callable=AsyncMock) as mock_sb:
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

    @pytest.mark.asyncio
    async def test_refresh_valid_token_returns_new_tokens(
        self, client: AsyncClient
    ) -> None:
        uid = uuid4()
        mock_sb_user = MagicMock()
        mock_sb_user.id = str(uid)
        mock_new_session = MagicMock()
        mock_new_session.access_token = "new_access"
        mock_new_session.refresh_token = "new_refresh"
        mock_resp = MagicMock()
        mock_resp.user = mock_sb_user
        mock_resp.session = mock_new_session

        with patch("app.auth.service._get_supabase", new_callable=AsyncMock) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.refresh_session = AsyncMock(return_value=mock_resp)
            mock_sb.return_value = supabase_client

            resp = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid_refresh_token"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["access_token"] == "new_access"
        assert body["refresh_token"] == "new_refresh"


class TestLogoutWithMockedSupabase:
    @pytest.mark.asyncio
    async def test_logout_succeeds_without_token(self, client: AsyncClient) -> None:
        """Logout is idempotent — no auth token needed, always returns 200."""
        with patch("app.auth.service._get_supabase", new_callable=AsyncMock) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.set_session = AsyncMock()
            supabase_client.auth.sign_out = AsyncMock()
            mock_sb.return_value = supabase_client

            resp = await client.post("/api/v1/auth/logout", json={})

        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert "logged out" in resp.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_supabase_error_still_returns_200(
        self, client: AsyncClient
    ) -> None:
        """Even if Supabase sign-out fails, we return 200 (client discards tokens)."""
        with patch("app.auth.service._get_supabase", new_callable=AsyncMock) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.set_session = AsyncMock(
                side_effect=Exception("Supabase unavailable")
            )
            supabase_client.auth.sign_out = AsyncMock()
            mock_sb.return_value = supabase_client

            resp = await client.post("/api/v1/auth/logout", json={})

        assert resp.status_code == 200


class TestRegisterWithMockedSupabase:
    @pytest.mark.asyncio
    async def test_register_duplicate_email_returns_409(
        self,
        client: AsyncClient,
        mock_user,
    ) -> None:
        """Registration with an email that already exists in DB → 409."""
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "testuser@example.com",   # same as mock_user
                "password": "Secure1pass",
            },
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_register_supabase_failure_returns_401(
        self, client: AsyncClient
    ) -> None:
        with patch("app.auth.service._get_supabase", new_callable=AsyncMock) as mock_sb:
            supabase_client = AsyncMock()
            supabase_client.auth.sign_up = AsyncMock(
                side_effect=Exception("Supabase error")
            )
            mock_sb.return_value = supabase_client

            resp = await client.post(
                "/api/v1/auth/register",
                json={"email": "brand_new@test.com", "password": "Secure1pass"},
            )
        assert resp.status_code == 401
