from unittest.mock import AsyncMock

import pytest

from app.store import Store

from .utils import *  # noqa:  F403


@pytest.fixture
def tg_api_send_message_mock(store: Store) -> AsyncMock:
    mock = AsyncMock()
    store.tg_bot.send_message = mock
    return mock


@pytest.fixture
def tg_api_send_start_button_message_mock(store: Store) -> AsyncMock:
    mock = AsyncMock()
    store.tg_bot.send_start_button_message = mock
    return mock


@pytest.fixture
def tg_api_get_profile_photo_mock(store: Store) -> AsyncMock:
    mock = AsyncMock()
    store.tg_bot.get_profile_photo = mock
    mock.return_value = [
        [
            {
                "file_id": "file_id",
                "file_unique_id": "file_id",
                "file_size": 10582,
                "width": 160,
                "height": 160,
            }
        ]
    ]
    return mock


@pytest.fixture
def tg_api_notify_about_participation_mock(store: Store):
    mock = AsyncMock()
    store.tg_bot.notify_about_participation = mock
    mock.return_value = {"ok": True, "result": True}
    return mock


@pytest.fixture
def tg_api_send_photo_mock(store: Store):
    mock = AsyncMock()
    store.tg_bot.send_photo = mock
    return mock


@pytest.fixture
def tg_api_delete_message_mock(store: Store):
    mock = AsyncMock()
    store.tg_bot.delete_message = mock
    return mock


@pytest.fixture
def tg_api_send_poll_mock(store: Store):
    mock = AsyncMock()
    store.tg_bot.send_poll = mock
    return mock


@pytest.fixture
def tg_api_stop_poll_mock(store: Store):
    mock = AsyncMock()
    store.tg_bot.stop_poll = mock
    mock.return_value = {
        "ok": True,
        "poll": {
            "id": "5370570743509683973",
            "question": "Какое фото больше нравится?",
            "options": [
                {"text": "Надежда", "voter_count": 0},
                {"text": "@deelaym", "voter_count": 2},
            ],
            "total_voter_count": 2,
            "is_closed": True,
            "is_anonymous": True,
            "type": "regular",
            "allows_multiple_answers": False,
        },
    }
    return mock


@pytest.fixture
def tg_api_poll_message_update_mock(store: Store, update_message_for_poll):
    mock = AsyncMock()
    store.tg_bot.poll = mock
    mock.return_value = update_message_for_poll
    return mock


@pytest.fixture
def tg_api_poll_callback_query_update_mock(
    store: Store, update_callback_query_for_poll
):
    mock = AsyncMock()
    store.tg_bot.poll = mock
    mock.return_value = update_callback_query_for_poll
    return mock


@pytest.fixture
def tg_api_poll_no_updates_mock(store: Store):
    mock = AsyncMock()
    mock.return_value = {"ok": True, "result": []}
    store.tg_bot.poll = mock
    return mock


@pytest.fixture
def tg_api_poll_another_update_mock(store: Store):
    mock = AsyncMock()
    mock.return_value = {
        "ok": True,
        "result": [
            {
                "update_id": 6984,
                "from": {
                    "id": 7135032952,
                    "is_bot": True,
                    "first_name": "Photo Contest Bot",
                    "username": "shashin_kontesuto_bot",
                },
                "chat": {
                    "id": -4236667037,
                    "title": "test2",
                    "type": "group",
                    "all_members_are_administrators": True,
                },
                "date": 1716540685,
                "text": "Принять участие в фото конкурсе. "
                        "Начало через 15 секунд.",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "Участвовать", "callback_data": "data"}]
                    ]
                },
            }
        ],
    }
    store.tg_bot.poll = mock
    return mock


@pytest.fixture
def update_message_for_poll(update_message):
    return {"ok": True, "result": [update_message]}


@pytest.fixture
def update_callback_query_for_poll(update_callback_query):
    return {"ok": True, "result": [update_callback_query]}
