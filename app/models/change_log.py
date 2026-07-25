"""
app/models/change_log.py
------------------------
SQLAlchemy 2 model for the ``change_logs`` table.

Schema (from Database Design Document):
    id             UUID PK   gen_random_uuid()
    competitor_id  UUID FK   → competitors.id
    snapshot_type  TEXT      (SnapshotType enum)
    change_type    TEXT      (ChangeType enum)
    severity       TEXT      (ChangeSeverity enum)
    summary        TEXT
    detected_at    TIMESTAMPTZ NOT NULL  default now()

Indexes (from Database Design Document):
    change_logs(competitor_id, detected_at)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ChangeSeverity, ChangeType, SnapshotType
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.competitor import Competitor
    from app.models.ai_insight import AIInsight


class ChangeLog(Base):
    """
    Records a detected change between two consecutive snapshots.

    The change detection engine compares the current snapshot to the previous
    one and writes a ChangeLog row when a meaningful difference is found.
    AI insights are then generated from these change logs.
    """

    __tablename__ = "change_logs"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Unique change log identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
        doc="Competitor where the change was detected.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    snapshot_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Which monitoring module detected the change: website | keyword | pricing | social | advertising.",
    )
    change_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Nature of the change: added | removed | modified | unchanged.",
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ChangeSeverity.LOW,
        server_default=ChangeSeverity.LOW,
        doc="Business impact severity: low | medium | high | critical.",
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Human-readable summary of what changed.",
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="UTC timestamp when the change was detected.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    competitor: Mapped["Competitor"] = relationship(
        "Competitor",
        back_populates="change_logs",
        lazy="select",
        doc="Competitor where the change was detected.",
    )
    ai_insights: Mapped[List["AIInsight"]] = relationship(
        "AIInsight",
        back_populates="change_log",
        cascade="all, delete-orphan",
        lazy="select",
        doc="AI-generated insights derived from this change.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_change_logs_competitor_id_detected_at", "competitor_id", "detected_at"),
        Index("ix_change_logs_severity", "severity"),
        Index("ix_change_logs_snapshot_type", "snapshot_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<ChangeLog id={self.id} "
            f"type={self.change_type!r} "
            f"severity={self.severity!r} "
            f"competitor_id={self.competitor_id}>"
        )
