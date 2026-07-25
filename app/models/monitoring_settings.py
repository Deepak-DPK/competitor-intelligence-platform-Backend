"""
app/models/monitoring_settings.py
----------------------------------
SQLAlchemy 2 model for the ``monitoring_settings`` table.

Schema (from Database Design Document):
    id                   UUID PK   gen_random_uuid()
    competitor_id        UUID FK   → competitors.id  (UNIQUE — one-to-one)
    website_enabled      BOOLEAN   NOT NULL  default true
    keyword_enabled      BOOLEAN   NOT NULL  default true
    pricing_enabled      BOOLEAN   NOT NULL  default true
    social_enabled       BOOLEAN   NOT NULL  default true
    advertising_enabled  BOOLEAN   NOT NULL  default true
    scan_frequency       TEXT      (ScanFrequency enum: hourly | daily | weekly)

One-to-one with Competitor (enforced via UNIQUE constraint on competitor_id).
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ScanFrequency
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.competitor import Competitor


class MonitoringSettings(Base):
    """
    Per-competitor monitoring configuration (one-to-one).

    Fine-grained controls over which monitoring modules run and how often.
    The master switch is ``Competitor.monitoring_enabled``; these flags
    provide module-level control on top of that.
    """

    __tablename__ = "monitoring_settings"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Unique settings record identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key (one-to-one enforced by UNIQUE constraint below)
    # ------------------------------------------------------------------ #
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
        doc="Competitor these settings apply to.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    website_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="Enable website page monitoring for this competitor.",
    )
    keyword_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="Enable SEO keyword monitoring for this competitor.",
    )
    pricing_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="Enable pricing monitoring for this competitor.",
    )
    social_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="Enable social media monitoring for this competitor.",
    )
    advertising_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="Enable advertising campaign monitoring for this competitor.",
    )
    scan_frequency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ScanFrequency.DAILY,
        server_default=ScanFrequency.DAILY,
        doc="How often the monitoring pipeline runs: hourly | daily | weekly.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    competitor: Mapped["Competitor"] = relationship(
        "Competitor",
        back_populates="monitoring_settings",
        lazy="select",
        doc="The competitor these settings belong to.",
    )

    # ------------------------------------------------------------------ #
    # Table-level constraints
    # ------------------------------------------------------------------ #
    __table_args__ = (
        # Enforce one-to-one: each competitor has exactly one settings row
        UniqueConstraint(
            "competitor_id",
            name="uq_monitoring_settings_competitor_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<MonitoringSettings competitor_id={self.competitor_id} "
            f"frequency={self.scan_frequency!r}>"
        )
