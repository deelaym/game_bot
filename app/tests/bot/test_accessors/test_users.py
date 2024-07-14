from unittest.mock import AsyncMock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload

from admin_app.tests.utils import session_to_dict
from app.store import Store
from app.tg_bot.dataclasses import Update
from app.users.models import SessionModel, UserModel, UserSession


class TestUserAccessor:
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
            "polls_time": game_session.polls_time,
        }

    async def test_get_user(
        self, store: Store, user_1: UserModel, user_request: dict
    ):
        user = await store.user.get_user(user_1.id_)

        assert user_request == {
            "id_": user.id_,
            "first_name": user.first_name,
            "username": user.username,
        }

    async def test_add_user_to_session(
        self,
        db_sessionmaker,
        store: Store,
        update_with_callback,
        tg_api_get_profile_photo_mock,
        tg_api_notify_about_participation_mock,
    ):
        await store.user.create_new_session(update_with_callback)
        await store.user.add_user_to_session(update_with_callback)

        async with db_sessionmaker() as session:
            game_session = await session.scalar(
                select(SessionModel)
                .where(
                    SessionModel.chat_id
                    == update_with_callback.message.chat.id_,
                    SessionModel.in_progress,
                )
                .options(joinedload(SessionModel.users))
            )

            assert len(game_session.users) == 1

    async def test_stop_game_session(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        update: Update,
        game_session_1: SessionModel,
        tg_api_send_message_mock: AsyncMock,
    ):
        await store.user.stop_game_session(update)
        async with db_sessionmaker() as session:
            game_session = await session.scalar(
                select(SessionModel).where(
                    SessionModel.id_ == game_session_1.id_
                )
            )
            assert game_session.id_ == game_session_1.id_
            assert not game_session.in_progress

    async def test_get_amount_of_users_in_session(
        self, db_sessionmaker, store: Store, game_session_1, user_1
    ):
        async with db_sessionmaker() as session:
            game_session = await session.scalar(
                select(SessionModel).where(
                    SessionModel.id_ == game_session_1.id_
                )
            )
            game_session.users.append(user_1)
            await session.commit()
            users_amount = await store.user.get_amount_of_users_in_session(
                game_session_1.chat_id
            )

            assert len(game_session.users) == users_amount
            assert users_amount == 1

    async def test_get_winners_game_session_in_progress(
        self,
        store: Store,
        game_session_with_two_users: SessionModel,
        update: Update,
        user_session_1: UserSession,
        user_session_2: UserSession,
        user_1: UserModel,
        user_2: UserModel,
        tg_api_send_message_mock: AsyncMock,
    ):
        text = await store.user.get_winners(update, game_session_with_two_users)

        assert (
            f"Топ-2:\n"
            f" 1. @{user_1.username} Побед: 0\n"
            f" 2. @{user_2.username} Побед: 0"
        ) == text

    async def test_get_winners_game_session_not_in_progress(
        self,
        store: Store,
        game_session_with_user: SessionModel,
        update: Update,
        user_session_1: UserSession,
        user_1: UserModel,
        tg_api_send_message_mock: AsyncMock,
        tg_api_send_photo_mock: AsyncMock,
    ):
        game_session_with_user.in_progress = False
        text = await store.user.get_winners(update, game_session_with_user)
        assert f"Победитель конкурса: @{user_1.username}" == text

    async def test_get_all_in_game_users(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        game_session_with_two_users: SessionModel,
        user_1: UserModel,
        user_2: UserModel,
        user_session_1: UserSession,
        user_session_2: UserSession,
    ):
        users = await store.user.get_all_in_game_users(
            game_session_with_two_users.chat_id
        )

        assert len(users) == 2
        assert users[0].user_id == user_1.id_
        assert users[1].user_id == user_2.id_

        async with db_sessionmaker() as session:
            user_session = await session.scalar(
                select(UserSession).where(UserSession.id_ == user_session_2.id_)
            )
            user_session.in_game = False
            await session.commit()

        users = await store.user.get_all_in_game_users(
            game_session_with_two_users.chat_id
        )

        assert len(users) == 1
        assert users[0].user_id == user_1.id_

    async def test_set_round_number(
        self, store: Store, game_session_1: SessionModel
    ):
        game_session = await store.user.set_round_number(game_session_1.chat_id)

        assert game_session.round_number == 2

    async def test_set_points_two_users(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        user_session_1: UserSession,
        user_session_2: UserSession,
    ):
        await store.user.set_points(
            user_session_1.id_, user_session_2.id_, 1, 0
        )

        async with db_sessionmaker() as session:
            user_session_1_ = await session.get(UserSession, user_session_1.id_)
            user_session_2_ = await session.get(UserSession, user_session_2.id_)

        assert user_session_1_.points == user_session_1.points + 1
        assert user_session_2_.points == user_session_2.points

    async def test_set_points_one_user(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        user_session_1: UserSession,
        user_session_2: UserSession,
    ):
        await store.user.set_points(user_session_1.id_, None, 1)

        async with db_sessionmaker() as session:
            user_session_1_ = await session.get(UserSession, user_session_1.id_)

        assert user_session_1_.points == user_session_1.points + 1

    async def test_get_winner_in_pair_first_user_winner(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        user_session_1: UserSession,
        user_session_2: UserSession,
        user_1: UserModel,
        user_2: UserModel,
    ):
        await store.user.set_points(
            user_session_1.id_, user_session_2.id_, 1, 0
        )
        name = await store.user.get_winner_in_pair(
            user_session_1, user_session_2
        )

        assert name == user_1.display_name

    async def test_get_winner_in_pair_second_user_winner(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        user_session_1: UserSession,
        user_session_2: UserSession,
        user_1: UserModel,
        user_2: UserModel,
    ):
        await store.user.set_points(
            user_session_1.id_, user_session_2.id_, 0, 1
        )
        name = await store.user.get_winner_in_pair(
            user_session_1, user_session_2
        )

        assert name == user_2.display_name

    async def test_get_winner_in_pair_draw(
        self,
        db_sessionmaker: async_sessionmaker[AsyncSession],
        store: Store,
        user_session_1: UserSession,
        user_session_2: UserSession,
        user_1: UserModel,
        user_2: UserModel,
    ):
        await store.user.set_points(
            user_session_1.id_, user_session_2.id_, 1, 1
        )
        name = await store.user.get_winner_in_pair(
            user_session_1, user_session_2
        )

        assert name is None

    async def test_get_game_session(
        self, store: Store, game_session_1: SessionModel
    ):
        game_session = await store.user.get_game_session(game_session_1.chat_id)
        assert game_session.id_ == game_session_1.id_

    async def test_get_all_in_progress_game_sessions(
        self,
        store: Store,
        game_session_1: SessionModel,
        game_session_2: SessionModel,
    ):
        game_sessions = (
            await store.user.get_all_in_progress_game_sessions()
        ).all()

        assert len(game_sessions) == 2
        assert game_sessions[0].id_ == game_session_1.id_
        assert game_sessions[1].id_ == game_session_2.id_

    async def test_get_state(self, store: Store, game_session_1: SessionModel):
        state = await store.user.get_state(game_session_1.chat_id)

        assert state == "start"

    async def test_set_state(self, store: Store, game_session_1: SessionModel):
        state = await store.user.set_state(game_session_1.chat_id, "stop")

        assert state == "stop"

    async def test_set_message_id_to_session(
        self, store: Store, game_session_1: SessionModel
    ):
        game_session = await store.user.set_message_id_to_session(
            game_session_1.chat_id, 42
        )

        assert game_session.message_id == 42

    async def test_get_seconds_game_session_exists(
        self, store: Store, game_session_1: SessionModel
    ):
        seconds = await store.user.get_seconds(game_session_1.id_)
        assert seconds == 15

    async def test_get_seconds_game_session_not_exists(self, store: Store):
        seconds = await store.user.get_seconds(42)
        assert seconds == 15
