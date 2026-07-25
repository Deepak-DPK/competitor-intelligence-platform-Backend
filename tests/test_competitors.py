"""
tests/test_competitors.py
-------------------------
Integration tests for Competitor and MonitoringSettings CRUD.
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def sample_project(client: AsyncClient, auth_headers: dict) -> str:
    """Fixture to create a project and return its ID."""
    resp = await client.post("/api/v1/projects", json={"name": "Test Project"}, headers=auth_headers)
    return resp.json()["id"]


async def test_create_competitor(client: AsyncClient, auth_headers: dict, sample_project: str):
    payload = {
        "project_id": sample_project,
        "name": "Competitor A",
        "website_url": "https://competitor.com",
        "country": "US",
        "category": "Hotel"
    }
    response = await client.post("/api/v1/competitors", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Competitor A"
    assert data["project_id"] == sample_project
    
    # Verify monitoring settings were auto-created
    competitor_id = data["id"]
    mon_resp = await client.get(f"/api/v1/competitors/{competitor_id}/monitoring-settings", headers=auth_headers)
    assert mon_resp.status_code == 200
    mon_data = mon_resp.json()
    assert mon_data["website_enabled"] is True
    assert mon_data["scan_frequency"] == "daily"


async def test_list_competitors(client: AsyncClient, auth_headers: dict, sample_project: str):
    await client.post("/api/v1/competitors", json={"project_id": sample_project, "name": "Comp 1", "website_url": "https://a.com"}, headers=auth_headers)
    await client.post("/api/v1/competitors", json={"project_id": sample_project, "name": "Comp 2", "website_url": "https://b.com"}, headers=auth_headers)

    response = await client.get(f"/api/v1/competitors?project_id={sample_project}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2


async def test_update_monitoring_settings(client: AsyncClient, auth_headers: dict, sample_project: str):
    # Create competitor
    comp_resp = await client.post(
        "/api/v1/competitors", 
        json={"project_id": sample_project, "name": "Comp 1", "website_url": "https://a.com"}, 
        headers=auth_headers
    )
    comp_id = comp_resp.json()["id"]

    # Update settings
    payload = {"scan_frequency": "hourly", "website_enabled": False}
    update_resp = await client.patch(f"/api/v1/competitors/{comp_id}/monitoring-settings", json=payload, headers=auth_headers)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["scan_frequency"] == "hourly"
    assert data["website_enabled"] is False


async def test_delete_competitor(client: AsyncClient, auth_headers: dict, sample_project: str):
    comp_resp = await client.post(
        "/api/v1/competitors", 
        json={"project_id": sample_project, "name": "To Delete", "website_url": "https://a.com"}, 
        headers=auth_headers
    )
    comp_id = comp_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/competitors/{comp_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    list_resp = await client.get(f"/api/v1/competitors?project_id={sample_project}", headers=auth_headers)
    ids = [c["id"] for c in list_resp.json()]
    assert comp_id not in ids
