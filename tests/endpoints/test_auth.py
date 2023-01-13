import pytest

from app.core.security import create_access_token
from tests.factories.user_factory import UserFactory


@pytest.mark.usefixtures("create_test_database")
class TestAuthEndpoints:
    @property
    def base_url(self):
        return f"/api/v1/auth"

    def test_create_user(self, client, faker):
        email = faker.email()
        password = faker.password()
        payload = {"email": email, "password": password, "password2": password}
        response = client.post(
            f"{self.base_url}/users/",
            json=payload,
        )
        assert response.status_code == 201
        response_json = response.json()
        assert response_json["email"] == email
        assert response_json["is_active"] is True
        assert response_json["external_id"]

    def test_load_users(self, client, super_user_token):
        UserFactory.create_batch(2)
        response = client.get(
            f"{self.base_url}/users/",
            headers={"Authorization": f"Bearer {super_user_token}"},
        )
        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == 3

    def test_update_user(self, client, super_user_token, user_factory, faker):
        payload = {"email": faker.email()}

        response = client.patch(
            f"{self.base_url}/users/{user_factory.external_id}",
            json=payload,
            headers={"Authorization": f"Bearer {super_user_token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == payload["email"]

    def test_update_user_me(self, client, faker, user_token):
        payload = {"email": faker.email()}

        response = client.patch(
            f"{self.base_url}/users/me",
            json=payload,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == payload["email"]
