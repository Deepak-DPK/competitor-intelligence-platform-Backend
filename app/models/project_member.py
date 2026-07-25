"""
app/models/project_member.py
----------------------------
SQLAlchemy 2 model for the ``project_members`` table.

Schema (from Database Design Document):
    id          UUID PK   gen_random_uuid()
    project_id  UUID FK   → projects.id
    user_id     UUID FK   → users.id
    role        TEXT      (UserRole enum: admin | member | viewer)
    invited_at  TIMESTAMPTZ NOT NULL  default now()

This is a join table with an extra ``role`` column — not a plain many-to-many
association table, hence it gets its own full model.
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import UserRole
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class ProjectMember(Base):
    """Associates a user with a project and defines their role within it."""

    __tablename__ = "project_members"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Unique membership record identifier.",
    )

    # ------------------------------------------------------------------ #
    # Foreign keys
    # ------------------------------------------------------------------ #
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        doc="Project this membership belongs to.",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="User who is a member of the project.",
    )

    # ------------------------------------------------------------------ #
    # Columns
    # ------------------------------------------------------------------ #
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=UserRole.MEMBER,
        server_default=UserRole.MEMBER,
        doc="Member's role within this project: admin | member | viewer.",
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="UTC timestamp when the user was invited to the project.",
    )

    # ------------------------------------------------------------------ #
    # Relationships
    # ------------------------------------------------------------------ #
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="members",
        lazy="select",
        doc="The project this membership is for.",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="project_memberships",
        lazy="select",
        doc="The user who holds this membership.",
    )

    # ------------------------------------------------------------------ #
    # Table-level constraints & indexes
    # ------------------------------------------------------------------ #
    __table_args__ = (
        # A user can only be a member of a given project once
        UniqueConstraint("project_id", "user_id", name="uq_project_members_project_id_user_id"),
        Index("ix_project_members_project_id", "project_id"),
        Index("ix_project_members_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<ProjectMember project_id={self.project_id} "
            f"user_id={self.user_id} role={self.role!r}>"
        )
