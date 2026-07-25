"""
app/models/pricing_snapshot.py
------------------------------
SQLAlchemy 2 model for the ``pricing_snapshots`` table.

Schema (from Database Design Document):
    id            UUID PK   gen_random_uuid()
    competitor_id UUID FK   → competitors.id
    product_name  TEXT
    currency      TEXT
    price         NUMERIC(12, 2)
    offer         TEXT
    captured_at   TIMESTAMPTZ NOT NULL  default now()

IMMUTABLE — append-only table.

Indexes (from Database Design Document):
    pricing_snapshots(competitor_id, captured_at)
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.competitor import Competitor


class PricingSnapshot(Base):
    """
    Point-in-time pricing snapshot for a competitor's product or room type.
    Supports detection of price drops, offers, and rate-parity violations.
    """

    __tablename__ = "pricing_snapshots"

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
        doc="Competitor this pricing snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    product_name: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Product, room type, or package name.",
    )
    currency: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        doc="ISO 4217 currency code (e.g. 'USD', 'EUR').",
    )
    price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        doc="Captured price value with up to 2 decimal places.",
    )
    offer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Promotional offer text (e.g. '20% off — Book before July 31').",
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
        back_populates="pricing_snapshots",
        lazy="select",
        doc="Competitor this pricing snapshot belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_pricing_snapshots_competitor_id_captured_at", "competitor_id", "captured_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<PricingSnapshot id={self.id} "
            f"product={self.product_name!r} "
            f"price={self.price} {self.currency}>"
        )
