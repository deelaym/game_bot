from admin_app.users.views import (
    AddUserToSessionView,
    ChangeUserPhotoView,
    CreateGameSessionView,
    DeleteUserFromSessionView,
    GetGameStatisticsView,
)


def setup_routes(app):
    app.router.add_view("/add.user.to.session", AddUserToSessionView)
    app.router.add_view("/change.user.photo", ChangeUserPhotoView)
    app.router.add_view("/delete.user.from.session", DeleteUserFromSessionView)
    app.router.add_view("/create.session", CreateGameSessionView)
    app.router.add_view("/get.game.statistics", GetGameStatisticsView)
