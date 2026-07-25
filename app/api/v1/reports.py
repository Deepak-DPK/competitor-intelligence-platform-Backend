"""
app/api/v1/reports.py
---------------------
REST API for Reports.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.report import ReportResponse, ReportCreate
from app.services.report import ReportService
from app.services.project import ProjectService


router = APIRouter()


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    project_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List generated reports for a project."""
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    report_service = ReportService(db)
    return await report_service.get_reports(
        project_id=project_id,
        limit=limit,
        offset=skip
    )


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger the generation of a new report."""
    project_service = ProjectService(db)
    project = await project_service.get_project(data.project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    report_service = ReportService(db)
    return await report_service.generate_report(data.project_id, data.report_type)
