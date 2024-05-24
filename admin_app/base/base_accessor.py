from logging import getLogger


class BaseAccessor:
    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.logger = getLogger("accessor")

        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app):
        return

    async def disconnect(self, app):
        return
