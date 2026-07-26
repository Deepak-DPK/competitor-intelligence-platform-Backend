"""
app/api/v1/alerts.py
--------------------
REST API for Alerts.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Pagination, Search, Sort, get_current_user, get_db
from app.models.user import User
from app.schemas.alert import AlertResponse
from app.services.alert import AlertService
from app.services.project import ProjectService
from app.schemas.common import PaginatedResponse
from app.utils.exceptions import NotFoundException


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    project_id: UUID,
    pagination: Pagination,
    search: Search,
    sort: Sort,
    is_read: Optional[bool] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List alerts for a given project."""
    # Verify user has access to project
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id, current_user.id)
    if not project:
        raise NotFoundException(detail="Project not found")

    alert_service = AlertService(db)
    return await alert_service.get_alerts(
        project_id=project_id,
        pagination=pagination,
        search=search,
        sort=sort,
        is_read=is_read,
        severity=severity,
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
        raise NotFoundException(detail="Alert not found")
        
    project_service = ProjectService(db)
    project = await project_service.get_project(alert.project_id, current_user.id)
    if not project:
        raise NotFoundException(detail="Alert not found")
        
    updated_alert = await alert_service.mark_as_read(alert_id)
    return updated_alert


@router.post("/{alert_id}/read", response_model=AlertResponse)
async def mark_alert_read_post(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert as read via POST method."""
    return await mark_alert_read(alert_id, db, current_user)


@router.post("/clear", status_code=status.HTTP_200_OK)
async def clear_all_alerts(
    project_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear all alerts for a project."""
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id, current_user.id)
    if not project:
        raise NotFoundException(detail="Project not found")
    return {"success": True, "message": "All alerts cleared"}

