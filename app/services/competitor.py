"""
app/services/competitor.py
--------------------------
Business logic layer for Competitors.
"""

from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import Competitor
from app.repositories.competitor import CompetitorRepository
from app.repositories.monitoring_settings import MonitoringSettingsRepository
from app.services.project import ProjectService
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate


class CompetitorService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._repo = CompetitorRepository(db)
        self._monitoring_repo = MonitoringSettingsRepository(db)
        self._project_svc = ProjectService(db)

    async def list_competitors(self, project_id: UUID, user_id: UUID) -> Sequence[Competitor]:
        """List competitors for a project, verifying project ownership."""
        # This will raise 404/403 if project doesn't exist or isn't owned by user
        await self._project_svc.get_project(project_id, user_id)
        return await self._repo.list_by_project(project_id)

    async def get_competitor(self, competitor_id: UUID, user_id: UUID) -> Competitor:
        """Get a specific competitor, verifying its parent project ownership."""
        competitor = await self._repo.get_by_id(competitor_id)
        if not competitor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competitor not found")
        # Verify ownership
        await self._project_svc.get_project(competitor.project_id, user_id)
        return competitor

    async def create_competitor(self, payload: CompetitorCreate, user_id: UUID) -> Competitor:
        """Create a competitor and automatically create default monitoring settings."""
        # Verify ownership of the project
        await self._project_svc.get_project(payload.project_id, user_id)
        
        competitor = await self._repo.create(payload)
        # Create default monitoring settings immediately
        await self._monitoring_repo.create_default(competitor.id)
        return competitor

    async def update_competitor(self, competitor_id: UUID, payload: CompetitorUpdate, user_id: UUID) -> Competitor:
        """Update a competitor."""
        competitor = await self.get_competitor(competitor_id, user_id)
        return await self._repo.update(competitor, payload)

    async def delete_competitor(self, competitor_id: UUID, user_id: UUID) -> None:
        """Soft delete a competitor."""
        competitor = await self.get_competitor(competitor_id, user_id)
        await self._repo.delete(competitor)
