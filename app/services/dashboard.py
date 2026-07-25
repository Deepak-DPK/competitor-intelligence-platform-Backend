"""
app/services/dashboard.py
-------------------------
Service layer for aggregated Dashboard views.
"""

from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RecommendationStatus
from app.models.ai_insight import AIInsight
from app.models.alert import Alert
from app.models.change_log import ChangeLog
from app.models.competitor import Competitor
from app.models.recommendation import Recommendation
from app.schemas.dashboard import DashboardStatistics, RecentInsightResponse, TimelineEvent


from cachetools import TTLCache

# Module level cache for dashboard statistics (lives for 60 seconds)
# Key: project_id (UUID), Value: DashboardStatistics
stats_cache = TTLCache(maxsize=100, ttl=60)

class DashboardService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_statistics(self, project_id: UUID) -> DashboardStatistics:
        """Calculate high-level dashboard metrics for a project."""
        
        # Check cache first
        if project_id in stats_cache:
            return stats_cache[project_id]

        # 1. Total Competitors
        stmt_comp = select(func.count(Competitor.id)).where(Competitor.project_id == project_id)
        res_comp = await self._db.execute(stmt_comp)
        total_competitors = res_comp.scalar() or 0

        # 2. Active Alerts (unread)
        stmt_alerts = select(func.count(Alert.id)).where(
            Alert.project_id == project_id,
            Alert.is_read == False
        )
        res_alerts = await self._db.execute(stmt_alerts)
        active_alerts = res_alerts.scalar() or 0

        # 3. Pending Recommendations
        # Join Competitor -> ChangeLog -> AIInsight -> Recommendation
        stmt_rec = (
            select(func.count(Recommendation.id))
            .select_from(Recommendation)
            .join(AIInsight, Recommendation.insight_id == AIInsight.id)
            .join(ChangeLog, AIInsight.change_log_id == ChangeLog.id)
            .join(Competitor, ChangeLog.competitor_id == Competitor.id)
            .where(
                Competitor.project_id == project_id,
                Recommendation.status == RecommendationStatus.PENDING
            )
        )
        res_rec = await self._db.execute(stmt_rec)
        pending_recs = res_rec.scalar() or 0

        stats = DashboardStatistics(
            total_competitors=total_competitors,
            active_alerts=active_alerts,
            pending_recommendations=pending_recs
        )
        
        # Save to cache
        stats_cache[project_id] = stats
        return stats

    async def get_recent_insights(self, project_id: UUID, limit: int = 5) -> List[RecentInsightResponse]:
        """Fetch the most recent AI Insights for a project."""
        stmt = (
            select(AIInsight)
            .join(ChangeLog, AIInsight.change_log_id == ChangeLog.id)
            .join(Competitor, ChangeLog.competitor_id == Competitor.id)
            .where(Competitor.project_id == project_id)
            .order_by(AIInsight.created_at.desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        insights = result.scalars().all()
        
        # Map to schema
        return [
            RecentInsightResponse(
                id=i.id,
                change_log_id=i.change_log_id,
                summary=i.summary,
                business_impact=i.business_impact,
                confidence=i.confidence,
                created_at=i.created_at
            ) for i in insights
        ]

    async def get_timeline(self, project_id: UUID, limit: int = 20) -> List[TimelineEvent]:
        """Fetch a unified timeline of recent changes."""
        stmt = (
            select(ChangeLog, Competitor)
            .join(Competitor, ChangeLog.competitor_id == Competitor.id)
            .where(Competitor.project_id == project_id)
            .order_by(ChangeLog.detected_at.desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        rows = result.all()
        
        events = []
        for change_log, competitor in rows:
            events.append(TimelineEvent(
                id=change_log.id,
                snapshot_type=change_log.snapshot_type,
                change_type=change_log.change_type,
                severity=change_log.severity,
                summary=change_log.summary,
                detected_at=change_log.detected_at,
                competitor_id=competitor.id,
                competitor_name=competitor.name
            ))
            
        return events
