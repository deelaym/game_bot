from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.store.database.sqlalchemy_base import BaseModel


class Database:
    def __init__(self, app) -> None:
        self.app = app
        self.engine: AsyncEngine | None = None
        self._db: type[DeclarativeBase] = BaseModel
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, *args, **kwargs) -> None:
        db_info = self.app.config.database
        self.engine = create_async_engine(
            URL.create(
                "postgresql+asyncpg",
                db_info.user,
                db_info.password,
                db_info.host,
                db_info.port,
                db_info.database,
            ),
            echo=True,
        )

        self.session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autocommit=False,
        )

    async def disconnect(self, *args, **kwargs) -> None:
        try:
            await self.engine.dispose()
        except Exception:
            pass
