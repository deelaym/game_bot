from aiohttp.web_exceptions import HTTPBadRequest
from aiohttp_apispec import docs, request_schema, response_schema
from sqlalchemy.exc import IntegrityError

from admin_app.tg_bot.dataclasses import Chat, MessageObject, Update
from admin_app.users.schema import (
    SessionSchema,
    StatisticsSchema,
    UserSessionSchema,
)
from admin_app.web.admin_app import View
from admin_app.web.mw import require_login
from admin_app.web.schemes import OkResponseSchema
from admin_app.web.utils import json_response


@require_login
class UserSessionView(View):
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

        if game_session:
            await self.store.user.add_user_to_session_manual(user, game_session)
            user_session = await self.store.user.add_user_photo(
                user.id_, game_session.id_, self.data["file_id"]
            )
        else:
            raise HTTPBadRequest

        return json_response(data=UserSessionSchema().dump(user_session))

    @docs(
        tags=["game_session"],
        summary="Removing a user from a game session",
        description="Removing a user from a game session",
    )
    @request_schema(UserSessionSchema)
    @response_schema(OkResponseSchema, 200)
    async def delete(self):
        await self.store.user.delete_user_from_session(
            self.data["user_id"], self.data["session_id"]
        )
        return json_response()


@require_login
class ChangeUserPhotoView(View):
    @docs(
        tags=["game_session"],
        summary="Сhange a photo for an existing user in the session",
        description="Сhange a photo for an existing user in the session",
    )
    @request_schema(UserSessionSchema)
    @response_schema(UserSessionSchema, 200)
    async def put(self):
        user_session = await self.store.user.add_user_photo(
            self.data["user_id"], self.data["session_id"], self.data["file_id"]
        )
        return json_response(data=UserSessionSchema().dump(user_session))


@require_login
class CreateGameSessionView(View):
    @docs(
        tags=["game_session"],
        summary="Creating a game session",
        description="Creating a game session",
    )
    @request_schema(SessionSchema)
    @response_schema(SessionSchema, 200)
    async def post(self):
        game_session = await self.store.user.create_new_session(
            Update(message=MessageObject(chat=Chat(id_=self.data["chat_id"])))
        )
        return json_response(data=SessionSchema().dump(game_session))


@require_login
class GetGameStatisticsView(View):
    @docs(
        tags=["game_session"],
        summary="Send game statistics",
        description="Send game statistics",
    )
    @request_schema(SessionSchema)
    @response_schema(StatisticsSchema, 200)
    async def get(self):
        statistics = await self.store.user.get_game_statistics(
            self.data["session_id"]
        )
        return json_response(data=StatisticsSchema().dump(statistics))
