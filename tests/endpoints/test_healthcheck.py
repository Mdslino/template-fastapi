from typing import Any


def test_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"app": "ok", "db": "ok", "version": Any}
