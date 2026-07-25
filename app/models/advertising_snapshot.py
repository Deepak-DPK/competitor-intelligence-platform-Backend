"""
app/models/advertising_snapshot.py
-----------------------------------
SQLAlchemy 2 model for the ``advertising_snapshots`` table.

Schema (from Database Design Document):
    id            UUID PK   gen_random_uuid()
    competitor_id UUID FK   → competitors.id
    campaign      TEXT
    landing_page  TEXT
    cta           TEXT
    captured_at   TIMESTAMPTZ NOT NULL  default now()

IMMUTABLE — append-only table.

Indexes (from Database Design Document):
    advertising_snapshots(competitor_id, captured_at)
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


class AdvertisingSnapshot(Base):
    """
    Point-in-time snapshot of a competitor's advertising campaign.
    Captures the campaign name, landing page, and call-to-action text
    to detect changes in ad strategy.
    """

    __tablename__ = "advertising_snapshots"

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
        doc="Competitor this advertising snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    campaign: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Name or identifier of the advertising campaign.",
    )
    landing_page: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="URL of the campaign's landing page.",
    )
    cta: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Call-to-action text observed in the ad or landing page.",
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
        back_populates="advertising_snapshots",
        lazy="select",
        doc="Competitor this advertising snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index(
            "ix_advertising_snapshots_competitor_id_captured_at",
            "competitor_id",
            "captured_at",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AdvertisingSnapshot id={self.id} "
            f"campaign={self.campaign!r} "
            f"competitor_id={self.competitor_id}>"
        )
