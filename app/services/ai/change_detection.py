"""
app/services/ai/change_detection.py
-----------------------------------
Compares a newly captured snapshot with the previous one.
If a meaningful difference is detected, generates a ChangeLog entry.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.constants import SnapshotType, ChangeType, ChangeSeverity
from app.models.change_log import ChangeLog
from app.models.website_snapshot import WebsiteSnapshot
from app.models.pricing_snapshot import PricingSnapshot
from app.models.keyword_snapshot import KeywordSnapshot
from app.models.social_snapshot import SocialSnapshot
from app.models.advertising_snapshot import AdvertisingSnapshot

logger = get_logger(__name__)


class ChangeDetectionEngine:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def _get_previous_snapshot(self, model_class, current_snapshot):
        """Fetch the immediately preceding snapshot for this competitor."""
        stmt = (
            select(model_class)
            .where(model_class.competitor_id == current_snapshot.competitor_id)
            .where(model_class.id != current_snapshot.id)
            .where(model_class.captured_at <= current_snapshot.captured_at)
            .order_by(model_class.captured_at.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def process_snapshot(self, snapshot) -> Optional[ChangeLog]:
        """Route to the correct diffing logic based on snapshot type."""
        
        change_log = None
        
        if isinstance(snapshot, WebsiteSnapshot):
            change_log = await self._detect_website_change(snapshot)
        elif isinstance(snapshot, PricingSnapshot):
            change_log = await self._detect_pricing_change(snapshot)
        elif isinstance(snapshot, KeywordSnapshot):
            change_log = await self._detect_keyword_change(snapshot)
        elif isinstance(snapshot, SocialSnapshot):
            change_log = await self._detect_social_change(snapshot)
        elif isinstance(snapshot, AdvertisingSnapshot):
            change_log = await self._detect_advertising_change(snapshot)
            
        if change_log:
            self._db.add(change_log)
            await self._db.flush()
            logger.info("Change detected and logged", extra={"change_log_id": str(change_log.id)})
            
            # Fetch the project_id associated with the competitor
            from app.models.competitor import Competitor
            stmt = select(Competitor.project_id).where(Competitor.id == snapshot.competitor_id)
            proj_result = await self._db.execute(stmt)
            project_id = proj_result.scalar_one_or_none()
            
            if project_id:
                from app.services.alert import AlertService
                alert_service = AlertService(self._db)
                await alert_service.create_alert_from_change(project_id, change_log)
            
        return change_log

    async def _detect_website_change(self, current: WebsiteSnapshot) -> Optional[ChangeLog]:
        prev = await self._get_previous_snapshot(WebsiteSnapshot, current)
        if not prev:
            return None # First snapshot, nothing to compare against
            
        if current.html_hash != prev.html_hash:
            return ChangeLog(
                competitor_id=current.competitor_id,
                snapshot_type=SnapshotType.WEBSITE,
                change_type=ChangeType.MODIFIED,
                severity=ChangeSeverity.MEDIUM,
                summary="Website HTML content changed."
            )
        return None

    async def _detect_pricing_change(self, current: PricingSnapshot) -> Optional[ChangeLog]:
        prev = await self._get_previous_snapshot(PricingSnapshot, current)
        if not prev:
            return None
            
        summary_parts = []
        severity = ChangeSeverity.LOW
        
        if current.price != prev.price:
            summary_parts.append(f"Price changed from {prev.price} to {current.price}")
            severity = ChangeSeverity.HIGH
            
        if current.offer != prev.offer:
            summary_parts.append("New promotional offer detected")
            if not summary_parts:
                severity = ChangeSeverity.MEDIUM
                
        if summary_parts:
            return ChangeLog(
                competitor_id=current.competitor_id,
                snapshot_type=SnapshotType.PRICING,
                change_type=ChangeType.MODIFIED,
                severity=severity,
                summary="; ".join(summary_parts)
            )
        return None

    async def _detect_keyword_change(self, current: KeywordSnapshot) -> Optional[ChangeLog]:
        prev = await self._get_previous_snapshot(KeywordSnapshot, current)
        if not prev:
            return None
            
        summary_parts = []
        if current.title != prev.title:
            summary_parts.append("Page title tag changed")
        if current.h1 != prev.h1:
            summary_parts.append("H1 heading changed")
            
        if summary_parts:
            return ChangeLog(
                competitor_id=current.competitor_id,
                snapshot_type=SnapshotType.KEYWORD,
                change_type=ChangeType.MODIFIED,
                severity=ChangeSeverity.MEDIUM,
                summary="; ".join(summary_parts)
            )
        return None

    async def _detect_social_change(self, current: SocialSnapshot) -> Optional[ChangeLog]:
        prev = await self._get_previous_snapshot(SocialSnapshot, current)
        if not prev:
            return None
            
        if current.engagement and prev.engagement and (current.engagement > prev.engagement * 1.5):
            return ChangeLog(
                competitor_id=current.competitor_id,
                snapshot_type=SnapshotType.SOCIAL,
                change_type=ChangeType.MODIFIED,
                severity=ChangeSeverity.HIGH,
                summary=f"Significant engagement spike detected on {current.platform}"
            )
        return None

    async def _detect_advertising_change(self, current: AdvertisingSnapshot) -> Optional[ChangeLog]:
        prev = await self._get_previous_snapshot(AdvertisingSnapshot, current)
        if not prev:
            return None
            
        if current.campaign != prev.campaign or current.cta != prev.cta:
            return ChangeLog(
                competitor_id=current.competitor_id,
                snapshot_type=SnapshotType.ADVERTISING,
                change_type=ChangeType.MODIFIED,
                severity=ChangeSeverity.HIGH,
                summary="New advertising campaign or CTA detected."
            )
        return None
