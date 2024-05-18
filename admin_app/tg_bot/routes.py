from admin_app.tg_bot.views import SetTimeOfPolls


def setup_routes(app):
    app.router.add_view("/set.time", SetTimeOfPolls)
