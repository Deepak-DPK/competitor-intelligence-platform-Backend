"""
alembic/env.py
--------------
Alembic runtime environment.

Key design decisions:
- Uses SYNCHRONOUS psycopg driver for migrations (avoids pgbouncer asyncpg issues).
- The app itself still uses asyncpg for async performance.
- Imports Base and all models so autogenerate can detect schema changes.
- DATABASE_URL is sourced from app.core.config (which reads .env).
"""

import os
import sys
from logging.config import fileConfig

# Add the root directory to PYTHONPATH so alembic can find 'app'
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from alembic import context
from sqlalchemy import engine_from_config, pool

# ------------------------------------------------------------------ #
# Project imports
# ------------------------------------------------------------------ #
from app.core.config import settings
from app.database.base import Base

# Import all models so Alembic autogenerate can see them.
import app.models  # noqa: F401

# ------------------------------------------------------------------ #
# Build a synchronous psycopg URL from the asyncpg URL
# ------------------------------------------------------------------ #
def _get_sync_url() -> str:
    """
    Converts postgresql+asyncpg://... to postgresql+psycopg://...
    so Alembic can use the synchronous psycopg driver.
    This avoids pgbouncer DuplicatePreparedStatementError.
    """
    url = settings.DATABASE_URL
    # Replace asyncpg dialect with psycopg
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    # Handle plain postgresql:// as well
    if url.startswith("postgresql://") and "asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


SYNC_DATABASE_URL = _get_sync_url()

# ------------------------------------------------------------------ #
# Alembic Config object
# ------------------------------------------------------------------ #
config = context.config

# Override sqlalchemy.url — escape % to avoid configparser interpolation
config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL.replace("%", "%%"))

# Interpret the config file for Python logging (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata object for autogenerate support
target_metadata = Base.metadata


# ------------------------------------------------------------------ #
# Offline migrations
# ------------------------------------------------------------------ #
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------------------------ #
# Online migrations  (synchronous psycopg — no prepared stmt issues)
# ------------------------------------------------------------------ #
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------------------------------------ #
# Dispatch
# ------------------------------------------------------------------ #
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
