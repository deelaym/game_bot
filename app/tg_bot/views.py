from aiohttp_apispec import docs, request_schema, response_schema

from app.tg_bot.schemes import FileIdSchema, PhotoListSchema
from app.users.schema import UserSchema
from app.web.app import View
from app.web.utils import json_response


class GetUserPhotoFileIdsView(View):
    @docs(
        tags=["tg_bot"],
        summary="Get all user photo ids",
        description="Get all user photo ids",
    )
    @request_schema(UserSchema)
    @response_schema(PhotoListSchema, 200)
    async def post(self):
        photos = await self.store.tg_bot.get_profile_photo(
            self.data["user_id"], limit=100
        )
        photo_file_ids = [
            FileIdSchema().load({"file_id": photo[0]["file_id"]})
            for photo in photos
        ]
        return json_response(PhotoListSchema().dump({"photos": photo_file_ids}))

