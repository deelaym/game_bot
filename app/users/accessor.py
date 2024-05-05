from sqlalchemy.exc import IntegrityError

from app.base.base_accessor import BaseAccessor
from app.users.models import SessionModel, UserModel


class UserAccessor(BaseAccessor):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    async def create_new_session(self, update):
        game_session = SessionModel(
            id_=update.message.message_id + 1, chat_id=update.message.chat.id_
        )
        async with self.app.database.session() as session:
            session.add(game_session)
            await session.commit()
        return game_session

    async def add_user_to_session(self, update):
        async with self.app.database.session() as session:
            existing_user = await session.get(
                UserModel, update.callback_query.from_.id_
            )
            game_session = await session.get(
                SessionModel, update.message.message_id
            )
            if existing_user:
                existing_user.sessions.append(game_session)
            else:
                user = UserModel(
                    id_=update.callback_query.from_.id_,
                    first_name=update.callback_query.from_.first_name,
                    username=update.callback_query.from_.username,
                )
                user.sessions.append(game_session)
                session.add(user)
            try:
                await session.commit()
            except IntegrityError as e:
                self.logger.error(str(e))

        return existing_user if existing_user else user
