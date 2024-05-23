from unittest.mock import AsyncMock

import pytest

from app.store import Store


@pytest.fixture
def tg_api_send_message_mock(store: Store) -> AsyncMock:
    mock = AsyncMock()
    store.tg_bot.send_message = mock
    return mock


@pytest.fixture
def tg_api_get_profile_photo_mock(store: Store) -> AsyncMock:
    mock = AsyncMock()
    store.tg_bot.get_profile_photo = mock
    mock.return_value = [[
        {
            "file_id": "file_id",
            "file_unique_id": "file_id",
            "file_size": 10582,
            "width": 160,
            "height": 160
        }
    ]]
    return mock

@pytest.fixture
def tg_api_notify_about_participation_mock(store: Store):
    mock = AsyncMock()
    store.tg_bot.notify_about_participation = mock
    mock.return_value = {'ok': True, 'result': True}


@pytest.fixture
def tg_api_send_photo_mock(store: Store):
    mock = AsyncMock()
    store.tg_bot.send_photo = mock