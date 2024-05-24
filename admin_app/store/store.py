from admin_app.store.database.database import Database


class Store:
    def __init__(self, app, *args, **kwargs):
        from admin_app.admin.accessor import AdminAccessor
        from admin_app.users.accessor import UserAccessor

        self.user = UserAccessor(app)
        self.admin = AdminAccessor(app)


def setup_store(app):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
