import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.base import Base
from app.infrastructure.config.normalizer import normalize_database_url

# Import ALL model files so Alembic's autogenerate detects table metadata
from app.adapters.persistence.models.ats_model import ATSScoreModel  # noqa: F401,F403
from app.adapters.persistence.models.career_profile_model import CareerProfileModel  # noqa: F401,F403
from app.adapters.persistence.models.job_model import JobModel  # noqa: F401,F403
from app.adapters.persistence.models.resume_model import ResumeModel  # noqa: F401,F403
from app.adapters.persistence.models.user_model import UserModel  # noqa: F401,F403



config = context.config
_settings = get_settings()
config.set_main_option("sqlalchemy.url", normalize_database_url(_settings.database_url))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
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
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    def do_run_migrations(connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    async def do_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    asyncio.run(do_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
