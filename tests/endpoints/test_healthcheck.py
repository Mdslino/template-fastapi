from unittest.mock import ANY
from unittest import mock

import pytest


def test_healthcheck(client):
    response = client.get('/healthcheck')
    assert response.status_code == 200
    assert response.json() == {'app': 'ok', 'db': 'ok', 'version': ANY}


@pytest.mark.vcr()
def test_authenticated_healthcheck(client):
    response = client.get(
        '/auth-healthcheck',
        headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6IlZCeTZzSzVXdTNoelhFN04iLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3JjZXd2ZXp2cWh5a2t6a2N1dWlrLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIxYjI3OGNjYi05ZWJiLTRhOTYtYjdlZi01NzZiNTdhMTg5MzEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzI1Mzc3MzMzLCJpYXQiOjE3MjUzNzM3MzMsImVtYWlsIjoibWRzbGlub0BnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7fSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTcyNTM3MzczM31dLCJzZXNzaW9uX2lkIjoiM2VhZDQwMGYtYWY5YS00YzdkLTk0ZGQtM2VlOGRjNDdlYmE3IiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.wXVsiL4lFiMGraX4je_G974zpr3bXIPv2__SotMo5D0'
        },
    )

    assert response.status_code == 200
