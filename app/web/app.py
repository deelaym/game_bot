from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)

from app.web.logger import setup_logging

from .config import setup_config
from .mw import setup_middlewares
from .routes import setup_routes

__all__ = ("Application",)


from ..store.database.database import Database
from ..store.store import Store, setup_store


class Application(AiohttpApplication):
    config = None
    store = None
    database = None


class Request(AiohttpRequest):
    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self) -> Database:
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    setup_routes(app)
    setup_middlewares(app)
    setup_store(app)
    return app
