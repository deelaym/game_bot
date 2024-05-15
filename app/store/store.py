from app.store.database.database import Database
from app.tg_bot.manager import BotManager


class Store:
    def __init__(self, app, *args, **kwargs):
        from app.users.accessor import UserAccessor
        from app.tg_bot.accessor import TgApiAccessor

        self.user = UserAccessor(app)
        self.tg_bot = TgApiAccessor(app)
        self.bot_manager = BotManager(app)


def setup_store(app):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
