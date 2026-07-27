"""
app/models/company_profile.py
-----------------------------
SQLAlchemy 2 model for the ``company_profiles`` table.
Stores AI-extracted data about a company's website.
"""

import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import JSON, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project


class CompanyProfile(TimestampMixin, Base):
    """
    Stores AI-extracted data about a company's website.
    Used as the basis for discovering competitors.
    """

    __tablename__ = "company_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier.",
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        doc="The project this company profile belongs to.",
    )

    website: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="The URL of the company website.",
    )

    company_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="AI-extracted company name.",
    )

    industry: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="AI-extracted industry.",
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="AI-extracted business category.",
    )

    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="AI-generated business summary.",
    )

    keywords: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="JSON array of important keywords, products, or target audiences.",
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        lazy="select",
        doc="The parent project.",
    )

    def __repr__(self) -> str:
        return f"<CompanyProfile id={self.id} company_name={self.company_name!r}>"
