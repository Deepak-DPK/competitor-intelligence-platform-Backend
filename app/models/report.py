"""
app/models/report.py
--------------------
SQLAlchemy 2 model for the ``reports`` table.

Schema (from Database Design Document):
    id           UUID PK   gen_random_uuid()
    project_id   UUID FK   → projects.id
    report_type  TEXT      (ReportType enum: weekly | monthly | custom | on_demand)
    report_url   TEXT
    generated_at TIMESTAMPTZ NOT NULL  default now()

Indexes (from Database Design Document):
    reports(project_id)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ReportType
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.project import Project


class Report(Base):
    """
    A generated report for a project.

    Reports are stored as URLs pointing to Supabase Storage objects
    (PDF or JSON exports).  The report_url is populated after the
    report generation service completes.
    """

    __tablename__ = "reports"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Unique report identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        doc="Project this report was generated for.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    report_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        doc="Type of report: weekly | monthly | custom | on_demand.",
    )
    report_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Supabase Storage URL for the generated report file (PDF / JSON).",
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="UTC timestamp when this report was generated.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="reports",
        lazy="select",
        doc="Project this report belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_reports_project_id", "project_id"),
        Index("ix_reports_report_type", "report_type"),
        Index("ix_reports_generated_at", "generated_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Report id={self.id} "
            f"type={self.report_type!r} "
            f"project_id={self.project_id}>"
        )
