"""
tests/conftest.py
-----------------
Pytest fixtures shared across the test suite.

Phase 1 fixtures:
- `client`    — AsyncClient wired to the FastAPI test app
- `test_app`  — isolated FastAPI app instance for tests
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Async test client for integration tests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
