"""
app/models/activity_log.py
---------------------------
SQLAlchemy 2 model for the ``activity_logs`` table.

Schema (from Database Design Document):
    id          UUID PK   gen_random_uuid()
    user_id     UUID FK   → users.id
    action      TEXT      NOT NULL
    entity      TEXT
    entity_id   TEXT
    created_at  TIMESTAMPTZ NOT NULL  default now()

Append-only audit trail — never updated or deleted.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ActivityLog(Base):
    """
    Immutable audit log recording every significant user action.

    Examples:
        action="project.created", entity="project", entity_id="<uuid>"
        action="competitor.deleted", entity="competitor", entity_id="<uuid>"
        action="report.generated", entity="report", entity_id="<uuid>"
    """

    __tablename__ = "activity_logs"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique activity log identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign key
    # ------------------------------------------------------------------ #
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="User who performed the action.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Action performed (e.g. 'project.created', 'competitor.deleted').",
    )
    entity: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Entity type affected (e.g. 'project', 'competitor', 'report').",
    )
    entity_id: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Identifier of the affected entity (stored as text to support any PK type).",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="UTC timestamp when the action was performed.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    user: Mapped["User"] = relationship(
        "User",
        back_populates="activity_logs",
        lazy="select",
        doc="User who performed this action.",
    )

    # ------------------------------------------------------------------ #
    # Table-level indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_activity_logs_user_id", "user_id"),
        Index("ix_activity_logs_entity", "entity"),
        Index("ix_activity_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<ActivityLog id={self.id} "
            f"action={self.action!r} "
            f"user_id={self.user_id}>"
        )
