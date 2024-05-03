from aiohttp.web_app import Application

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    import app.users.routes

    app.users.routes.register_urls(app)
