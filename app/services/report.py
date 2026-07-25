"""
app/services/report.py
----------------------
Service layer for Reports.
"""

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report


class ReportService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_reports(
        self,
        project_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Report]:
        """Fetches generated reports for a project."""
        stmt = (
            select(Report)
            .where(Report.project_id == project_id)
            .order_by(Report.generated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def generate_report(self, project_id: UUID, report_type: str) -> Report:
        """
        Creates a new Report record.
        In a full production scenario, this would trigger a background task 
        to build a PDF and upload to Supabase Storage, then set report_url.
        """
        report = Report(
            project_id=project_id,
            report_type=report_type,
            # Placeholder until PDF generation is implemented
            report_url=f"https://supabase.co/storage/v1/object/public/reports/{project_id}_{report_type}.pdf"
        )
        self._db.add(report)
        await self._db.commit()
        await self._db.refresh(report)
        return report
