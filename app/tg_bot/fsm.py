from logging import getLogger

from app.tg_bot.dataclasses import Chat, MessageObject, Update


class FSM:
    def __init__(self, app, state=None):
        self.app = app
        self.state = state
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
                "func": self.app.store.user.get_winners,
            },
            None: {
                "next_state": None,
                "func": self.logger.debug,
            },
        }
        for (
            game
        ) in await self.app.store.user.get_all_in_progress_game_sessions():
            if game.state:
                await self.transitions[game.state]["func"](
                    Update(message=MessageObject(chat=Chat(id_=game.chat_id)))
                )

    async def launch_func(self, state, *args, **kwargs):
        transition = self.transitions.get(state, None)
        if transition:
            self.state = state
            await transition["func"](*args, **kwargs)
        else:
            raise ValueError(state)
