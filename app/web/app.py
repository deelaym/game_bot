from aiohttp.web import (
    Application as AiohttpApplication,
)
from aiohttp_apispec import setup_aiohttp_apispec

from app.web.logger import setup_logging

from .config import setup_config
from .mw import setup_middlewares
from .routes import setup_routes

__all__ = ("Application",)

from ..store.store import setup_store


class Application(AiohttpApplication):
    config = None
    store = None
    database = None


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    # session_setup(app, EncryptedCookieStorage(app.config.session.key))
    setup_routes(app)
    setup_aiohttp_apispec(
        app,
        title="Telegram Photo Contest Bot",
        url="/docs/json",
        swagger_path="/docs",
    )
    setup_middlewares(app)
    setup_store(app)
    return app
