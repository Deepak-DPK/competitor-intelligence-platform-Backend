"""
app/models/recommendation.py
-----------------------------
SQLAlchemy 2 model for the ``recommendations`` table.

Schema (from Database Design Document):
    id              UUID PK   gen_random_uuid()
    insight_id      UUID FK   → ai_insights.id
    recommendation  TEXT
    priority        TEXT      (RecommendationPriority enum: low | medium | high)
    status          TEXT      (RecommendationStatus enum: pending | in_progress | done | dismissed)
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import RecommendationPriority, RecommendationStatus
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.ai_insight import AIInsight


class Recommendation(Base):
    """
    An actionable recommendation derived from an AI insight.

    Users can track the lifecycle of each recommendation
    (pending → in_progress → done | dismissed).
    """

    __tablename__ = "recommendations"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique recommendation identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    insight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_insights.id", ondelete="CASCADE"),
        nullable=False,
        doc="AI insight this recommendation was generated from.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    recommendation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Natural-language action the user should consider taking.",
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=RecommendationPriority.MEDIUM,
        server_default=RecommendationPriority.MEDIUM,
        doc="Urgency level: low | medium | high.",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=RecommendationStatus.PENDING,
        server_default=RecommendationStatus.PENDING,
        doc="Workflow status: pending | in_progress | done | dismissed.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    insight: Mapped["AIInsight"] = relationship(
        "AIInsight",
        back_populates="recommendations",
        lazy="select",
        doc="The AI insight this recommendation is derived from.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_recommendations_insight_id", "insight_id"),
        Index("ix_recommendations_status", "status"),
        Index("ix_recommendations_priority", "priority"),
    )

    def __repr__(self) -> str:
        return (
            f"<Recommendation id={self.id} "
            f"priority={self.priority!r} "
            f"status={self.status!r}>"
        )
