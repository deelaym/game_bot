from aiohttp.web_exceptions import HTTPBadRequest, HTTPForbidden
from sqlalchemy import select

from admin_app.admin.models import AdminModel
from admin_app.base.base_accessor import BaseAccessor
from admin_app.web.utils import hash_password


class AdminAccessor(BaseAccessor):
    async def connect(self, app) -> None:
        self.app = app
        self.logger.info("connect to database")
        if not await self.get_by_email(self.app.config.admin.email):
            await self.create_admin(
                email=self.app.config.admin.email,
                password=self.app.config.admin.password,
            )

    async def login_admin(self, email: str, password: str) -> AdminModel:
        admin = await self.get_by_email(email)
        if admin:
            if admin.password == hash_password(password):
                return admin
            raise HTTPBadRequest
        raise HTTPForbidden

    async def get_by_email(self, email: str) -> AdminModel | None:
        async with self.app.database.session() as session:
            query = select(AdminModel).where(AdminModel.email == email)
            return await session.scalar(query)

    async def create_admin(self, email: str, password: str) -> AdminModel:
        admin = AdminModel(email=email, password=hash_password(password))

        async with self.app.database.session() as session:
            session.add(admin)
            await session.commit()
            self.logger.info("Admin created")
        return admin
