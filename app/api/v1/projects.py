"""
app/api/v1/projects.py
----------------------
API router for Project CRUD operations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUserId
from app.database.session import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import ProjectService


router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    user_id: CurrentUserId,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Create a new project."""
    return await service.create_project(user_id, payload)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user_id: CurrentUserId,
    service: ProjectService = Depends(get_project_service),
) -> List[ProjectResponse]:
    """List all non-deleted projects owned by the user."""
    return await service.list_projects(user_id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    user_id: CurrentUserId,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Get details of a specific project."""
    return await service.get_project(project_id, user_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    user_id: CurrentUserId,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Update a specific project."""
    return await service.update_project(project_id, user_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    user_id: CurrentUserId,
    service: ProjectService = Depends(get_project_service),
) -> None:
    """Soft delete a specific project."""
    await service.delete_project(project_id, user_id)
