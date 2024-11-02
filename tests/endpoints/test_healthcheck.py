from unittest import mock
from unittest.mock import ANY

import pytest


def test_healthcheck(client):
    response = client.get('/healthcheck')
    assert response.status_code == 200
    assert response.json() == {'app': 'ok', 'db': 'ok', 'version': ANY}
