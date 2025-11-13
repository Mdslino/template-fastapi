"""Tests for User domain entity."""

from datetime import datetime

import pytest

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username


class TestUser:
    """Test User domain entity."""

    def test_create_user(self):
        """Test creating a user with factory method."""
        username = Username(value='john_doe')
        email = Email(value='john@example.com')

        user = User.create(
            username=username, email=email, full_name='John Doe'
        )

        assert user.id is not None
        assert user.username == username
        assert user.email == email
        assert user.full_name == 'John Doe'
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_create_user_without_full_name(self):
        """Test creating a user without full name."""
        username = Username(value='jane_doe')
        email = Email(value='jane@example.com')

        user = User.create(username=username, email=email)

        assert user.full_name is None
        assert user.is_active is True

    def test_deactivate_user(self):
        """Test deactivating a user."""
        username = Username(value='john_doe')
        email = Email(value='john@example.com')
        user = User.create(username=username, email=email)

        assert user.is_active is True

        user.deactivate()

        assert user.is_active is False

    def test_activate_user(self):
        """Test activating a user."""
        username = Username(value='john_doe')
        email = Email(value='john@example.com')
        user = User.create(username=username, email=email)

        user.deactivate()
        assert user.is_active is False

        user.activate()
        assert user.is_active is True

    def test_update_profile_full_name(self):
        """Test updating user full name."""
        username = Username(value='john_doe')
        email = Email(value='john@example.com')
        user = User.create(username=username, email=email, full_name='John')

        user.update_profile(full_name='John Doe')

        assert user.full_name == 'John Doe'

    def test_update_profile_email(self):
        """Test updating user email."""
        username = Username(value='john_doe')
        old_email = Email(value='john@example.com')
        new_email = Email(value='johndoe@example.com')

        user = User.create(username=username, email=old_email)

        user.update_profile(email=new_email)

        assert user.email == new_email

    def test_update_profile_both(self):
        """Test updating both full name and email."""
        username = Username(value='john_doe')
        old_email = Email(value='john@example.com')
        new_email = Email(value='johndoe@example.com')

        user = User.create(
            username=username, email=old_email, full_name='John'
        )

        user.update_profile(full_name='John Doe', email=new_email)

        assert user.full_name == 'John Doe'
        assert user.email == new_email

    def test_updated_at_changes(self):
        """Test that updated_at changes after modifications."""
        username = Username(value='john_doe')
        email = Email(value='john@example.com')
        user = User.create(username=username, email=email)

        original_updated_at = user.updated_at

        # Small delay to ensure different timestamp
        import time

        time.sleep(0.01)

        user.update_profile(full_name='John Doe')

        assert user.updated_at > original_updated_at
