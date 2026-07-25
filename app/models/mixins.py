"""
app/models/mixins.py
--------------------
Reusable SQLAlchemy 2 column mixins.

Design:
- TimestampMixin  — adds created_at + updated_at TIMESTAMPTZ columns.
- SoftDeleteMixin — adds deleted_at TIMESTAMPTZ for soft-delete support.

All models that need timestamps simply inherit these mixins alongside Base.
The `onupdate` hook on updated_at fires automatically on every UPDATE,
so service code never needs to set it manually.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Adds ``created_at`` and ``updated_at`` columns (TIMESTAMPTZ) to any model.

    - ``created_at``: set once on INSERT via server_default=func.now().
    - ``updated_at``: auto-updated on every UPDATE via onupdate=func.now().
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="UTC timestamp of row creation.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="UTC timestamp of last update.",
    )


class SoftDeleteMixin:
    """
    Adds a ``deleted_at`` column for soft-delete semantics.

    When ``deleted_at`` is non-NULL the row is considered logically deleted.
    Queries in repositories must filter ``Model.deleted_at.is_(None)``
    unless explicitly requesting deleted records.
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="UTC timestamp of soft-deletion; NULL means the record is active.",
    )
