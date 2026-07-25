"""
app/services/company_analysis/competitor_discovery.py
-----------------------------------------------------
Coordinates the discovery of competitors and manages suggestions.
"""

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.company_profile import CompanyProfile
from app.models.competitor_suggestion import CompetitorSuggestion
from app.services.company_analysis.search_service import SearchProvider

logger = get_logger(__name__)

class CompetitorDiscoveryService:
    def __init__(self, db: AsyncSession, search_provider: SearchProvider):
        self._db = db
        self.search_provider = search_provider

    async def run_discovery(self, profile: CompanyProfile) -> List[CompetitorSuggestion]:
        """
        Runs the discovery process for a given company profile.
        Saves the suggestions into the DB and returns them.
        """
        raw_competitors = await self.search_provider.discover_competitors(profile)
        
        suggestions = []
        for comp_data in raw_competitors:
            suggestion = CompetitorSuggestion(
                project_id=profile.project_id,
                competitor_name=comp_data.get("name", "Unknown"),
                website=comp_data.get("website"),
                confidence_score=float(comp_data.get("confidence_score", 0.5)),
                reason=comp_data.get("reason"),
            )
            self._db.add(suggestion)
            suggestions.append(suggestion)
            
        await self._db.flush()
        logger.info(f"Discovered {len(suggestions)} competitors for profile {profile.id}")
        return suggestions

    async def get_pending_suggestions(self, project_id: UUID) -> List[CompetitorSuggestion]:
        """
        Retrieves all unapproved/unrejected suggestions for a project.
        """
        stmt = select(CompetitorSuggestion).where(
            CompetitorSuggestion.project_id == project_id,
            CompetitorSuggestion.approved.is_(None)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def approve_suggestion(self, suggestion_id: UUID) -> CompetitorSuggestion:
        """Marks a suggestion as approved."""
        stmt = select(CompetitorSuggestion).where(CompetitorSuggestion.id == suggestion_id)
        result = await self._db.execute(stmt)
        suggestion = result.scalar_one_or_none()
        
        if suggestion:
            suggestion.approved = True
            await self._db.flush()
            
        return suggestion

    async def reject_suggestion(self, suggestion_id: UUID) -> CompetitorSuggestion:
        """Marks a suggestion as rejected."""
        stmt = select(CompetitorSuggestion).where(CompetitorSuggestion.id == suggestion_id)
        result = await self._db.execute(stmt)
        suggestion = result.scalar_one_or_none()
        
        if suggestion:
            suggestion.approved = False
            await self._db.flush()
            
        return suggestion
