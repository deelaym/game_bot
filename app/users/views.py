from aiohttp_apispec import docs, request_schema, response_schema
from sqlalchemy.exc import IntegrityError

from app.users.schema import UserSessionSchema
from app.web.app import View
from app.web.mw import require_login
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response


@require_login
class AddUserToSessionView(View):
    @docs(
        tags=["game_session"],
        summary="Add user to existing game session",
        description="Add user to existing game session",
    )
    @request_schema(UserSessionSchema)
    @response_schema(UserSessionSchema, 200)
    async def post(self):
        try:
            user = await self.store.user.create_user(
                self.data["user_id"],
                self.data["first_name"],
                self.data["username"],
            )
        except IntegrityError:
            user = await self.store.user.get_user(self.data["user_id"])

        game_session = await self.store.user.get_game_session_by_id(
            self.data["session_id"]
        )

        await self.store.user.add_user_to_session_manual(user, game_session)
        user_session = await self.store.user.add_user_photo(
            user.id_, game_session.id_, self.data["photo"]
        )

        return json_response(data=UserSessionSchema().dump(user_session))


@require_login
class ChangeUserPhotoView(View):
    @docs(
        tags=["game_session"],
        summary="Сhange a photo for an existing user in the session",
        description="Сhange a photo for an existing user in the session",
    )
    @request_schema(UserSessionSchema)
    @response_schema(UserSessionSchema, 200)
    async def post(self):
        user_session = await self.store.user.add_user_photo(
            self.data["user_id"], self.data["session_id"], self.data["photo"]
        )
        return json_response(data=UserSessionSchema().dump(user_session))


@require_login
class DeleteUserFromSessionView(View):
    @docs(
        tags=["game_session"],
        summary="Removing a user from a game session",
        description="Removing a user from a game session",
    )
    @request_schema(UserSessionSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        await self.store.user.delete_user_from_session(
            self.data["user_id"], self.data["session_id"]
        )
        return json_response()
