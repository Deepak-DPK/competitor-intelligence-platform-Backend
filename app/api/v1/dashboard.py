"""
app/api/v1/dashboard.py
-----------------------
REST API for Dashboard aggregations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStatistics, RecentInsightResponse, TimelineEvent
from app.services.dashboard import DashboardService
from app.services.project import ProjectService


router = APIRouter()


async def verify_project_access(project_id: UUID, current_user: User, db: AsyncSession):
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/statistics", response_model=DashboardStatistics)
async def get_statistics(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get high-level aggregated statistics for the dashboard."""
    await verify_project_access(project_id, current_user, db)
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_statistics(project_id)


@router.get("/recent-insights", response_model=List[RecentInsightResponse])
async def get_recent_insights(
    project_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recent AI insights."""
    await verify_project_access(project_id, current_user, db)
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_recent_insights(project_id, limit)


@router.get("/timeline", response_model=List[TimelineEvent])
async def get_timeline(
    project_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a unified timeline of recent competitor changes."""
    await verify_project_access(project_id, current_user, db)
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_timeline(project_id, limit)
