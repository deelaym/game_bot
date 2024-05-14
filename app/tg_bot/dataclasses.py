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
    type: str | None = None
    title: str | None = None
    first_name: str | None = None
    username: str | None = None


@dataclass
class MessageObject:
    message_id: int | None = None
    date: int | None = None
    from_: FromObject | None = None
    chat: Chat | None = None
    text: str | None = None


@dataclass
class CallbackQueryObject:
    id_: int
    from_: FromObject

@dataclass
class Option:
    text: str
    voter_count: int

@dataclass
class PollObject:
    id_: int
    question: str
    options: list[Option]
    total_voter_count: int


@dataclass
class Update:
    update_id: int | None = None
    message: MessageObject | None = None
    callback_query: CallbackQueryObject | None = None
    poll: PollObject | None = None


@dataclass
class Message:
    chat_id: int
    text: str


@dataclass
class ButtonMessage(Message):
    reply_markup: str = ""


