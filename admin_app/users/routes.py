from admin_app.users.views import (
    UserSessionView,
    ChangeUserPhotoView,
    CreateGameSessionView,
    GetGameStatisticsView,
)


def setup_routes(app):
    app.router.add_view("/session.user", UserSessionView)
    app.router.add_view("/user.photo", ChangeUserPhotoView)
    app.router.add_view("/session", CreateGameSessionView)
    app.router.add_view("/game.statistics", GetGameStatisticsView)
