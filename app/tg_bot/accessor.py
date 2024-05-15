import asyncio
import json
from urllib.parse import urlencode

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.tg_bot.dataclasses import (
    Message,
    Update,
)
from app.tg_bot.parsing_update import (
    get_callback_query_from_update,
    get_message_from_update,
    get_poll_answer_from_update,
)
from app.tg_bot.poller import Poller
from app.users.models import UserSession

API_PATH = "https://api.telegram.org/bot"
TIMEOUT = 60


class TgApiAccessor(BaseAccessor):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.session: ClientSession | None = None
        self.offset: int = -2
        self.poller: Poller | None = None
        self.seconds: int = 10

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
                flag = True
                match update:
                    case {"message": _}:
                        update_obj = get_message_from_update(update)
                    case {"callback_query": _}:
                        update_obj = get_callback_query_from_update(update)
                    case {"poll": _}:
                        update_obj = get_poll_answer_from_update(update)
                        flag = False
                    case _:
                        update_obj = Update(update_id=update["update_id"])
                if flag:
                    updates.append(update_obj)

            await self.app.store.bot_manager.handle_updates(updates)
            return updates

    def _done_callback(self, result):
        if result.exception():
            self.logger.error(result.exception())

    async def send_start_button_message(self, message, update) -> None:
        send_url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="sendMessage",
            params={
                "chat_id": message.chat_id,
                "text": message.text,
                "reply_markup": message.reply_markup,
            },
        )
        async with self.session.get(send_url) as response:
            data = await response.json()
            self.logger.info(data)

        delete_message_task = asyncio.create_task(
            self.delete_message(message.chat_id, data["result"]["message_id"])
        )
        check_users_task = asyncio.create_task(
            self.check_users_in_session_enough(update)
        )
        delete_message_task.add_done_callback(self._done_callback)
        check_users_task.add_done_callback(self._done_callback)

    async def delete_message(self, chat_id, message_id) -> None:
        await asyncio.sleep(self.seconds)

        delete_url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="deleteMessage",
            params={"chat_id": chat_id, "message_id": message_id},
        )
        async with self.session.get(delete_url) as response:
            delete_data = await response.json()
            self.logger.info(delete_data)

    async def check_users_in_session_enough(self, update):
        await asyncio.sleep(self.seconds)

        number_of_users = (
            await self.app.store.user.get_amount_of_users_in_session(
                update.message.chat.id_
            )
        )
        if number_of_users < 2:
            await self.send_message(
                Message(
                    chat_id=update.message.chat.id_,
                    text="Недостаточно участников...",
                )
            )
            await self.app.store.user.stop_game_session(update)
        else:
            fsm = self.app.store.bot_manager.fsm
            fsm.state = fsm.transitions[fsm.state]["next_state"]
            await fsm.launch_func(fsm.state, update)

    async def send_message(self, message):
        send_url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="sendMessage",
            params={"chat_id": message.chat_id, "text": message.text},
        )
        async with self.session.get(send_url) as response:
            data = await response.json()
            self.logger.info(data)

    async def get_profile_photo(self, user_id, limit=1) -> list:
        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="getUserProfilePhotos",
            params={"user_id": user_id, "limit": limit},
        )

        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info(data)
            return data["result"]["photos"]

    async def notify_about_participation(self, callback_query, message) -> None:
        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="answerCallbackQuery",
            params={
                "callback_query_id": callback_query.id_,
                "text": message,
            },
        )

        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info(data)

    async def send_photo(self, user: UserSession, chat_id):
        user_info = await self.app.store.user.get_user(user.user_id)
        username = (
            f"@{user_info.username}"
            if user_info.username
            else user_info.first_name
        )

        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="sendPhoto",
            params={
                "chat_id": chat_id,
                "photo": user.file_id,
                "caption": username,
            },
        )

        async with self.session.get(url) as response:
            data = await response.json()
            self.logger.info(data)

    async def send_poll(self, update, first_user, second_user):
        usernames = []
        for user in (first_user, second_user):
            user_info = await self.app.store.user.get_user(user.user_id)
            usernames.append(
                f"@{user_info.username}"
                if user_info.username
                else user_info.first_name
            )

        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="sendPoll",
            params={
                "chat_id": update.message.chat.id_,
                "question": "Какое фото больше нравится?",
                "options": json.dumps(usernames),
            },
        )

        async with self.session.get(url) as response:
            poll = await response.json()
            self.logger.info(poll)

        await asyncio.sleep(self.seconds)

        poll_answer = await self.stop_poll(update, poll["result"]["message_id"])
        poll_answer["poll"] = poll_answer["result"]
        update = get_poll_answer_from_update(poll_answer)
        await self.get_poll_answers(first_user.id_, second_user.id_, update)

    async def stop_poll(self, update, message_id):
        url = self._build_query(
            host=API_PATH,
            token=self.app.config.bot.token,
            method="stopPoll",
            params={
                "chat_id": update.message.chat.id_,
                "message_id": message_id,
            },
        )

        async with self.session.get(url) as response:
            poll = await response.json()
            self.logger.info(poll)
            return poll

    async def get_poll_answers(self, first_id, second_id, update):
        self.logger.info(update)
        first_user, second_user = update.poll.options

        if first_user.voter_count > second_user.voter_count:
            first_points = 1
            second_points = 0
        elif first_user.voter_count < second_user.voter_count:
            first_points = 0
            second_points = 1
        else:
            first_points = 1
            second_points = 1

        await self.app.store.user.set_points(
            first_id, second_id, first_points, second_points
        )
