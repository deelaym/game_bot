from urllib.parse import urlencode

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.tg_bot.dataclasses import Update, Message, FromObject, ChatObject, MessageObject
from app.tg_bot.poller import Poller


API_PATH = 'https://api.telegram.org/bot'
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
        return f'{host}{token}/{method}?{urlencode(params)}'

    async def poll(self):
        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method='getUpdates',
            params={'offset': self.offset + 1}
        )
        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info(data)

            updates = []
            for update in data.get('result', []):
                self.offset = update['update_id']
                message = update['message']

                from_ = message['from']
                from_obj = FromObject(
                    id_=from_['id'],
                    is_bot=from_['is_bot'],
                    first_name=from_['first_name'],
                    username=from_['username'],
                    language_code=from_['language_code']
                )

                chat = message['chat']
                chat_obj = ChatObject(
                    id_=chat['id'],
                    first_name=chat['first_name'],
                    username=chat['username'],
                    type=chat['type']
                )

                date = message['date']
                text = '...'
                if 'text' in message:
                    text = message['text']

                update = Update(
                    update_id=update['update_id'],
                    message=MessageObject(
                        message_id=message['message_id'],
                        from_=from_obj,
                        chat=chat_obj,
                        date=date,
                        data=text
                    )
                )

                updates.append(update)

            await self.app.store.bot_manager.handle_updates(updates)

    async def send_message(self, message) -> None:
        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method='sendMessage',
            params={
                'chat_id': message.chat_id,
                'text': message.text
            }
        )
        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info(data)



