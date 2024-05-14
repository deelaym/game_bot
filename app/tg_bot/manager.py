import asyncio
import json
from logging import getLogger
import random

from app.tg_bot.dataclasses import ButtonMessage, Update, Message
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
                text = update.message.text.split('@')[0][1:]
                await self.fsm.launch_func(text, update)
            else:
                await self.fsm.launch_func(self.fsm.state, update)




        # for update in updates:
        #     if update.message.text and update.message.text.startswith("/start"):
        #         await self.start_button(update)
        #     if update.message.text and update.message.text.startswith("/stop"):
        #         await self.app.store.user.stop_game_session(update)
        #     if update.callback_query:
        #         await self.app.store.user.add_user_to_session(update)
        #         self.logger.info(update.callback_query)

    async def start_button(self, update):
        self.fsm.state = self.fsm.transitions[self.fsm.state]["next_state"]

        game_session = await self.app.store.user.get_game_session(update.message.chat.id_)
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
                    text="Конкурс уже идет. Отправьте /stop, чтобы завершить его. Или /round, чтобы возобновить игру."
                )
            )


    async def start_round(self, update):
        game_session = await self.app.store.user.get_game_session(update.message.chat.id_)

        users_in_game = await self.app.store.user.get_all_in_game_users(update.message.chat.id_)
        random.shuffle(users_in_game)

        match len(users_in_game):
            case 2:
                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text="Финал!"
                    )
                )
            case 1 | 0:
                fsm = self.app.store.bot_manager.fsm
                fsm.state = fsm.transitions[fsm.state]["next_state"]
                await fsm.launch_func(fsm.state, update)
            case _:
                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text=f"Раунд {game_session.round_number}!"
                    )
                )

        await self.app.store.user.set_round_number(update.message.chat.id_)

        while users_in_game:
            first_user = users_in_game.pop()
            if users_in_game:
                second_user = users_in_game.pop()

                await self.app.store.tg_bot.send_photo(first_user, update.message.chat.id_)
                await self.app.store.tg_bot.send_photo(second_user, update.message.chat.id_)

                await self.app.store.tg_bot.send_poll(update.message.chat.id_, first_user, second_user)

                # await asyncio.sleep(self.app.store.tg_bot.seconds)


                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text="Опрос окончен!"
                    )
                )

                winner = await self.app.store.user.get_winner_in_pair(first_user, second_user)

                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text=f"Победитель - {winner}!" if winner else "Ничья! Оба участника проходят в следующий раунд!"
                    )
                )

        await self.start_round(update)





