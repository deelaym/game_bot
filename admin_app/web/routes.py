from aiohttp.web_app import Application

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    from admin_app.admin.routes import setup_routes as admin_setup_routes

    admin_setup_routes(app)
