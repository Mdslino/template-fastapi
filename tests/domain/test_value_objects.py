"""Tests for domain value objects."""

import pytest

from app.domain.exceptions import ValidationException
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username


class TestEmail:
    """Test Email value object."""

    def test_valid_email(self):
        """Test creating a valid email."""
        email = Email(value='test@example.com')
        assert email.value == 'test@example.com'
        assert str(email) == 'test@example.com'

    def test_invalid_email_no_at(self):
        """Test invalid email without @."""
        with pytest.raises(ValidationException) as exc_info:
            Email(value='invalid.email.com')
        assert 'Invalid email format' in str(exc_info.value)

    def test_invalid_email_no_domain(self):
        """Test invalid email without domain."""
        with pytest.raises(ValidationException) as exc_info:
            Email(value='test@')
        assert 'Invalid email format' in str(exc_info.value)

    def test_email_immutability(self):
        """Test that email is immutable."""
        email = Email(value='test@example.com')
        with pytest.raises(Exception):
            email.value = 'new@example.com'


class TestUsername:
    """Test Username value object."""

    def test_valid_username(self):
        """Test creating a valid username."""
        username = Username(value='john_doe')
        assert username.value == 'john_doe'
        assert str(username) == 'john_doe'

    def test_username_too_short(self):
        """Test username that is too short."""
        with pytest.raises(ValidationException) as exc_info:
            Username(value='ab')
        assert 'at least 3 characters' in str(exc_info.value)

    def test_username_too_long(self):
        """Test username that is too long."""
        with pytest.raises(ValidationException) as exc_info:
            Username(value='a' * 51)
        assert 'at most 50 characters' in str(exc_info.value)

    def test_username_invalid_characters(self):
        """Test username with invalid characters."""
        with pytest.raises(ValidationException) as exc_info:
            Username(value='john-doe')
        assert 'can only contain' in str(exc_info.value)

    def test_username_empty(self):
        """Test empty username."""
        with pytest.raises(ValidationException) as exc_info:
            Username(value='')
        assert 'cannot be empty' in str(exc_info.value)

    def test_username_immutability(self):
        """Test that username is immutable."""
        username = Username(value='john_doe')
        with pytest.raises(Exception):
            username.value = 'jane_doe'
