import asyncio
from functools import partial
from logging import getLogger

from app.tg_bot.dataclasses import Chat, MessageObject, Update


class FSM:
    def __init__(self, app, state=None):
        self.app = app
        self.transitions = {}
        self.logger = getLogger("fsm")

        app.on_startup.append(self.connect)

    async def connect(self, app):
        self.transitions = {
            "start": {
                "next_state": "registration",
                "func": self.app.store.bot_manager.start_button,
            },
            "registration": {
                "next_state": "round",
                "func": self.app.store.user.add_user_to_session,
            },
            "round": {
                "next_state": "stop",
                "func": self.app.store.bot_manager.start_round,
            },
            "stop": {
                "next_state": None,
                "func": self.app.store.user.stop_game_session,
            },
            "about": {
                "next_state": None,
                "func": partial(self.app.store.user.get_winners, about=True),
            },
        }
        games_in_progress = (
            await self.app.store.user.get_all_in_progress_game_sessions()
        )
        tasks = []
        for game in games_in_progress:
            if game.state:
                task = self.transitions[game.state]["func"](
                    Update(message=MessageObject(chat=Chat(id_=game.chat_id)))
                )
                tasks.append(task)
        await asyncio.gather(*tasks)

    async def launch_func(self, state, *args, **kwargs):
        transition = self.transitions.get(state, None)
        if transition:
            await transition["func"](*args, **kwargs)
        else:
            raise ValueError(state)

    async def get_next_state(self, chat_id):
        current_state = await self.app.store.user.get_state(chat_id)
        state = self.transitions[current_state]["next_state"]
        await self.app.store.user.set_state(chat_id, state)
        return state
