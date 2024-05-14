class FSM:
    def __init__(self,  app, state=None):
        self.app = app
        self.state = state
        self.transitions = {
            "start": {"next_state": "registration", "func": self.app.store.bot_manager.start_button},
            "registration": {"next_state": "round", "func": self.app.store.user.add_user_to_session},
            "round": {"next_state": "stop", "func": self.app.store.bot_manager.start_round},
            # "poll_answers": {"next_state": "round", "func": self.app.store.tg_bot.get_poll_answers},
            "stop": {"next_state": None, "func": self.app.store.user.stop_game_session},
        }

    async def launch_func(self, state, *args, **kwargs):
        transition = self.transitions.get(state, None)
        if transition:
            self.state = state
            await transition["func"](*args, **kwargs)
        else:
            raise ValueError
