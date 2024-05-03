from dataclasses import dataclass
from typing import Any


@dataclass
class FromObject:
    id_: int
    is_bot: bool
    first_name: str
    username: str
    language_code: str


@dataclass
class ChatObject:
    id_: int
    first_name: str
    username: str
    type: str


@dataclass
class MessageObject:
    message_id: int
    from_: FromObject
    chat: ChatObject
    date: int
    data: Any



@dataclass
class Update:
    update_id: int
    message: MessageObject

@dataclass
class Message:
    chat_id: int
    text: str

