"""
alembic/env.py
--------------
Alembic runtime environment for SQLAlchemy 2 async engine.

Key design decisions:
- Uses asyncio.run() to drive the async engine from synchronous Alembic CLI.
- Imports Base and all models so autogenerate can detect schema changes.
- DATABASE_URL is sourced from app.core.config (which reads .env).
"""

import asyncio
import os
import sys
from logging.config import fileConfig

# Add the root directory to PYTHONPATH so alembic can find 'app'
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ------------------------------------------------------------------ #
# Project imports
# ------------------------------------------------------------------ #
from app.core.config import settings
from app.database.base import Base

# Import all models so Alembic autogenerate can see them.
# Add new model imports here as they are created in Phase 2+.
import app.models  # noqa: F401  (registers models against Base.metadata)

# ------------------------------------------------------------------ #
# Alembic Config object (provides access to alembic.ini values)
# ------------------------------------------------------------------ #
config = context.config

# Override sqlalchemy.url from config file with the runtime value
# We replace '%' with '%%' to prevent configparser from treating password characters (like %40) as interpolation variables.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

# Interpret the config file for Python logging (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata object for autogenerate support
target_metadata = Base.metadata


# ------------------------------------------------------------------ #
# Offline migrations  (no live DB connection needed)
# ------------------------------------------------------------------ #

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — emit SQL to stdout / file without
    connecting to the database.  Useful for generating SQL scripts.
    """
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
# Online migrations  (live DB connection via async engine)
# ------------------------------------------------------------------ #

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using the async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online mode — wraps async runner in asyncio.run()."""
    asyncio.run(run_async_migrations())


# ------------------------------------------------------------------ #
# Dispatch
# ------------------------------------------------------------------ #
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
