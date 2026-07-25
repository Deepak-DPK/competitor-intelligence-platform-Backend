"""
tests/test_dashboard.py
-----------------------
Tests for the Dashboard and Alerts API.
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.competitor import Competitor
from app.models.alert import Alert
from app.core.constants import AlertSeverity

pytestmark = pytest.mark.asyncio

async def test_dashboard_statistics(client: TestClient, db: AsyncSession, normal_user, get_auth_headers):
    # Create project
    proj_id = uuid4()
    proj = Project(id=proj_id, owner_id=normal_user.id, name="Test Dashboard Project")
    db.add(proj)
    
    # Create competitor
    comp = Competitor(project_id=proj_id, name="Test Comp")
    db.add(comp)
    
    # Create unread alert
    alert = Alert(project_id=proj_id, title="Test Alert", severity=AlertSeverity.INFO, is_read=False)
    db.add(alert)
    
    await db.commit()
    
    headers = await get_auth_headers(normal_user.email, "testpassword123")
    response = client.get(f"/api/v1/dashboard/statistics?project_id={proj_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_competitors"] == 1
    assert data["active_alerts"] == 1
    assert data["pending_recommendations"] == 0


async def test_alerts_api(client: TestClient, db: AsyncSession, normal_user, get_auth_headers):
    proj_id = uuid4()
    proj = Project(id=proj_id, owner_id=normal_user.id, name="Test Alerts Project")
    db.add(proj)
    
    alert = Alert(project_id=proj_id, title="Warning Alert", severity=AlertSeverity.WARNING, is_read=False)
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    headers = await get_auth_headers(normal_user.email, "testpassword123")
    
    # List alerts
    list_res = client.get(f"/api/v1/alerts/?project_id={proj_id}", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    
    # Mark as read
    patch_res = client.patch(f"/api/v1/alerts/{alert.id}/read", headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["is_read"] is True
