from app.tg_bot.views import GetUserPhotoFileIdsView


def setup_routes(app):
    app.router.add_view("/get.user.photos", GetUserPhotoFileIdsView)
