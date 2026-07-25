"""
app/services/project.py
-----------------------
Business logic layer for Projects.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.exceptions import ForbiddenException, NotFoundException


class ProjectService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._repo = ProjectRepository(db)

    async def list_projects(
        self,
        user_id: UUID,
        pagination: "PaginationParams",
        search: "SearchParams",
        sort: "SortParams",
    ) -> "PaginatedResponse[Project]":
        """List all non-deleted projects for the user with pagination."""
        from app.schemas.common import PaginatedResponse

        items, total = await self._repo.list_by_owner(user_id, pagination, search, sort)
        return PaginatedResponse(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
        )

    async def get_project(self, project_id: UUID, user_id: UUID) -> Project:
        """Get a specific project, ensuring ownership."""
        project = await self._repo.get_by_id(project_id)
        if not project:
            raise NotFoundException(detail="Project not found")
        if project.owner_id != user_id:
            raise ForbiddenException(detail="Not authorized to access this project")
        return project

    async def create_project(self, user_id: UUID, payload: ProjectCreate) -> Project:
        """Create a new project."""
        return await self._repo.create(user_id, payload)

    async def update_project(self, project_id: UUID, user_id: UUID, payload: ProjectUpdate) -> Project:
        """Update an existing project."""
        project = await self.get_project(project_id, user_id)
        return await self._repo.update(project, payload)

    async def delete_project(self, project_id: UUID, user_id: UUID) -> None:
        """Soft delete a project."""
        project = await self.get_project(project_id, user_id)
        await self._repo.delete(project)
