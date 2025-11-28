"""
Authentication models.

This module defines all authentication-related domain models:
- AuthenticatedUser: Provider-agnostic user representation
- OAuth2Token: OAuth2 access token model
- TokenPayload: JWT token payload
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AuthenticatedUser(BaseModel):
    """
    Authenticated user entity.

    This represents a user authenticated via OAuth2, regardless of the
    provider (Supabase, Firebase, Cognito, Auth0, etc.).

    Attributes:
        user_id: Unique user identifier from the OAuth2 provider
        email: User's email address
        email_verified: Whether the email has been verified
        name: User's display name (optional)
        picture: URL to user's profile picture (optional)
        provider: OAuth2 provider name (e.g., 'supabase', 'firebase')
        provider_user_id: User ID from the provider's system
        roles: List of roles assigned to the user
        permissions: List of permissions granted to the user
        metadata: Additional provider-specific metadata
        created_at: When the user was first authenticated
        last_login: Last login timestamp
    """

    user_id: UUID
    email: EmailStr
    email_verified: bool = False
    name: str | None = None
    picture: str | None = None
    provider: str
    provider_user_id: str
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: datetime = Field(default_factory=datetime.now)

    model_config = {'frozen': True}

    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            role: Role name to check

        Returns:
            True if user has the role, False otherwise
        """
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            permission: Permission name to check

        Returns:
            True if user has the permission, False otherwise
        """
        return permission in self.permissions

    def has_any_role(self, roles: list[str]) -> bool:
        """
        Check if user has any of the specified roles.

        Args:
            roles: List of role names to check

        Returns:
            True if user has at least one role, False otherwise
        """
        return any(role in self.roles for role in roles)

    def has_all_roles(self, roles: list[str]) -> bool:
        """
        Check if user has all of the specified roles.

        Args:
            roles: List of role names to check

        Returns:
            True if user has all roles, False otherwise
        """
        return all(role in self.roles for role in roles)
"""
OAuth2 token models.

This module defines token-related models for OAuth2 authentication.
"""

from pydantic import BaseModel, Field


class OAuth2Token(BaseModel):
    """
    OAuth2 access token response.

    Attributes:
        access_token: The access token
        token_type: Token type (usually 'Bearer')
        expires_in: Token expiration time in seconds
        refresh_token: Refresh token (optional)
        scope: Token scope (optional)
    """

    access_token: str
    token_type: str = 'Bearer'
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None


class TokenPayload(BaseModel):
    """
    Decoded JWT token payload.

    Attributes:
        sub: Subject (user ID)
        exp: Expiration timestamp
        iat: Issued at timestamp
        email: User email
        email_verified: Whether email is verified
        provider: OAuth2 provider name
        roles: User roles
        permissions: User permissions
    """

    sub: str
    exp: int
    iat: int | None = None
    email: str | None = None
    email_verified: bool = False
    provider: str | None = None
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
