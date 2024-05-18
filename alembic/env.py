import asyncio
import os
from logging.config import fileConfig

import yaml
from dotenv import load_dotenv
from sqlalchemy import pool, URL, MetaData
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine, AsyncSession

from alembic import context

from app.web.config import DatabaseConfig
from app.store.database.sqlalchemy_base import BaseModel as tg_base
from admin_app.store.database.sqlalchemy_base import BaseModel as admin_base



# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

load_dotenv()

raw_config = {'database': {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB')
}}

if not raw_config['database']['host']:
    config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), '..', 'etc/config.yaml'
    )
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)


config = context.config
app_config = DatabaseConfig(**raw_config['database'])
config.set_main_option(
    'sqlalchemy.url',
    URL.create(
        drivername='postgresql+asyncpg',
        username=app_config.user,
        password=app_config.password,
        host=app_config.host,
        port=app_config.port,
        database=app_config.database,
    ).render_as_string(hide_password=False),
)

# engine = create_async_engine(
#     URL.create(
#         drivername='postgresql+asyncpg',
#         username=app_config.user,
#         password=app_config.password,
#         host=app_config.host,
#         port=app_config.port,
#         database=app_config.database,
#     ), echo=False,
#     )
#
# metadata = MetaData()
# tg_base.metadata.reflect(bind=engine, tables=metadata.tables)
# admin_base.metadata.reflect(bind=engine, tables=metadata.tables)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = admin_base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
