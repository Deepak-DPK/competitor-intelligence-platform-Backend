"""
tests/conftest.py
-----------------
Pytest fixtures shared across the test suite.

Phase 3 update:
- Added `db_session` fixture (in-memory SQLite via asyncio).
- Added `mock_user` fixture (a User ORM instance for testing protected routes).
- Added `auth_headers` fixture (Bearer token derived from a signed Supabase-style JWT).
- DB dependency override so tests never require a real PostgreSQL connection.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import jwt

from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.user import User


# ------------------------------------------------------------------ #
# In-memory SQLite async engine (no real DB needed for unit tests)
# ------------------------------------------------------------------ #

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

_TestSessionLocal = sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    """
    Create all tables in in-memory SQLite, yield a session,
    then drop everything after the test.
    """
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with _TestSessionLocal() as session:
        yield session

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ------------------------------------------------------------------ #
# Override the DB dependency — routes use the test DB session
# ------------------------------------------------------------------ #

@pytest_asyncio.fixture(autouse=True)
async def override_get_db(db_session: AsyncSession):
    """
    Replace the real get_db dependency with the in-memory test session.
    Runs for every test automatically (autouse=True).
    """
    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


# ------------------------------------------------------------------ #
# HTTP test client
# ------------------------------------------------------------------ #

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Async test client for integration tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ------------------------------------------------------------------ #
# Mock User fixture
# ------------------------------------------------------------------ #

@pytest.fixture
def mock_user_id():
    return uuid4()


@pytest_asyncio.fixture
async def mock_user(db_session: AsyncSession, mock_user_id) -> User:
    """
    Insert a real User row into the in-memory DB for auth-protected route tests.
    """
    from datetime import datetime, timezone
    user = User(
        id=mock_user_id,
        email="testuser@example.com",
        full_name="Test User",
        role="member",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ------------------------------------------------------------------ #
# JWT token fixture (Supabase-style — signed with SUPABASE_JWT_SECRET)
# ------------------------------------------------------------------ #

@pytest.fixture
def valid_access_token(mock_user_id) -> str:
    """
    Generate a Supabase-style JWT signed with SUPABASE_JWT_SECRET.
    verify_supabase_jwt() will accept this in tests.
    """
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": str(mock_user_id),
        "email": "testuser@example.com",
        "role": "member",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(tz=timezone.utc),
    }
    return jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")


@pytest.fixture
def auth_headers(valid_access_token: str) -> dict:
    """HTTP headers with a valid Bearer token."""
    return {"Authorization": f"Bearer {valid_access_token}"}


@pytest.fixture
def expired_access_token(mock_user_id) -> str:
    """Generate an already-expired JWT for negative tests."""
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": str(mock_user_id),
        "exp": datetime.now(tz=timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(tz=timezone.utc) - timedelta(hours=2),
    }
    return jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
