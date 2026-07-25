"""
app/services/monitoring_settings.py
-----------------------------------
Business logic layer for Monitoring Settings.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitoring_settings import MonitoringSettings
from app.repositories.monitoring_settings import MonitoringSettingsRepository
from app.schemas.monitoring_settings import MonitoringSettingsUpdate
from app.services.competitor import CompetitorService


class MonitoringSettingsService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._repo = MonitoringSettingsRepository(db)
        self._competitor_svc = CompetitorService(db)

    async def get_monitoring_settings(self, competitor_id: UUID, user_id: UUID) -> MonitoringSettings:
        """Get monitoring settings for a competitor."""
        # Verify ownership via CompetitorService
        await self._competitor_svc.get_competitor(competitor_id, user_id)
        
        settings = await self._repo.get_by_competitor_id(competitor_id)
        if not settings:
            # Fallback in case settings were somehow not created
            settings = await self._repo.create_default(competitor_id)
        return settings

    async def update_monitoring_settings(self, competitor_id: UUID, payload: MonitoringSettingsUpdate, user_id: UUID) -> MonitoringSettings:
        """Update monitoring settings for a competitor."""
        settings = await self.get_monitoring_settings(competitor_id, user_id)
        return await self._repo.update(settings, payload)
