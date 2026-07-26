"""
app/models/website_snapshot.py
------------------------------
SQLAlchemy 2 model for the ``website_snapshots`` table.

Schema (from Database Design Document):
    id               UUID PK   gen_random_uuid()
    competitor_id    UUID FK   → competitors.id
    page_url         TEXT      NOT NULL
    html_hash        TEXT      — SHA-256 of raw HTML (change detection key)
    markdown_content TEXT      — cleaned markdown from Firecrawl Cloud API
    captured_at      TIMESTAMPTZ NOT NULL  default now()

This table is IMMUTABLE (append-only).  Never UPDATE or DELETE rows;
store monitoring history as new snapshots.

Indexes (from Database Design Document):
    website_snapshots(competitor_id, captured_at)
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


class WebsiteSnapshot(Base):
    """
    Immutable point-in-time snapshot of a competitor's web page.
    Captured by Playwright → cleaned by Firecrawl Cloud API → stored here.
    """

    __tablename__ = "website_snapshots"

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
        doc="Competitor this snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    page_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Full URL of the captured page.",
    )
    html_hash: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="SHA-256 hex digest of the raw HTML — used for fast change detection.",
    )
    markdown_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Cleaned markdown representation of the page (from Firecrawl Cloud API).",
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
        back_populates="website_snapshots",
        lazy="select",
        doc="Competitor this snapshot was captured for.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_website_snapshots_competitor_id_captured_at", "competitor_id", "captured_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<WebsiteSnapshot id={self.id} "
            f"competitor_id={self.competitor_id} "
            f"captured_at={self.captured_at}>"
        )
