"""
tests/test_health.py
--------------------
Tests for health check endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    """GET /api/v1/health should return 200 with status ok."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_liveness_response_headers(client: AsyncClient) -> None:
    """Correlation ID headers should be present in responses."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
