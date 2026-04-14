"""
Authentication schemas.

This module defines Pydantic schemas for authentication-related data.
"""

from shared.schemas import BaseSchema


class TokenPayload(BaseSchema):
    """
    JWT token payload schema.

    Contains the decoded JWT token claims from Auth0.
    """

    sub: str  # Subject (user ID)
    permissions: list[str] = []  # User permissions from Auth0
    iss: str | None = None  # Issuer
    aud: str | list[str] | None = None  # Audience
    exp: int | None = None  # Expiration time
    iat: int | None = None  # Issued at time


class AuthenticatedUser(BaseSchema):
    """
    Authenticated user schema.

    Represents the current authenticated user with their permissions.
    """

    user_id: str  # User ID from token (sub claim)
    permissions: list[str] = []  # User permissions

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: list[str]) -> bool:
        """Check if user has at least one of the specified permissions."""
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: list[str]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(p in self.permissions for p in permissions)
