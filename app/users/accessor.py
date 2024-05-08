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
                SessionModel,
                update.message.message_id,
            )

            if existing_user:
                game_session.users.append(existing_user)
            else:
                user = UserModel(
                    id_=update.callback_query.from_.id_,
                    first_name=update.callback_query.from_.first_name,
                    username=update.callback_query.from_.username,
                )
                game_session.users.append(user)
                session.add(user)

            try:
                await session.commit()
                await self.app.store.tg_bot.notify_about_participation(
                    update.callback_query
                )
            except IntegrityError as e:
                self.logger.error(e)

        return existing_user if existing_user else user
