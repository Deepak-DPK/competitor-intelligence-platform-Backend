"""
app/database/base.py
--------------------
Declarative base for all SQLAlchemy models.

Every model file imports `Base` from here and inherits from it.
This file also re-exports the base so Alembic's env.py can do a single
import: `from app.database.base import Base`.

NOTE (Phase 2): All 16 models live under app/models/ and are imported
in app/models/__init__.py so Alembic autogenerate discovers them.
"""

from sqlalchemy.orm import DeclarativeBase, MappedColumn
from sqlalchemy import MetaData

# Naming convention for Alembic auto-generated constraint names
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    SQLAlchemy 2 declarative base shared by all application models.

    The naming convention is set here so that Alembic migrations produce
    deterministic, human-readable constraint names across all environments.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
