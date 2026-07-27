"""
app/models/competitor_suggestion.py
-----------------------------------
SQLAlchemy 2 model for the ``competitor_suggestions`` table.
Stores AI-suggested competitors waiting for user approval.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project


class CompetitorSuggestion(TimestampMixin, Base):
    """
    Stores AI-suggested competitors waiting for user approval.
    """

    __tablename__ = "competitor_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier.",
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        doc="The project this suggestion belongs to.",
    )

    competitor_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Suggested competitor name.",
    )

    website: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Suggested competitor website.",
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
        doc="AI confidence score for this suggestion.",
    )

    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="AI reason for suggesting this competitor.",
    )

    approved: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        doc="Approval status. True = Approved, False = Rejected, Null = Pending.",
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        lazy="select",
        doc="The parent project.",
    )

    def __repr__(self) -> str:
        return f"<CompetitorSuggestion id={self.id} name={self.competitor_name!r}>"
