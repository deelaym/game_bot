from app.tg_bot.dataclasses import (
    CallbackQueryObject,
    Chat,
    FromObject,
    MessageObject,
    Option,
    PollObject,
    Update,
)


def get_message_from_update(update) -> Update:
    message = update["message"]
    from_ = message["from"]
    from_obj = FromObject(
        id_=from_["id"],
        is_bot=from_["is_bot"],
        first_name=from_["first_name"],
        username=from_.get("username", None),
    )

    chat = message["chat"]
    chat_obj = Chat(
        id_=chat["id"],
        type=chat["type"],
        title=chat.get("title", None),
        first_name=chat.get("first_name", None),
        username=chat.get("username", None),
    )

    date = message["date"]
    text = message.get("text", "")

    return Update(
        update_id=update["update_id"],
        message=MessageObject(
            message_id=message["message_id"],
            from_=from_obj,
            chat=chat_obj,
            date=date,
            text=text,
        ),
    )


def get_callback_query_from_update(update) -> Update:
    from_ = update["callback_query"]["from"]
    from_obj = FromObject(
        id_=from_["id"],
        is_bot=from_["is_bot"],
        first_name=from_["first_name"],
        username=from_.get("username", None),
    )

    message = update["callback_query"]["message"]
    chat = message["chat"]
    chat_obj = Chat(
        id_=chat["id"],
        type=chat["type"],
        title=chat.get("title", None),
        first_name=chat.get("first_name", None),
        username=chat.get("username", None),
    )
    message_obj = MessageObject(
        message_id=message["message_id"],
        date=message["date"],
        chat=chat_obj,
    )

    callback_query = CallbackQueryObject(
        id_=update["callback_query"]["id"], from_=from_obj
    )

    return Update(
        update_id=update["update_id"],
        message=message_obj,
        callback_query=callback_query,
    )


def get_poll_answer_from_update(update) -> Update:
    poll = update["poll"]
    options = [
        Option(text=option["text"], voter_count=option["voter_count"])
        for option in poll["options"]
    ]

    poll_obj = PollObject(
        id_=poll["id"],
        question=poll["question"],
        options=options,
        total_voter_count=poll["total_voter_count"],
    )

    return Update(update_id=update.get("update_id", None), poll=poll_obj)
