"""
app/repositories/monitoring_settings.py
---------------------------------------
Data access layer for Monitoring Settings.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.monitoring_settings import MonitoringSettings
from app.schemas.monitoring_settings import MonitoringSettingsUpdate

logger = get_logger(__name__)


class MonitoringSettingsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_competitor_id(self, competitor_id: UUID) -> Optional[MonitoringSettings]:
        result = await self._db.execute(
            select(MonitoringSettings).where(MonitoringSettings.competitor_id == competitor_id)
        )
        return result.scalar_one_or_none()

    async def create_default(self, competitor_id: UUID) -> MonitoringSettings:
        """Create default monitoring settings for a newly created competitor."""
        settings = MonitoringSettings(competitor_id=competitor_id)
        self._db.add(settings)
        await self._db.flush()
        await self._db.refresh(settings)
        logger.info("Default monitoring settings created", extra={"competitor_id": str(competitor_id)})
        return settings

    async def update(self, settings: MonitoringSettings, payload: MonitoringSettingsUpdate) -> MonitoringSettings:
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(settings, key, value)

        self._db.add(settings)
        await self._db.flush()
        await self._db.refresh(settings)
        logger.info("Monitoring settings updated", extra={"competitor_id": str(settings.competitor_id)})
        return settings
