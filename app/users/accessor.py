from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.tg_bot.dataclasses import Message
from app.users.models import SessionModel, UserModel, UserSession


class UserAccessor(BaseAccessor):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    async def create_new_session(self, update):
        game_session = SessionModel(chat_id=update.message.chat.id_)
        async with self.app.database.session() as session:
            session.add(game_session)
            await session.commit()
        return game_session

    async def add_user_to_session(self, update) -> None:
        async with self.app.database.session() as session:
            photo = await self.app.store.tg_bot.get_profile_photo(
                update.callback_query.from_.id_
            )
            if photo:
                existing_user = await self.get_user(
                    update.callback_query.from_.id_
                )
                game_session = (
                    await session.execute(
                        select(SessionModel)
                        .where(
                            SessionModel.chat_id == update.message.chat.id_,
                            SessionModel.in_progress,
                        )
                        .options(joinedload(SessionModel.users))
                    )
                ).scalar()

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

                user_session = (
                    await session.execute(
                        select(UserSession).where(
                            UserSession.user_id
                            == update.callback_query.from_.id_,
                            UserSession.session_id == game_session.id_,
                        )
                    )
                ).scalar()
                user_session.file_id = photo[0][0]["file_id"]
                self.logger.info(user_session.file_id)

                try:
                    await session.commit()
                    await self.app.store.tg_bot.notify_about_participation(
                        update.callback_query, "Вы участвуете в конкурсе!"
                    )
                except IntegrityError as e:
                    self.logger.error(e)
                return existing_user if existing_user else user

            await self.app.store.tg_bot.notify_about_participation(
                update.callback_query,
                "У вас нет фото, \
                как можно участвовать в фото конкурсе без фото!?",
            )
            return None

    async def stop_game_session(self, update) -> None:
        async with self.app.database.session() as session:
            current_game_session = await session.scalar(
                select(SessionModel).where(
                    SessionModel.chat_id == update.message.chat.id_,
                    SessionModel.in_progress,
                )
            )
            if current_game_session:
                if (
                    await self.get_amount_of_users_in_session(
                        current_game_session.chat_id
                    )
                    > 1
                ):
                    await self.get_winners(update, current_game_session.id_)

                current_game_session.in_progress = False
                await session.commit()

                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text="Конкурс завершен!",
                    )
                )
            else:
                await self.app.store.tg_bot.send_message(
                    Message(
                        chat_id=update.message.chat.id_,
                        text="Сейчас нет никаких конкурсов!",
                    )
                )
            fsm = self.app.store.bot_manager.fsm
            fsm.state = fsm.transitions[fsm.state]["next_state"]

    async def get_amount_of_users_in_session(self, chat_id) -> int:
        async with self.app.database.session() as session:
            current_game_session = await session.scalar(
                select(SessionModel).where(
                    SessionModel.chat_id == chat_id,
                    SessionModel.in_progress,
                )
            )
            users_amount = await session.scalar(
                select(func.count(UserSession.user_id)).where(
                    UserSession.session_id == current_game_session.id_
                )
            )
            self.logger.info(users_amount)
            return users_amount

    async def get_winners(self, update, session_id=None) -> None:
        async with self.app.database.session() as session:
            if session_id is None:
                game_session = await self.get_game_session(
                    update.message.chat.id_
                )
                session_id = game_session.id_

            users_in_session = (
                await session.scalars(
                    select(UserSession)
                    .where(
                        UserSession.session_id == session_id,
                        UserSession.in_game,
                    )
                    .order_by(UserSession.points.desc())
                    .limit(3)
                )
            ).all()

            self.logger.info(users_in_session)
            if len(users_in_session) == 1:
                user_profile = await self.get_user(users_in_session[0].user_id)
                username = (
                    f"@{user_profile.username}"
                    if user_profile.username
                    else user_profile.first_name
                )
                if self.app.store.bot_manager.fsm.state == "about":
                    text = f"Победитель прошлого конкурса: {username}"
                else:
                    text = f"Победитель: {username}"
            else:
                text = f"Топ-{len(users_in_session)}:"
                for i, user in enumerate(users_in_session, start=1):
                    user_profile = await self.get_user(user.user_id)
                    username = (
                        f"@{user_profile.username}"
                        if user_profile.username
                        else user_profile.first_name
                    )
                    text += f"\n {i}. {username} Побед: {user.points}"

            await self.app.store.tg_bot.send_message(
                Message(chat_id=update.message.chat.id_, text=text)
            )

            if len(users_in_session) == 1:
                await self.app.store.tg_bot.send_photo(
                    users_in_session[0], update.message.chat.id_
                )

    async def get_all_in_game_users(self, chat_id):
        async with self.app.database.session() as session:
            game_session = await self.get_game_session(chat_id)
            return (
                await session.scalars(
                    select(UserSession).where(
                        UserSession.session_id == game_session.id_,
                        UserSession.in_game,
                        UserSession.points == game_session.round_number - 1,
                    )
                )
            ).all()

    async def set_round_number(self, chat_id):
        async with self.app.database.session() as session:
            game_session = await self.get_game_session(chat_id)
            game_session.round_number += 1
            session.add(game_session)
            await session.commit()
            return game_session

    async def set_points(self, first_id, second_id, *points):
        async with self.app.database.session() as session:
            for id_, point in zip([first_id, second_id], points, strict=True):
                user_session = await session.get(UserSession, id_)
                user_session.points += point
            await session.commit()

    async def get_winner_in_pair(self, first_user, second_user):
        async with self.app.database.session() as session:
            first_user = await session.get(UserSession, first_user.id_)
            first_user_info = await self.get_user(first_user.user_id)
            second_user = await session.get(UserSession, second_user.id_)
            second_user_info = await self.get_user(first_user.user_id)

            self.logger.info(first_user_info)

            if first_user.points > second_user.points:
                second_user.in_game = False
                await session.commit()
                return (
                    f"@{first_user_info.username}"
                    if first_user_info.username
                    else first_user_info.first_name
                )
            if first_user.points < second_user.points:
                first_user.in_game = False
                await session.commit()
                return (
                    f"@{second_user_info.username}"
                    if second_user_info.username
                    else second_user_info.first_name
                )
            return None

    async def get_user(self, user_id):
        async with self.app.database.session() as session:
            return await session.get(UserModel, user_id)

    async def get_game_session(self, chat_id):
        async with self.app.database.session() as session:
            return (
                await session.scalars(
                    select(SessionModel)
                    .where(SessionModel.chat_id == chat_id)
                    .order_by(SessionModel.id_.desc())
                )
            ).first()

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
            game_session.users.append(user)
            session.add(game_session)
            await session.commit()

    async def add_user_photo(self, user_id, session_id, photo):
        async with self.app.database.session() as session:
            user_session = (
                await session.execute(
                    select(UserSession).where(
                        UserSession.user_id == user_id,
                        UserSession.session_id == session_id,
                    )
                )
            ).scalar()
            user_session.file_id = photo
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
