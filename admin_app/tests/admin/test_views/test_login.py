from aiohttp.test_utils import TestClient

from admin_app.web.config import Config


class TestAdminLoginView:
    async def test_success_when_good_credentials(self, cli: TestClient, config: Config) -> None:
        response = await cli.post("/admin.login", json={
            "email": config.admin.email,
            "password": config.admin.password
        })

        assert response.status == 200

        data = await response.json()
        assert data == {
            "status": "ok",
            "data": {
                "id": 1,
                "email": config.admin.email
            }
        }

    async def test_bad_request_when_missed_email(self, cli: TestClient, config: Config) -> None:
        response = await cli.post("/admin.login",
                                  json={
                                      "password": config.admin.password
                                  })
        assert response.status == 422

        data = await response.json()

        assert data == {
            "status": "Unprocessable Entity",
            "message": "Unprocessable Entity",
            "data": '{"json": {"email": ["Missing data for required field."]}}'
        }

    async def test_bad_request_with_wrong_email(self, cli: TestClient, config: Config) -> None:
        response = await cli.post("/admin.login",
                                  json={
                                      "email": "querty@admin.com",
                                      "password": config.admin.password
                                  })
        assert response.status == 403

        data = await response.json()

        assert data == {
            "status": "Forbidden",
            "message": "Forbidden",
            "data": "403: Forbidden"
        }




    async def test_bad_request_with_wrong_password(self, cli: TestClient, config: Config) -> None:
        response = await cli.post("/admin.login",
                                  json={
                                      "email": config.admin.email,
                                      "password": "querty"
                                  })
        assert response.status == 400

        data = await response.json()

        assert data == {
            "status": "Bad Request",
            "message": "Bad Request",
            "data": "400: Bad Request"
        }