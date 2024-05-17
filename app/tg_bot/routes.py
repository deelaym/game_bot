from app.tg_bot.views import GetUserPhotoFileIdsView, SetTimeOfPolls


def setup_routes(app):
    app.router.add_view("/get.user.photos", GetUserPhotoFileIdsView)
    app.router.add_view("/set.time", SetTimeOfPolls)
