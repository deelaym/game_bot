from aiohttp.test_utils import TestClient

from admin_app.users.models import SessionModel, UserModel


class TestUserSessionView:
    async def test_success_add_user(self, auth_cli: TestClient, game_session_1: SessionModel):
        response = await auth_cli.post("/session.user", json={
            "user_id": 66666666,
            "first_name": "FirstName",
            "username": "username",
            "session_id": game_session_1.id_,
            "file_id": "file_id"
        })

        assert response.status == 200

        data = await response.json()

        assert data["data"] == {
            "id_": data["data"]["id_"],
            "user_id": 66666666,
            "session_id": game_session_1.id_,
            "in_game": True,
            "points": 0,
            "file_id": "file_id",
        }

    async def test_wrong_session_id(self, auth_cli: TestClient):
        response = await auth_cli.post("/session.user", json={
            "user_id": 66666666,
            "first_name": "FirstName",
            "username": "username",
            "session_id": 42424242,
            "file_id": "file_id"
        })

        assert response.status == 400


