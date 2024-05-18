from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

__all__ = ("Application",)


from admin_app.store import Store
from admin_app.store.database.database import Database
from admin_app.store.store import setup_store
from admin_app.web.config import setup_config
from admin_app.web.logger import setup_logging
from admin_app.web.mw import setup_middlewares


class Application(AiohttpApplication):
    config = None
    store = None
    database = None


class Request(AiohttpRequest):
    from admin_app.admin.models import AdminModel  # noqa: PLC0415

    admin: AdminModel | None = None

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


admin_app = Application()


def setup_app(config_path: str) -> Application:
    from admin_app.admin.routes import setup_routes  # noqa: PLC0415

    setup_logging(admin_app)
    setup_config(admin_app, config_path)
    session_setup(
        admin_app, EncryptedCookieStorage(admin_app.config.session.key)
    )
    setup_routes(admin_app)
    setup_aiohttp_apispec(
        admin_app,
        title="Telegram Photo Contest Bot",
        url="/docs/json",
        swagger_path="/docs",
    )
    setup_middlewares(admin_app)
    setup_store(admin_app)
    return admin_app
