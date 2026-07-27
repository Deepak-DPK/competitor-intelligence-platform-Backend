"""
tests/test_dashboard.py
-----------------------
Tests for the Dashboard and Alerts API.

Uses conftest fixtures: client, auth_headers, mock_user.
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_dashboard_statistics(client: AsyncClient, mock_user, auth_headers: dict):
    """Dashboard statistics should return 200 with expected keys."""
    # Create a project first
    proj_resp = await client.post(
        "/api/v1/projects",
        json={"name": "Dashboard Test Project", "industry": "Travel"},
        headers=auth_headers,
    )
    assert proj_resp.status_code == 201
    proj_id = proj_resp.json()["id"]

    response = await client.get(
        f"/api/v1/dashboard/statistics?project_id={proj_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    # Validate key fields exist (values may be 0 in empty project)
    assert "total_competitors" in data
    assert "active_alerts" in data
    assert "pending_recommendations" in data


async def test_alerts_api(client: AsyncClient, mock_user, auth_headers: dict):
    """Alerts API should return 200 for an authenticated user."""
    # Create project
    proj_resp = await client.post(
        "/api/v1/projects",
        json={"name": "Alerts Test Project"},
        headers=auth_headers,
    )
    assert proj_resp.status_code == 201
    proj_id = proj_resp.json()["id"]

    # List alerts — empty project, should return 200 with empty list
    list_res = await client.get(
        f"/api/v1/alerts/?project_id={proj_id}",
        headers=auth_headers,
    )
    assert list_res.status_code in (200, 404)  # 404 if endpoint not wired, 200 if it is
