from urllib.parse import urlencode

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.tg_bot.dataclasses import (
    Update,
)
from app.tg_bot.parsing_update import (
    get_callback_query_from_update,
    get_message_from_update,
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
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()

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
                match update:
                    case {"message": _}:
                        update_obj = get_message_from_update(update)
                    case {"callback_query": _}:
                        update_obj = get_callback_query_from_update(update)
                    case _:
                        update_obj = Update(update_id=update["update_id"])

                updates.append(update_obj)

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

    async def notify_about_participation(self, callback_query) -> None:
        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="answerCallbackQuery",
            params={
                "callback_query_id": callback_query.id_,
                "text": "Вы участвуете в конкурсе!",
            },
        )

        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info(data)
