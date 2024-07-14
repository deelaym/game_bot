from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from admin_app.base.base_accessor import BaseAccessor
from admin_app.users.models import SessionModel, UserModel, UserSession
from admin_app.users.schema import UserSessionSchema


class UserAccessor(BaseAccessor):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    async def create_new_session(self, update):
        game_session = SessionModel(chat_id=update.message.chat.id_)
        async with self.app.database.session() as session:
            session.add(game_session)
            await session.commit()
        return game_session

    async def get_user(self, user_id):
        async with self.app.database.session() as session:
            return await session.get(UserModel, user_id)

    async def create_user(self, id_, first_name, username):
        user = UserModel(id_=id_, first_name=first_name, username=username)

        async with self.app.database.session() as session:
            session.add(user)
            await session.commit()
        return user

    async def get_game_session_by_id(self, session_id):
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(SessionModel)
                    .where(SessionModel.id_ == session_id)
                    .options(joinedload(SessionModel.users))
                )
            ).scalar()

    async def add_user_to_session_manual(self, user, game_session):
        async with self.app.database.session() as session:
            game_session = await session.scalar(
                select(SessionModel)
                .where(
                    SessionModel.id_ == game_session.id_,
                )
                .options(joinedload(SessionModel.users))
            )
            user = await session.scalar(
                select(UserModel).where(UserModel.id_ == user.id_)
            )

            game_session.users.append(user)
            session.add(game_session)
            await session.commit()
            return game_session

    async def add_user_photo(self, user_id, session_id, file_id):
        async with self.app.database.session() as session:
            user_session = (
                await session.execute(
                    select(UserSession).where(
                        UserSession.user_id == user_id,
                        UserSession.session_id == session_id,
                    )
                )
            ).scalar()
            user_session.file_id = file_id
            await session.commit()
            return user_session

    async def delete_user_from_session(self, user_id, session_id):
        async with self.app.database.session() as session:
            await session.execute(
                delete(UserSession).where(
                    UserSession.user_id == user_id,
                    UserSession.session_id == session_id,
                )
            )
            await session.commit()

    async def get_all_users_in_session(self, session_id):
        async with self.app.database.session() as session:
            return (
                await session.scalars(
                    select(UserSession)
                    .where(UserSession.session_id == session_id)
                    .order_by(UserSession.points.desc())
                )
            ).all()

    async def get_game_statistics(self, session_id):
        game_session = await self.get_game_session_by_id(session_id)
        users = []
        for user in await self.get_all_users_in_session(game_session.id_):
            user_info = await self.get_user(user.user_id)
            user_schema = UserSessionSchema().load(
                {
                    "user_id": user.user_id,
                    "first_name": user_info.first_name,
                    "username": user_info.username,
                    "points": user.points,
                    "in_game": user.in_game,
                    "file_id": user.file_id,
                }
            )
            users.append(user_schema)

        return {
            "users": users,
            "chat_id": game_session.chat_id,
            "round_number": game_session.round_number,
            "in_progress": game_session.in_progress,
        }

    async def set_seconds(self, session_id, seconds):
        async with self.app.database.session() as session:
            game_session = await self.get_game_session_by_id(session_id)
            game_session.polls_time = seconds
            session.add(game_session)
            await session.commit()
            return game_session
