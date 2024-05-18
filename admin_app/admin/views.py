import aiohttp_session
from aiohttp_apispec import docs, request_schema, response_schema

from admin_app.admin.schemes import AdminSchema
from admin_app.web.admin_app import View
from admin_app.web.mw import require_login
from admin_app.web.utils import json_response


class AdminLoginView(View):
    @docs(
        tags=["admin"], summary="Login for admin", description="Login for admin"
    )
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        admin = await self.request.app.store.admin.login_admin(
            email=self.data["email"], password=self.data["password"]
        )
        session = await aiohttp_session.new_session(request=self.request)
        admin_data = AdminSchema().dump(admin)
        session["admin"] = admin_data
        return json_response(data=admin_data)


@require_login
class AdminCurrentView(View):
    @docs(tags=["admin"], summary="Current admin", description="Current admin")
    @response_schema(AdminSchema, 200)
    async def get(self):
        session = await aiohttp_session.get_session(request=self.request)
        admin = await self.store.admin.get_by_email(session["admin"]["email"])
        return json_response(data=AdminSchema().dump(admin))
