from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.orm_base import Base

import app.modules.chat.models  # noqa: F401
import app.modules.deals.models  # noqa: F401
import app.modules.lawyer_profiles.models  # noqa: F401
import app.modules.offers.models  # noqa: F401
import app.modules.requests.models  # noqa: F401
import app.modules.users.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.getenv("DATABASE_URL")
if database_url:
    sync_url = database_url
    if sync_url.startswith("postgresql+asyncpg://"):
        sync_url = "postgresql+psycopg://" + sync_url.removeprefix(
            "postgresql+asyncpg://"
        )
    elif sync_url.startswith("sqlite+aiosqlite:"):
        sync_url = sync_url.replace("sqlite+aiosqlite:", "sqlite:", 1)
    config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
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
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
