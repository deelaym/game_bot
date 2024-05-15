from app.users.views import (
    AddUserToSessionView,
    ChangeUserPhotoView,
    DeleteUserFromSessionView,
)


def setup_routes(app):
    app.router.add_view("/add.user.to.session", AddUserToSessionView)
    app.router.add_view("/change.user.photo", ChangeUserPhotoView)
    app.router.add_view("/delete.user.from.session", DeleteUserFromSessionView)
