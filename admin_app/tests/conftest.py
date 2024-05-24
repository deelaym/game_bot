import logging
import os
from asyncio import AbstractEventLoop
from collections.abc import Iterator

import pytest
from aiohttp.pytest_plugin import AiohttpClient
from aiohttp.test_utils import TestClient, loop_context
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from admin_app.store.database.database import Database
from admin_app.web.admin_app import Application, setup_app
from admin_app.web.config import Config
from app.store import Store

from .fixtures import *  # noqa: F403


@pytest.fixture(scope="session")
def event_loop() -> Iterator[None]:
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(scope="session")
def app() -> Application:
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "config.yaml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    app.on_cleanup.clear()

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_startup.append(app.store.admin.connect)

    app.on_shutdown.append(app.database.disconnect)
    app.on_shutdown.append(app.store.admin.disconnect)
    return app


@pytest.fixture
def store(app: Application) -> Store:
    return app.store


@pytest.fixture
def db_sessionmaker(app: Application) -> async_sessionmaker[AsyncSession]:
    return app.database.session


@pytest.fixture
def db_engine(app: Application) -> AsyncEngine:
    return app.database.engine


@pytest.fixture
def config(app: Application) -> Config:
    return app.config


@pytest.fixture
async def inspect_list_tables(db_engine: AsyncEngine) -> list[str]:
    def use_inspector(connection: AsyncConnection) -> list[str]:
        inspector = inspect(connection)
        return inspector.get_table_names()

    async with db_engine.begin() as conn:
        return await conn.run_sync(use_inspector)


@pytest.fixture(autouse=True)
async def clear_db(app: Application) -> Iterator[None]:
    try:
        yield
    except Exception as err:
        logging.warning(err)
    finally:
        session = AsyncSession(app.database.engine)
        connection = session.connection()
        for table in app.database._db.metadata.tables:
            await session.execute(text(f"TRUNCATE {table} CASCADE"))
            await session.execute(
                text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1")
            )

        await session.commit()
        connection.close()


@pytest.fixture(autouse=True)
def cli(
    aiohttp_client: AiohttpClient,
    event_loop: AbstractEventLoop,
    app: Application,
) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
async def auth_cli(cli: TestClient, config: Config) -> TestClient:
    await cli.post(
        path="/admin.login",
        json={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    return cli
