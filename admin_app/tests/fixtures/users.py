import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from admin_app.store import Store
from admin_app.tg_bot.dataclasses import Chat, MessageObject, Update
from admin_app.users.models import SessionModel, UserModel, UserSession


@pytest.fixture
def update():
    return Update(message=MessageObject(chat=Chat(id_=42424242)))


@pytest.fixture
def user_request():
    return {"id_": 66666666, "first_name": "FirstName", "username": "username"}


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
async def user_1(
    db_sessionmaker: async_sessionmaker[AsyncSession], user_request: dict
):
    user = UserModel(**user_request)

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
async def game_session_with_user(
    store: Store, game_session_1: SessionModel, user_1: UserModel
):
    return await store.user.add_user_to_session_manual(user_1, game_session_1)
