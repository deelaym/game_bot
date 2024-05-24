from admin_app.users.models import SessionModel, UserModel, UserSession


def session_to_dict(game_session: SessionModel) -> dict:
    return {
        "id_": game_session.id_,
        "chat_id": game_session.chat_id,
        "in_progress": game_session.in_progress,
        "round_number": game_session.round_number,
        "state": game_session.state,
        "message_id": game_session.message_id,
        "polls_time": game_session.polls_time,
    }


def user_to_dict(user: UserModel) -> dict:
    return {
        "id_": user.id_,
        "first_name": user.first_name,
        "username": user.username,
    }


def user_session_to_dict(user_session: UserSession):
    return {
        "id_": user_session.id_,
        "user_id": user_session.user_id,
        "session_id": user_session.session_id,
        "points": user_session.points,
        "in_game": user_session.in_game,
        "file_id": user_session.file_id,
    }
