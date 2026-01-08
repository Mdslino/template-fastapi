"""
Authentication-specific exceptions.

This module defines exceptions for authentication and authorization errors.
"""

from shared.exceptions import DomainException


class AuthenticationException(DomainException):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = 'Authentication failed'):
        self.message = message
        super().__init__(message)


class InvalidTokenException(AuthenticationException):
    """Exception raised when a JWT token is invalid."""

    def __init__(self, reason: str = 'Invalid token'):
        self.reason = reason
        super().__init__(f'Invalid token: {reason}')


class ExpiredTokenException(AuthenticationException):
    """Exception raised when a JWT token has expired."""

    def __init__(self):
        super().__init__('Token has expired')


class InsufficientPermissionsException(DomainException):
    """Exception raised when user lacks required permissions."""

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions
        super().__init__(
            f'Insufficient permissions. Required: {", ".join(required_permissions)}'
        )
