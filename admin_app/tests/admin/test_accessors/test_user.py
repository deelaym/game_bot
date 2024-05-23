from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from admin_app.store import Store
from admin_app.tg_bot.dataclasses import Update
from admin_app.users.models import SessionModel, UserModel, UserSession
from admin_app.tests.utils import session_to_dict, user_to_dict, user_session_to_dict


class TestUserAccessor:
    async def test_table_exists(self, inspect_list_tables: list[str]):
        assert "users" in inspect_list_tables
        assert "sessions" in inspect_list_tables
        assert "user_session" in inspect_list_tables

    async def test_create_new_session(self, store: Store, update: Update):
        game_session = await store.user.create_new_session(update)

        assert isinstance(game_session, SessionModel)
        assert session_to_dict(game_session) == {
            "id_": game_session.id_,
            "chat_id": update.message.chat.id_,
            "in_progress": True,
            "round_number": 1,
            "state": "start",
            "message_id": None,
            "polls_time": 60
        }

    async def test_create_new_user(self, store: Store, user_request: dict):
        user = await store.user.create_user(**user_request)

        assert isinstance(user, UserModel)
        assert user_to_dict(user) == user_request

    async def test_get_game_session_by_id(self, store:Store, game_session_1: SessionModel):
        game_session = await store.user.get_game_session_by_id(game_session_1.id_)

        assert session_to_dict(game_session) == {
            "id_": game_session.id_,
            "chat_id": game_session.chat_id,
            "in_progress": game_session.in_progress,
            "round_number": game_session.round_number,
            "state": game_session.state,
            "message_id": game_session.message_id,
            "polls_time": game_session.polls_time
        }

    async def test_add_user_to_session_manual(self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store, user_1: UserModel, game_session_1: SessionModel):
        game_session = await store.user.add_user_to_session_manual(user_1, game_session_1)

        assert game_session.id_ == game_session_1.id_
        assert game_session.users

    async def test_add_user_photo(self, store: Store, user_session_request: dict, game_session_with_user: SessionModel):
        user_session = await store.user.add_user_photo(**user_session_request)

        assert isinstance(user_session, UserSession)
        assert user_session_to_dict(user_session) == {
            "id_": user_session.id_,
            "user_id": user_session.user_id,
            "session_id": user_session.session_id,
            "points": user_session.points,
            "in_game": user_session.in_game,
            "file_id": user_session.file_id
        }

    async def test_delete_user_from_session(self, db_sessionmaker: async_sessionmaker[AsyncSession], store: Store, user_session_1):
        await store.user.delete_user_from_session(user_session_1.user_id, user_session_1.session_id)

        async with db_sessionmaker() as session:
            user_session = await session.scalar(select(UserSession)
                                                .where(
                UserSession.session_id == user_session_1.session_id,
                UserSession.user_id == user_session_1.user_id))

        assert user_session is None

    async def test_get_all_users_in_session(self, store: Store, game_session_with_user):
        users = await store.user.get_all_users_in_session(game_session_with_user.id_)

        assert len(users) == 1

    async def test_get_game_statistics(self, store: Store, game_session_with_user: SessionModel, user_session_request_1: dict, user_session_request: dict):
        await store.user.add_user_photo(**user_session_request)
        statistics = await store.user.get_game_statistics(game_session_with_user.id_)

        users = [user_session_request_1]

        assert statistics == {
            "users": users,
            "chat_id": game_session_with_user.chat_id,
            "round_number": game_session_with_user.round_number,
            "in_progress": game_session_with_user.in_progress,
        }


    async def test_set_seconds(self, store: Store, game_session_1):
        game_session = await store.user.set_seconds(game_session_1.id_, 42)

        assert game_session.polls_time == 42





