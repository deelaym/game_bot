from unittest.mock import AsyncMock

from app.store import Store
from app.tg_bot.parsing_update import (
    get_callback_query_from_update,
    get_message_from_update,
    get_poll_answer_from_update,
)
from app.users.models import UserSession


class TestTgApiAccessor:
    async def test_poll_when_no_update(
        self, store: Store, tg_api_poll_no_updates_mock: AsyncMock
    ):
        data = await store.tg_bot.poll()
        assert data == {"ok": True, "result": []}
        tg_api_poll_no_updates_mock.assert_called_once()

    async def test_poll_when_message_update(
        self,
        store: Store,
        tg_api_poll_message_update_mock: AsyncMock,
        update_message_for_poll: dict,
    ):
        data = await store.tg_bot.poll()
        assert data == update_message_for_poll
        tg_api_poll_message_update_mock.assert_called_once()

    async def test_send_updates_no_update(
        self, store: Store, tg_api_poll_no_updates_mock: AsyncMock
    ):
        data = await store.tg_bot.poll()
        await store.tg_bot.send_updates(data)
        assert store.tg_bot.queue.empty()

    async def test_send_updates_message_update(
        self,
        store: Store,
        tg_api_poll_message_update_mock: AsyncMock,
        update_message: dict,
    ):
        data = await store.tg_bot.poll()
        await store.tg_bot.send_updates(data)
        update = get_message_from_update(update_message)

        assert not store.tg_bot.queue.empty()
        assert await store.tg_bot.queue.get() == update

    async def test_send_updates_callback_query_update(
        self,
        store: Store,
        tg_api_poll_callback_query_update_mock: AsyncMock,
        update_callback_query: dict,
    ):
        data = await store.tg_bot.poll()
        await store.tg_bot.send_updates(data)
        update = get_callback_query_from_update(update_callback_query)

        assert not store.tg_bot.queue.empty()
        assert await store.tg_bot.queue.get() == update

    async def test_send_updates_another_update(
        self, store: Store, tg_api_poll_another_update_mock: AsyncMock
    ):
        data = await store.tg_bot.poll()
        await store.tg_bot.send_updates(data)

        assert store.tg_bot.queue.empty()

    async def test_get_poll_answers(
        self,
        store: Store,
        tg_api_stop_poll_mock: AsyncMock,
        user_session_1: UserSession,
        user_session_2: UserSession,
    ):
        update = get_poll_answer_from_update(await store.tg_bot.stop_poll())
        answers = await store.tg_bot.get_poll_answers(
            user_session_1.id_, user_session_2.id_, update
        )

        assert answers == (0, 1)
