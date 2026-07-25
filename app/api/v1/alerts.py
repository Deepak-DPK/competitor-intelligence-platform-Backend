"""
app/api/v1/alerts.py
--------------------
REST API for Alerts.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.alert import AlertResponse
from app.services.alert import AlertService
from app.services.project import ProjectService


router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    project_id: UUID,
    is_read: Optional[bool] = None,
    severity: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List alerts for a given project."""
    # Verify user has access to project
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    alert_service = AlertService(db)
    return await alert_service.get_alerts(
        project_id=project_id,
        is_read=is_read,
        severity=severity,
        limit=limit,
        offset=skip
    )


@router.patch("/{alert_id}/read", response_model=AlertResponse)
async def mark_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert as read."""
    alert_service = AlertService(db)
    
    # Needs to verify the user has access. We fetch the alert first.
    alert = await alert_service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    project_service = ProjectService(db)
    project = await project_service.get_project(alert.project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    updated_alert = await alert_service.mark_as_read(alert_id)
    return updated_alert
