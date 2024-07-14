from admin_app.store import Store
from admin_app.web.config import Config


class TestAdminAccessor:
    async def test_admin_created_on_startup(
        self, store: Store, config: Config
    ) -> None:
        admin = await store.admin.get_by_email(config.admin.email)

        assert admin is not None
        assert admin.email == config.admin.email
        assert admin.password != config.admin.password
        assert admin.id == 1
