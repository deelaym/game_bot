from urllib.parse import urlencode

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.tg_bot.dataclasses import (
    CallbackQueryObject,
    Chat,
    FromObject,
    MessageObject,
    Update,
)
from app.tg_bot.poller import Poller

API_PATH = "https://api.telegram.org/bot"
TIMEOUT = 60


class TgApiAccessor(BaseAccessor):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.session: ClientSession | None = None
        self.offset: int = -2
        self.poller: Poller | None = None

    async def connect(self, app) -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))

        self.poller = Poller(app.store)
        self.logger.info("start polling")
        self.poller.start()

    async def disconnect(self, app) -> None:
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host, token, method, params):
        params.setdefault("timeout", TIMEOUT)
        return f"{host}{token}/{method}?{urlencode(params)}"

    async def poll(self):
        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="getUpdates",
            params={"offset": self.offset + 1},
        )
        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info(data)

            updates = []
            for update in data.get("result", []):
                self.offset = update["update_id"]
                if "message" in update:
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

                    update = Update(
                        update_id=update["update_id"],
                        message=MessageObject(
                            message_id=message["message_id"],
                            from_=from_obj,
                            chat=chat_obj,
                            date=date,
                            text=text,
                        ),
                    )

                elif "callback_query" in update:
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
                        id_=update["callback_query"], from_=from_obj
                    )

                    update = Update(
                        update_id=update["update_id"],
                        message=message_obj,
                        callback_query=callback_query,
                    )
                else:
                    update = Update(update_id=update["update_id"])

                updates.append(update)

            await self.app.store.bot_manager.handle_updates(updates)

    async def send_start_button_message(self, message) -> None:
        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="sendMessage",
            params={
                "chat_id": message.chat_id,
                "text": message.text,
                "reply_markup": message.reply_markup,
            },
        )
        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info(data)
