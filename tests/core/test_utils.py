import pytest
from pydantic import ValidationError

from app.core.utils import hide_email


def test_hide_email_success(faker):
    email = faker.email()
    masked_email = hide_email(email)

    assert masked_email != email
    assert "." in masked_email
    assert "*" in masked_email
    assert "@" in masked_email
    assert masked_email.split("@")[1] == email.split("@")[1]
    assert len(masked_email.split("@")[0]) == len(email.split("@")[0])


def test_hide_email_with_empty_email():
    with pytest.raises(ValidationError):
        hide_email("")
