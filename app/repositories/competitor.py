"""
app/repositories/competitor.py
------------------------------
Data access layer for Competitors.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate

logger = get_logger(__name__)


class CompetitorRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_by_project(self, project_id: UUID) -> Sequence[Competitor]:
        """Fetch all non-deleted competitors for a given project."""
        result = await self._db.execute(
            select(Competitor)
            .where(Competitor.project_id == project_id)
            .where(Competitor.deleted_at.is_(None))
            .order_by(Competitor.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, competitor_id: UUID) -> Optional[Competitor]:
        """Fetch a single competitor by ID."""
        result = await self._db.execute(
            select(Competitor)
            .where(Competitor.id == competitor_id)
            .where(Competitor.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, payload: CompetitorCreate) -> Competitor:
        competitor = Competitor(
            project_id=payload.project_id,
            name=payload.name,
            website_url=str(payload.website_url),
            country=payload.country,
            category=payload.category,
            monitoring_enabled=payload.monitoring_enabled,
        )
        self._db.add(competitor)
        await self._db.flush()
        await self._db.refresh(competitor)
        logger.info("Competitor created", extra={"competitor_id": str(competitor.id)})
        return competitor

    async def update(self, competitor: Competitor, payload: CompetitorUpdate) -> Competitor:
        update_data = payload.model_dump(exclude_unset=True)
        if "website_url" in update_data and update_data["website_url"]:
            update_data["website_url"] = str(update_data["website_url"])

        for key, value in update_data.items():
            setattr(competitor, key, value)

        self._db.add(competitor)
        await self._db.flush()
        await self._db.refresh(competitor)
        logger.info("Competitor updated", extra={"competitor_id": str(competitor.id)})
        return competitor

    async def delete(self, competitor: Competitor) -> None:
        """Soft delete the competitor."""
        from datetime import datetime, timezone
        competitor.deleted_at = datetime.now(timezone.utc)
        self._db.add(competitor)
        await self._db.flush()
        logger.info("Competitor deleted", extra={"competitor_id": str(competitor.id)})
