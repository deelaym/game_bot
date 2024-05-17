import json
import random
from logging import getLogger

from app.tg_bot.dataclasses import ButtonMessage, Message, Update


class BotManager:
    def __init__(self, app):
        self.app = app
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        self.logger.info(f"state: {self.app.store.fsm.state}")

        for update in updates:
            if update.message and update.message.text:
                text = update.message.text.split("@")[0][1:]
                await self.app.store.fsm.launch_func(text, update)
            else:
                await self.app.store.fsm.launch_func(
                    self.app.store.fsm.state, update
                )

    async def start_button(self, update):
        self.app.store.fsm.state = "start"
        game_session = await self.app.store.user.get_game_session(
            update.message.chat.id_
        )
        if not game_session or not game_session.in_progress:
            keyboard = {
                "inline_keyboard": [
                    [{"text": "Участвовать", "callback_data": "data"}]
                ]
            }

            data = await self.app.store.tg_bot.send_start_button_message(
                ButtonMessage(
                    chat_id=update.message.chat.id_,
                    text=f"Принять участие в фото конкурсе. \
                    Начало через {self.app.store.tg_bot.seconds} секунд.",
                    reply_markup=json.dumps(keyboard),
                ),
                update,
            )

            await self.app.store.user.create_new_session(update)

            await self.app.store.user.set_message_id_to_session(
                update.message.chat.id_, data["result"]["message_id"]
            )
            await self.app.store.tg_bot.finish_registration(
                update, data["result"]["message_id"]
            )

            self.app.store.fsm.state = await self.app.store.user.set_state(
                update.message.chat.id_, self.app.store.fsm.transitions[
                    await self.app.store.user.get_state(update.message.chat.id_)
                ]["next_state"]
            )
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
        self.app.store.fsm.state = "round"
        game_session = await self.app.store.user.get_game_session(
            update.message.chat.id_
        )
        if await self.is_game_stop(update):
            return

        users_in_game = await self.app.store.user.get_all_in_game_users(
            update.message.chat.id_
        )
        random.shuffle(users_in_game)

        if await self.check_users_in_game_amount(
            update, len(users_in_game), game_session.round_number
        ):
            return

        while users_in_game:
            if await self.is_game_stop(update):
                return

            first_user = users_in_game.pop()
            if users_in_game:
                second_user = users_in_game.pop()

                await self.send_poll_with_photos(
                    update, first_user, second_user
                )
                if await self.is_game_stop(update):
                    return
                await self.send_winner_in_round(update, first_user, second_user)

                await self.app.store.user.set_round_number(
                    update.message.chat.id_
                )
            else:
                winner = await self.app.store.user.get_winner_in_pair(
                    first_user
                )
                await self.app.store.tg_bot.send_photo(first_user, update.message.chat.id_)
                await self.app.store.user.set_points(first_user.id_, None, 1)

                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text=f"{winner} проходит в следующий раунд! "
                    )
                )

        await self.start_round(update)

    async def check_users_in_game_amount(
        self, update, users_amount, round_number
    ):
        match users_amount:
            case 2:
                await self.app.store.tg_bot.send_message(
                    Message(chat_id=update.message.chat.id_, text="Финал!")
                )
            case 1 | 0:
                self.app.store.fsm.state = await self.app.store.user.set_state(
                    update.message.chat.id_, self.app.store.fsm.transitions[
                        await self.app.store.user.get_state(update.message.chat.id_)
                    ]["next_state"]
                )
                await self.app.store.fsm.launch_func(
                    self.app.store.fsm.state, update
                )
                return True
            case _:
                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text=f"Раунд {round_number}!",
                    )
                )
        return None

    async def send_poll_with_photos(self, update, first_user, second_user):
        await self.app.store.tg_bot.send_photo(
            first_user, update.message.chat.id_
        )
        await self.app.store.tg_bot.send_photo(
            second_user, update.message.chat.id_
        )

        self.logger.debug(f"poll sending")

        await self.app.store.tg_bot.send_poll(update, first_user, second_user)

        self.logger.debug(f"poll sent")

        if await self.is_game_stop(update):
            return

        await self.app.store.tg_bot.send_message(
            Message(chat_id=update.message.chat.id_, text="Опрос окончен!")
        )

    async def is_game_stop(self, update):
        game_session = await self.app.store.user.get_game_session(
            update.message.chat.id_
        )
        return not game_session.in_progress

    async def send_winner_in_round(self, update, first_user, second_user=None):
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
