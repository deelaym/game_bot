from aiohttp.web_app import Application

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    from admin_app.admin.routes import setup_routes as admin_setup_routes
    from admin_app.tg_bot.routes import setup_routes as tg_setup_routes
    from admin_app.users.routes import setup_routes as user_setup_routes

    admin_setup_routes(app)
    user_setup_routes(app)
    tg_setup_routes(app)
