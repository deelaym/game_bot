from logging import getLogger

from app.tg_bot.dataclasses import Update, Message


class BotManager:
    def __init__(self, app):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            await self.app.store.tg_bot.send_message(
                Message(
                    chat_id=update.message.chat.id_,
                    text=update.message.data
                )
            )
