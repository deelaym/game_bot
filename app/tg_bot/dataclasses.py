from dataclasses import dataclass


@dataclass
class FromObject:
    id_: int
    is_bot: bool
    first_name: str
    username: str | None = None


@dataclass
class Chat:
    id_: int
    type: str
    title: str | None = None
    first_name: str | None = None
    username: str | None = None


@dataclass
class MessageObject:
    message_id: int
    date: int
    from_: FromObject | None = None
    chat: Chat | None = None
    text: str | None = None


@dataclass
class CallbackQueryObject:
    id_: int
    from_: FromObject


@dataclass
class Update:
    update_id: int
    message: MessageObject | None = None
    callback_query: CallbackQueryObject | None = None


@dataclass
class Message:
    chat_id: int
    text: str


@dataclass
class ButtonMessage(Message):
    reply_markup: str = ""
