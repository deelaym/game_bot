from aiohttp.web_app import Application

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    from app.tg_bot.routes import setup_routes as tg_bot_setup_routes

    tg_bot_setup_routes(app)
