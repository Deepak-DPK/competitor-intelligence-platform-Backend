"""
app/models/competitor.py
------------------------
SQLAlchemy 2 model for the ``competitors`` table.

Schema (from Database Design Document):
    id                  UUID PK   gen_random_uuid()
    project_id          UUID FK   → projects.id
    name                TEXT      NOT NULL
    website_url         TEXT      NOT NULL
    country             TEXT
    category            TEXT
    monitoring_enabled  BOOLEAN   NOT NULL  default true
    created_at          TIMESTAMPTZ NOT NULL  default now()
    updated_at          TIMESTAMPTZ NOT NULL  default now()

Indexes (from Database Design Document):
    competitors(project_id)
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.website_snapshot import WebsiteSnapshot
    from app.models.keyword_snapshot import KeywordSnapshot
    from app.models.pricing_snapshot import PricingSnapshot
    from app.models.social_snapshot import SocialSnapshot
    from app.models.advertising_snapshot import AdvertisingSnapshot
    from app.models.monitoring_settings import MonitoringSettings
    from app.models.change_log import ChangeLog


class Competitor(TimestampMixin, SoftDeleteMixin, Base):
    """
    A competitor entity inside a project.
    Each competitor is the central node that all snapshot and monitoring
    tables point back to.
    """

    __tablename__ = "competitors"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Unique competitor identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        doc="Project this competitor belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Competitor's display name.",
    )
    website_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Base URL of the competitor's website.",
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Country where the competitor primarily operates (ISO 3166-1 alpha-2 or full name).",
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Business category / vertical (e.g. 'luxury hotel', 'budget OTA').",
    )
    monitoring_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="Master switch — if False no monitoring runs for this competitor.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="competitors",
        lazy="select",
        doc="Parent project.",
    )
    website_snapshots: Mapped[List["WebsiteSnapshot"]] = relationship(
        "WebsiteSnapshot",
        back_populates="competitor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Historical website page snapshots.",
    )
    keyword_snapshots: Mapped[List["KeywordSnapshot"]] = relationship(
        "KeywordSnapshot",
        back_populates="competitor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Historical SEO keyword snapshots.",
    )
    pricing_snapshots: Mapped[List["PricingSnapshot"]] = relationship(
        "PricingSnapshot",
        back_populates="competitor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Historical pricing snapshots.",
    )
    social_snapshots: Mapped[List["SocialSnapshot"]] = relationship(
        "SocialSnapshot",
        back_populates="competitor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Historical social media snapshots.",
    )
    advertising_snapshots: Mapped[List["AdvertisingSnapshot"]] = relationship(
        "AdvertisingSnapshot",
        back_populates="competitor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Historical advertising campaign snapshots.",
    )
    monitoring_settings: Mapped[Optional["MonitoringSettings"]] = relationship(
        "MonitoringSettings",
        back_populates="competitor",
        cascade="all, delete-orphan",
        uselist=False,        # one-to-one
        lazy="select",
        doc="Per-competitor monitoring configuration (one-to-one).",
    )
    change_logs: Mapped[List["ChangeLog"]] = relationship(
        "ChangeLog",
        back_populates="competitor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Detected changes for this competitor.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_competitors_project_id", "project_id"),
        Index("ix_competitors_monitoring_enabled", "monitoring_enabled"),
    )

    def __repr__(self) -> str:
        return f"<Competitor id={self.id} name={self.name!r} project_id={self.project_id}>"
