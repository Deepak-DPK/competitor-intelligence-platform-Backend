"""
app/repositories/project.py
---------------------------
Data access layer for Projects.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = get_logger(__name__)


class ProjectRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_by_owner(self, owner_id: UUID) -> Sequence[Project]:
        """Fetch all non-deleted projects for an owner."""
        result = await self._db.execute(
            select(Project)
            .where(Project.owner_id == owner_id)
            .where(Project.deleted_at.is_(None))
            .order_by(Project.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Fetch a project by ID, ignoring deleted ones."""
        result = await self._db.execute(
            select(Project)
            .where(Project.id == project_id)
            .where(Project.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, owner_id: UUID, payload: ProjectCreate) -> Project:
        project = Project(
            owner_id=owner_id,
            name=payload.name,
            industry=payload.industry,
            description=payload.description,
        )
        self._db.add(project)
        await self._db.flush()
        await self._db.refresh(project)
        logger.info("Project created", extra={"project_id": str(project.id)})
        return project

    async def update(self, project: Project, payload: ProjectUpdate) -> Project:
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)

        self._db.add(project)
        await self._db.flush()
        await self._db.refresh(project)
        logger.info("Project updated", extra={"project_id": str(project.id)})
        return project

    async def delete(self, project: Project) -> None:
        """Soft delete the project."""
        from datetime import datetime, timezone
        project.deleted_at = datetime.now(timezone.utc)
        self._db.add(project)
        await self._db.flush()
        logger.info("Project deleted", extra={"project_id": str(project.id)})
