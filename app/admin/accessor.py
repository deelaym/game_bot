from aiohttp.web_exceptions import HTTPBadRequest, HTTPForbidden
from sqlalchemy import select

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor
from app.web.utils import hash_password


class AdminAccessor(BaseAccessor):
    async def connect(self, app) -> None:
        self.app = app
        self.logger.info("connect to database")
        # first_admin = self.app.config.admin
        # await self.create_admin(email=first_admin.email,
        # password=first_admin.password)

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
