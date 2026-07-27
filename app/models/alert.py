"""
app/models/alert.py
-------------------
SQLAlchemy 2 model for the ``alerts`` table.

Schema (from Database Design Document):
    id          UUID PK   gen_random_uuid()
    project_id  UUID FK   → projects.id
    title       TEXT      NOT NULL
    message     TEXT
    severity    TEXT      (AlertSeverity enum: info | warning | critical)
    is_read     BOOLEAN   NOT NULL  default false
    created_at  TIMESTAMPTZ NOT NULL  default now()

Indexes (from Database Design Document):
    alerts(project_id)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import AlertSeverity
from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project


class Alert(TimestampMixin, Base):
    """
    A user-facing alert generated when a significant change is detected.

    Alerts are project-scoped and support read/unread state to power
    notification badges and alert centres in the dashboard.
    """

    __tablename__ = "alerts"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique alert identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        doc="Project this alert belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Short descriptive title for the alert.",
    )
    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed alert message shown to the user.",
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AlertSeverity.INFO,
        server_default=AlertSeverity.INFO,
        doc="Alert severity: info | warning | critical.",
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        doc="Whether the alert has been read by the user.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="alerts",
        lazy="select",
        doc="Project this alert belongs to.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_alerts_project_id", "project_id"),
        Index("ix_alerts_is_read", "is_read"),
        Index("ix_alerts_severity", "severity"),
        # Composite index for the most common query: unread alerts for a project
        Index("ix_alerts_project_id_is_read", "project_id", "is_read"),
    )

    def __repr__(self) -> str:
        return (
            f"<Alert id={self.id} "
            f"severity={self.severity!r} "
            f"is_read={self.is_read} "
            f"project_id={self.project_id}>"
        )
