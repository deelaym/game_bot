from aiohttp_apispec import docs, request_schema, response_schema

from admin_app.tg_bot.schemes import TimeSchema
from admin_app.web.admin_app import View
from admin_app.web.mw import require_login
from admin_app.web.schemes import OkResponseSchema
from admin_app.web.utils import json_response


@require_login
class SetTimeOfPolls(View):
    @docs(
        tags=["game_session"],
        summary="Set voting time",
        description="Set voting time",
    )
    @request_schema(TimeSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        await self.store.user.set_seconds(self.data["seconds"])
        return json_response()
