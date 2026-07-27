"""
app/models/project.py
---------------------
SQLAlchemy 2 model for the ``projects`` table.

Schema (from Database Design Document):
    id          UUID PK   gen_random_uuid()
    owner_id    UUID FK   → users.id
    name        TEXT      NOT NULL
    industry    TEXT
    description TEXT
    status      TEXT      (ProjectStatus enum: active | paused | archived)
    created_at  TIMESTAMPTZ NOT NULL  default now()
    updated_at  TIMESTAMPTZ NOT NULL  default now()

Indexes (from Database Design Document):
    projects(owner_id)
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ProjectStatus
from app.database.base import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project_member import ProjectMember
    from app.models.competitor import Competitor
    from app.models.alert import Alert
    from app.models.report import Report


class Project(TimestampMixin, SoftDeleteMixin, Base):
    """
    A monitoring project groups competitors and analysis under one workspace.
    Users can own multiple projects; each project has one owner.
    """

    __tablename__ = "projects"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Unique project identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="ID of the user who owns this project.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human-readable project name.",
    )
    industry: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Hotel / hospitality industry vertical (e.g. 'luxury hotels', 'OTA').",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Free-text project description.",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ProjectStatus.ACTIVE,
        server_default=ProjectStatus.ACTIVE,
        doc="Project lifecycle status: active | paused | archived.",
    )
    business_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="Resort & Hospitality",
        server_default="Resort & Hospitality",
        doc="Travel business type.",
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="United States",
        server_default="United States",
        doc="Operating country.",
    )
    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="USD",
        server_default="USD",
        doc="Base currency.",
    )
    primary_destinations: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Comma-separated primary travel destinations.",
    )
    monitoring_preferences: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="JSON string of monitoring preferences.",
    )
    workspace_settings: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="JSON string of workspace settings.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="projects",
        lazy="select",
        doc="The user who owns this project.",
    )
    members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Team members with access to this project.",
    )
    competitors: Mapped[List["Competitor"]] = relationship(
        "Competitor",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Competitors being monitored in this project.",
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Alerts generated for this project.",
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Reports generated for this project.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_projects_owner_id", "owner_id"),
        Index("ix_projects_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} owner_id={self.owner_id}>"
