"""
app/models/social_snapshot.py
------------------------------
SQLAlchemy 2 model for the ``social_snapshots`` table.

Schema (from Database Design Document):
    id            UUID PK   gen_random_uuid()
    competitor_id UUID FK   → competitors.id
    platform      TEXT      (SocialPlatform enum)
    post_title    TEXT
    post_url      TEXT
    engagement    INTEGER
    captured_at   TIMESTAMPTZ NOT NULL  default now()

IMMUTABLE — append-only table.

Indexes (from Database Design Document):
    social_snapshots(competitor_id, captured_at)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import SocialPlatform
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.competitor import Competitor


class SocialSnapshot(Base):
    """
    Point-in-time snapshot of a competitor's social media post or activity.
    Tracks engagement metrics to detect viral content or social strategy shifts.
    """

    __tablename__ = "social_snapshots"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Unique snapshot identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
        doc="Competitor this social snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    platform: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Social platform: twitter | facebook | instagram | linkedin | youtube | tiktok.",
    )
    post_title: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Title or caption of the social post.",
    )
    post_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Direct URL to the social media post.",
    )
    engagement: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Aggregate engagement count (likes + shares + comments, platform-dependent).",
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="UTC timestamp when this snapshot was captured.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    competitor: Mapped["Competitor"] = relationship(
        "Competitor",
        back_populates="social_snapshots",
        lazy="select",
        doc="Competitor this social snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_social_snapshots_competitor_id_captured_at", "competitor_id", "captured_at"),
        Index("ix_social_snapshots_platform", "platform"),
    )

    def __repr__(self) -> str:
        return (
            f"<SocialSnapshot id={self.id} "
            f"platform={self.platform!r} "
            f"competitor_id={self.competitor_id}>"
        )
