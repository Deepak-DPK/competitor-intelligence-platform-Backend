"""
tests/test_projects.py
----------------------
Integration tests for the Projects CRUD API.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_create_project(client: AsyncClient, mock_user: User, auth_headers: dict):
    payload = {
        "name": "Test Hotel Project",
        "industry": "Hospitality",
        "description": "Monitoring local competitors."
    }
    response = await client.post("/api/v1/projects", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Hotel Project"
    assert data["owner_id"] == str(mock_user.id)
    assert "id" in data


async def test_list_projects(client: AsyncClient, mock_user: User, auth_headers: dict):
    # Create two projects
    await client.post("/api/v1/projects", json={"name": "Proj 1"}, headers=auth_headers)
    await client.post("/api/v1/projects", json={"name": "Proj 2"}, headers=auth_headers)

    response = await client.get("/api/v1/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [p["name"] for p in data]
    assert "Proj 1" in names
    assert "Proj 2" in names


async def test_update_project(client: AsyncClient, auth_headers: dict):
    # Create
    create_resp = await client.post("/api/v1/projects", json={"name": "Old Name"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    # Update
    update_resp = await client.patch(f"/api/v1/projects/{project_id}", json={"name": "New Name"}, headers=auth_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "New Name"


async def test_delete_project(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post("/api/v1/projects", json={"name": "To Delete"}, headers=auth_headers)
    project_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    # Ensure it's not listed anymore
    list_resp = await client.get("/api/v1/projects", headers=auth_headers)
    ids = [p["id"] for p in list_resp.json()]
    assert project_id not in ids
