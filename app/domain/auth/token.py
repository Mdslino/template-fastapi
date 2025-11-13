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
