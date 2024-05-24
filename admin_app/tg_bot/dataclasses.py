from dataclasses import dataclass


@dataclass
class Chat:
    id_: int


@dataclass
class MessageObject:
    chat: Chat | None = None


@dataclass
class Update:
    message: MessageObject | None = None
