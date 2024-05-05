import json
from logging import getLogger

from app.tg_bot.dataclasses import ButtonMessage, Update


class BotManager:
    def __init__(self, app):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.message.text and update.message.text.startswith("/start"):
                await self.start_button(update)
            if update.callback_query:
                await self.app.store.user.add_user_to_session(update)
                self.logger.info(update.callback_query)

    async def start_button(self, update):
        keyboard = {
            "inline_keyboard": [
                [{"text": "Участвовать", "callback_data": "data"}]
            ]
        }

        await self.app.store.tg_bot.send_start_button_message(
            ButtonMessage(
                chat_id=update.message.chat.id_,
                text="Принять участие в фото конкурсе",
                reply_markup=json.dumps(keyboard),
            )
        )

        await self.app.store.user.create_new_session(update)
