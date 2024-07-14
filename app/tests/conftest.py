import asyncio
import logging
import os
from collections.abc import Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.store import Store
from app.store.database.database import Database
from app.web.app import Application, setup_app
from app.web.config import Config

from .fixtures import *  # noqa: F403


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app() -> Application:
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "config.yaml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    app.on_cleanup.clear()

    app.database = Database(app)
    await app.database.connect()
    await app.store.tg_bot.connect(app)

    app.on_shutdown.append(app.database.disconnect)
    app.on_shutdown.append(app.store.tg_bot.disconnect)
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
