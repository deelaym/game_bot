import pytest


@pytest.fixture
def update_message():
    return {
        "update_id": 42,
        "message": {
            "message_id": 777,
            "from": {
                "id": 66666666,
                "is_bot": False,
                "first_name": "Name",
                "username": "username",
                "language_code": "en",
            },
            "chat": {
                "id": 42424242,
                "title": "test",
                "type": "group",
                "all_members_are_administrators": True,
            },
            "date": 1716502322,
            "text": "/start",
        },
    }


@pytest.fixture
def update_callback_query():
    return {
        "update_id": 99,
        "callback_query": {
            "id": 1053051988517703532,
            "from": {
                "id": 66666666,
                "is_bot": False,
                "first_name": "Name",
                "username": "username",
            },
            "message": {
                "message_id": 6953,
                "from": {
                    "id": 7135032952,
                    "is_bot": True,
                    "first_name": "Bot",
                    "username": "bot",
                },
                "chat": {
                    "id": 42424242,
                    "title": "test",
                    "type": "group",
                },
                "date": 1716480350,
                "text": "Button",
                "data": "data",
            },
        },
    }
