from app.tg_bot.dataclasses import Update, FromObject, MessageObject, Chat, CallbackQueryObject
from app.tg_bot.parsing_update import get_message_from_update, get_callback_query_from_update


def test_get_message_from_update(update_message):
    update = get_message_from_update(update_message)
    assert Update(
        update_id=42,
        message=MessageObject(
            message_id=777,
            from_=FromObject(
                id_=66666666,
                is_bot=False,
                first_name="Name",
                username="username"
            ),
            chat=Chat(
                id_=42424242,
                title="test",
                type="group"
            ),
            date=1716502322,
            text="/start",
        ),
    ) == update


def test_get_callback_query_from_update(update_callback_query):
    update = get_callback_query_from_update(update_callback_query)
    assert Update(
        update_id=99,
        message=MessageObject(
            message_id=6953,
            from_=None,
            chat=Chat(
                id_=42424242,
                title="test",
                type="group"
            ),
            date=1716480350
        ),
        callback_query=CallbackQueryObject(
            id_=1053051988517703532,
            from_=FromObject(
                id_=66666666,
                is_bot=False,
                first_name="Name",
                username="username"
            )
        ),
    ) == update