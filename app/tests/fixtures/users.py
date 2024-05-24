import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.tg_bot.dataclasses import (
    CallbackQueryObject,
    Chat,
    FromObject,
    MessageObject,
    Update,
)
from app.users.models import SessionModel, UserModel, UserSession


@pytest.fixture
def update():
    return Update(message=MessageObject(chat=Chat(id_=42424242)))


@pytest.fixture
def update_2():
    return Update(message=MessageObject(chat=Chat(id_=42424242)))


@pytest.fixture
def user_request():
    return {"id_": 66666666, "first_name": "FirstName", "username": "username"}


@pytest.fixture
def user_request_2():
    return {"id_": 77777777, "first_name": "Name", "username": "username2"}


@pytest.fixture
def user_session_request_1():
    return {
        "user_id": 66666666,
        "first_name": "FirstName",
        "username": "username",
        "in_game": True,
        "points": 0,
        "file_id": "file_id",
    }


@pytest.fixture
def user_session_request(user_session_request_1, game_session_1):
    return user_session_request_1 | {"session_id": game_session_1.id_}


@pytest.fixture
async def game_session_1(
    db_sessionmaker: async_sessionmaker[AsyncSession], update: Update
):
    game_session = SessionModel(
        chat_id=update.message.chat.id_,
    )
    async with db_sessionmaker() as session:
        session.add(game_session)
        await session.commit()
    return game_session


@pytest.fixture
async def game_session_2(
    db_sessionmaker: async_sessionmaker[AsyncSession], update_2: Update
):
    game_session = SessionModel(
        chat_id=update_2.message.chat.id_,
    )
    async with db_sessionmaker() as session:
        session.add(game_session)
        await session.commit()
    return game_session


@pytest.fixture
async def user_1(
    db_sessionmaker: async_sessionmaker[AsyncSession], user_request: dict
):
    user = UserModel(**user_request)

    async with db_sessionmaker() as session:
        session.add(user)
        await session.commit()
    return user


@pytest.fixture
async def user_2(
    db_sessionmaker: async_sessionmaker[AsyncSession], user_request_2: dict
):
    user = UserModel(**user_request_2)

    async with db_sessionmaker() as session:
        session.add(user)
        await session.commit()
    return user


@pytest.fixture
async def user_session_1(
    db_sessionmaker: async_sessionmaker[AsyncSession],
    user_1: UserModel,
    game_session_1: SessionModel,
):
    user_session = UserSession(
        session_id=game_session_1.id_,
        user_id=user_1.id_,
    )
    async with db_sessionmaker() as session:
        session.add(user_session)
        await session.commit()
    return user_session


@pytest.fixture
async def user_session_2(
    db_sessionmaker: async_sessionmaker[AsyncSession],
    user_2: UserModel,
    game_session_1: SessionModel,
):
    user_session = UserSession(
        session_id=game_session_1.id_,
        user_id=user_2.id_,
    )
    async with db_sessionmaker() as session:
        session.add(user_session)
        await session.commit()
    return user_session


@pytest.fixture
def update_with_callback():
    return Update(
        message=MessageObject(chat=Chat(id_=42424242)),
        callback_query=CallbackQueryObject(
            from_=FromObject(
                id_=14141414,
                is_bot=False,
                first_name="FirstName",
                username="Username",
            )
        ),
    )


@pytest.fixture
async def game_session_with_two_users(
    db_sessionmaker, game_session_1, user_1, user_2
):
    async with db_sessionmaker() as session:
        game_session = await session.scalar(
            select(SessionModel).where(SessionModel.id_ == game_session_1.id_)
        )
        game_session.users.append(user_1)
        game_session.users.append(user_2)
        return game_session


@pytest.fixture
async def game_session_with_user(db_sessionmaker, game_session_1, user_1):
    async with db_sessionmaker() as session:
        game_session = await session.scalar(
            select(SessionModel).where(SessionModel.id_ == game_session_1.id_)
        )
        game_session.users.append(user_1)
        return game_session
