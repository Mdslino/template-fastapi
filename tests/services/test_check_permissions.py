"""
Tests for permission checking service.

Following TDD approach: tests define the expected behavior of the service.
"""

import pytest

from app.auth.exceptions import InsufficientPermissionsException
from app.auth.schemas import AuthenticatedUser
from app.auth.services.check_permissions import CheckPermissionsService


class TestCheckPermissionsService:
    """Test cases for CheckPermissionsService."""

    def test_user_with_all_permissions_passes(self):
        """Test that user with all required permissions passes check."""
        # Arrange
        user = AuthenticatedUser(
            user_id='auth0|123456',
            permissions=['read:data', 'write:data', 'admin:write'],
        )
        service = CheckPermissionsService(['read:data', 'write:data'])

        # Act & Assert - should not raise
        service.execute(user)

    def test_user_without_permissions_raises_exception(self):
        """Test that user without required permissions raises exception."""
        # Arrange
        user = AuthenticatedUser(
            user_id='auth0|123456', permissions=['read:data']
        )
        service = CheckPermissionsService(['write:data', 'admin:write'])

        # Act & Assert
        with pytest.raises(InsufficientPermissionsException) as exc_info:
            service.execute(user)

        assert 'write:data' in str(exc_info.value)
        assert 'admin:write' in str(exc_info.value)

    def test_user_with_partial_permissions_raises_exception(self):
        """Test that user with only some permissions raises exception."""
        # Arrange
        user = AuthenticatedUser(
            user_id='auth0|123456', permissions=['read:data']
        )
        service = CheckPermissionsService(['read:data', 'write:data'])

        # Act & Assert
        with pytest.raises(InsufficientPermissionsException):
            service.execute(user)

    def test_empty_permissions_required_always_passes(self):
        """Test that no permissions required always passes."""
        # Arrange
        user = AuthenticatedUser(user_id='auth0|123456', permissions=[])
        service = CheckPermissionsService([])

        # Act & Assert - should not raise
        service.execute(user)

    def test_user_with_extra_permissions_passes(self):
        """Test that user with more than required permissions passes."""
        # Arrange
        user = AuthenticatedUser(
            user_id='auth0|123456',
            permissions=[
                'read:data',
                'write:data',
                'admin:write',
                'extra:permission',
            ],
        )
        service = CheckPermissionsService(['read:data'])

        # Act & Assert - should not raise
        service.execute(user)
