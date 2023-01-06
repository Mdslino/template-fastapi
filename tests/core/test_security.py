from datetime import timedelta
from uuid import uuid4

import pytest

from app.core import security


@pytest.mark.parametrize("time_delta", [None, timedelta(minutes=1)])
def test_create_access_token(time_delta):
    access_token = security.create_access_token(
        subject=uuid4(), expires_delta=time_delta
    )

    assert access_token is not None
    assert isinstance(access_token, str)


def test_verify_password():
    password = "password"
    hashed_password = security.get_password_hash(password)

    assert security.verify_password(password, hashed_password) is True
    assert security.verify_password("wrong_password", hashed_password) is False
