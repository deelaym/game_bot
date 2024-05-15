import json
import random
from logging import getLogger

from app.tg_bot.dataclasses import ButtonMessage, Message, Update
from app.tg_bot.fsm import FSM


class BotManager:
    def __init__(self, app):
        self.app = app
        self.logger = getLogger("handler")
        self.fsm = None

        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app):
        self.fsm = FSM(app)

    async def disconnect(self, app):
        return

    async def handle_updates(self, updates: list[Update]):
        self.logger.info(self.app.store.bot_manager.fsm.state)

        for update in updates:
            if update.message and update.message.text:
                text = update.message.text.split("@")[0][1:]
                await self.fsm.launch_func(text, update)
            else:
                await self.fsm.launch_func(self.fsm.state, update)

    async def start_button(self, update):
        self.fsm.state = self.fsm.transitions[self.fsm.state]["next_state"]

        game_session = await self.app.store.user.get_game_session(
            update.message.chat.id_
        )
        if not game_session or not game_session.in_progress:
            keyboard = {
                "inline_keyboard": [
                    [{"text": "Участвовать", "callback_data": "data"}]
                ]
            }

            await self.app.store.tg_bot.send_start_button_message(
                ButtonMessage(
                    chat_id=update.message.chat.id_,
                    text=f"Принять участие в фото конкурсе. \
                    Начало через {self.app.store.tg_bot.seconds} секунд.",
                    reply_markup=json.dumps(keyboard),
                ),
                update,
            )

            await self.app.store.user.create_new_session(update)
        else:
            await self.app.store.tg_bot.send_message(
                Message(
                    chat_id=update.message.chat.id_,
                    text="""Конкурс уже идет. 
                    Отправьте /stop, чтобы завершить его. 
                    Или /round, чтобы возобновить игру.""",
                )
            )

    async def start_round(self, update):
        fsm = self.app.store.bot_manager.fsm
        game_session = await self.app.store.user.get_game_session(
            update.message.chat.id_
        )
        users_in_game = await self.app.store.user.get_all_in_game_users(
            update.message.chat.id_
        )
        random.shuffle(users_in_game)

        match len(users_in_game):
            case 2:
                await self.app.store.tg_bot.send_message(
                    Message(chat_id=update.message.chat.id_, text="Финал!")
                )
            case 1:
                fsm.state = "stop"
                await fsm.launch_func(fsm.state, update)
                return
            case _:
                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text=f"Раунд {game_session.round_number}!",
                    )
                )

        while users_in_game:
            first_user = users_in_game.pop()
            if users_in_game:
                second_user = users_in_game.pop()

                await self.app.store.tg_bot.send_photo(
                    first_user, update.message.chat.id_
                )
                await self.app.store.tg_bot.send_photo(
                    second_user, update.message.chat.id_
                )

                await self.app.store.tg_bot.send_poll(
                    update, first_user, second_user
                )

                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_, text="Опрос окончен!"
                    )
                )

                winner = await self.app.store.user.get_winner_in_pair(
                    first_user, second_user
                )

                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text=f"Победитель - {winner}!"
                        if winner
                        else "Ничья! Оба участника проходят в следующий раунд!",
                    )
                )
                await self.app.store.user.set_round_number(
                    update.message.chat.id_
                )
        await self.start_round(update)
