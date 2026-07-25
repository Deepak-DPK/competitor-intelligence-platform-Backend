"""
app/services/alert.py
---------------------
Service layer for Alerts.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AlertSeverity, ChangeSeverity
from app.models.alert import Alert
from app.models.change_log import ChangeLog


class AlertService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_alerts(
        self,
        project_id: UUID,
        is_read: Optional[bool] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Alert]:
        """Fetches alerts for a project with optional filters."""
        stmt = select(Alert).where(Alert.project_id == project_id)
        
        if is_read is not None:
            stmt = stmt.where(Alert.is_read == is_read)
        if severity is not None:
            stmt = stmt.where(Alert.severity == severity)
            
        stmt = stmt.order_by(Alert.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_alert(self, alert_id: UUID) -> Optional[Alert]:
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_as_read(self, alert_id: UUID) -> Optional[Alert]:
        """Marks an alert as read."""
        stmt = (
            update(Alert)
            .where(Alert.id == alert_id)
            .values(is_read=True)
            .returning(Alert)
        )
        result = await self._db.execute(stmt)
        alert = result.scalar_one_or_none()
        if alert:
            await self._db.commit()
        return alert

    async def create_alert_from_change(self, project_id: UUID, change_log: ChangeLog) -> Optional[Alert]:
        """Creates an alert if the change log severity warrants it."""
        if change_log.severity not in [ChangeSeverity.HIGH, ChangeSeverity.CRITICAL]:
            return None
            
        # Map ChangeSeverity to AlertSeverity
        alert_sev = AlertSeverity.CRITICAL if change_log.severity == ChangeSeverity.CRITICAL else AlertSeverity.WARNING
        
        alert = Alert(
            project_id=project_id,
            title=f"Significant Change Detected: {change_log.snapshot_type}",
            message=change_log.summary,
            severity=alert_sev,
            is_read=False
        )
        self._db.add(alert)
        await self._db.flush()
        return alert
