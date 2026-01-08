"""
Service for checking user permissions.

This service validates that a user has the required permissions
to perform specific actions.
"""

import structlog

from app.auth.exceptions import InsufficientPermissionsException
from app.auth.schemas import AuthenticatedUser

logger = structlog.get_logger()


class CheckPermissionsService:
    """
    Service for validating user permissions.

    This service checks if a user has the required permissions
    to perform an action.
    """

    def __init__(self, required_permissions: list[str]):
        """
        Initialize the permission checker service.

        Args:
            required_permissions: List of permissions required
        """
        self.required_permissions = required_permissions

    def execute(self, user: AuthenticatedUser) -> None:
        """
        Check if user has all required permissions.

        Args:
            user: The authenticated user to check

        Raises:
            InsufficientPermissionsException: If user lacks required permissions
        """
        if not user.has_all_permissions(self.required_permissions):
            missing = [
                p
                for p in self.required_permissions
                if p not in user.permissions
            ]
            logger.warning(
                'User lacks required permissions',
                user_id=user.user_id,
                required=self.required_permissions,
                missing=missing,
            )
            raise InsufficientPermissionsException(self.required_permissions)

        logger.debug(
            'Permission check passed',
            user_id=user.user_id,
            permissions=self.required_permissions,
        )
