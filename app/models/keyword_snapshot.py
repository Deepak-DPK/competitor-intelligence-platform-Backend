"""
app/models/keyword_snapshot.py
------------------------------
SQLAlchemy 2 model for the ``keyword_snapshots`` table.

Schema (from Database Design Document):
    id               UUID PK   gen_random_uuid()
    competitor_id    UUID FK   → competitors.id
    keyword          TEXT      NOT NULL
    title            TEXT
    meta_description TEXT
    h1               TEXT
    h2               TEXT
    captured_at      TIMESTAMPTZ NOT NULL  default now()

IMMUTABLE — append-only table.

Indexes (from Database Design Document):
    keyword_snapshots(competitor_id, captured_at)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.competitor import Competitor


class KeywordSnapshot(Base):
    """
    Point-in-time SEO metadata snapshot for a given keyword and competitor.
    Tracks title, meta description, H1, H2 so changes can be detected over time.
    """

    __tablename__ = "keyword_snapshots"

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
        doc="Competitor this keyword snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    keyword: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="The search keyword or phrase being tracked.",
    )
    title: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="<title> tag content from the competitor's page for this keyword.",
    )
    meta_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="<meta name='description'> content.",
    )
    h1: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="First <h1> heading text.",
    )
    h2: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="First <h2> heading text (or concatenated H2 headings).",
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
        back_populates="keyword_snapshots",
        lazy="select",
        doc="Competitor this keyword snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_keyword_snapshots_competitor_id_captured_at", "competitor_id", "captured_at"),
        Index("ix_keyword_snapshots_keyword", "keyword"),
    )

    def __repr__(self) -> str:
        return (
            f"<KeywordSnapshot id={self.id} "
            f"keyword={self.keyword!r} "
            f"competitor_id={self.competitor_id}>"
        )
