import pytest


@pytest.mark.usefixtures("create_test_database")
class TestAuthEndpoints:
    @property
    def base_url(self):
        return f"/api/v1/auth"

    def test_create_user(self, client, faker):
        email = faker.email()
        password = faker.password()
        payload = {"email": email, "password": password, "password2": password}
        response = client.post(f"{self.base_url}/users/", json=payload)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["email"] == email
        assert response_json["is_active"] is True
        assert response_json["external_id"]
