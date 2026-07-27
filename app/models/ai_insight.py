"""
app/models/ai_insight.py
------------------------
SQLAlchemy 2 model for the ``ai_insights`` table.

Schema (from Database Design Document):
    id              UUID PK   gen_random_uuid()
    change_log_id   UUID FK   → change_logs.id
    summary         TEXT
    business_impact TEXT
    confidence      FLOAT     (0.0 – 1.0)
    created_at      TIMESTAMPTZ NOT NULL  default now()
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.change_log import ChangeLog
    from app.models.recommendation import Recommendation


class AIInsight(TimestampMixin, Base):
    """
    An AI-generated insight derived from a detected change.

    Gemini analyses the ChangeLog and produces a natural-language summary,
    business impact assessment, and a confidence score.  Actionable
    recommendations are stored in the ``recommendations`` child table.
    """

    __tablename__ = "ai_insights"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique insight identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    change_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("change_logs.id", ondelete="CASCADE"),
        nullable=False,
        doc="The change log entry this insight was generated from.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Gemini-generated natural-language summary of the change and its significance.",
    )
    business_impact: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Gemini-generated assessment of how this change affects the user's hotel business.",
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Model confidence score between 0.0 (low) and 1.0 (high).",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    change_log: Mapped["ChangeLog"] = relationship(
        "ChangeLog",
        back_populates="ai_insights",
        lazy="select",
        doc="The change log this insight was derived from.",
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="insight",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Actionable recommendations generated from this insight.",
    )

    # ------------------------------------------------------------------ #
    # Table-level constraints & indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        # Confidence must be between 0 and 1 (inclusive)
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)",
            name="ck_ai_insights_confidence_range",
        ),
        Index("ix_ai_insights_change_log_id", "change_log_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<AIInsight id={self.id} "
            f"change_log_id={self.change_log_id} "
            f"confidence={self.confidence}>"
        )
