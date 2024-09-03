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
            'Authorization': 'Bearer anykey'
        },
    )

    assert response.status_code == 200
