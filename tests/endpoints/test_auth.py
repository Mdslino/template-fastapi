from tests.factories.user_factory import UserFactory

BASE_URL = f"/api/v1/auth"


def test_create_user(client, faker):
    email = faker.email()
    password = faker.password()
    payload = {"email": email, "password": password, "password2": password}
    response = client.post(
        f"{BASE_URL}/users/",
        json=payload,
    )
    assert response.status_code == 201
    response_json = response.json()
    assert response_json["email"] == email
    assert response_json["is_active"] is True
    assert response_json["external_id"]


def test_load_users(client, super_user_token):
    UserFactory.create_batch(2)
    response = client.get(
        f"{BASE_URL}/users/",
        headers={"Authorization": f"Bearer {super_user_token}"},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 3


def test_update_user(client, super_user_token, user_factory, faker):
    payload = {"email": faker.email()}

    response = client.patch(
        f"{BASE_URL}/users/{user_factory.external_id}",
        json=payload,
        headers={"Authorization": f"Bearer {super_user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == payload["email"]


def test_update_user_me(client, faker, user_token):
    payload = {"email": faker.email()}

    response = client.patch(
        f"{BASE_URL}/users/me",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == payload["email"]


def test_read_user_me(client, user_token):
    response = client.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()


def test_login(client, user_factory):
    payload = {
        "username": user_factory.email,
        "password": "password",
    }
    response = client.post(
        f"{BASE_URL}/token",
        data=payload,
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"
