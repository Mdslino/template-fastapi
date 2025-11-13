"""
OAuth2 provider interface (port).

This module defines the abstract interface for OAuth2 providers,
allowing the application to work with any OAuth2 provider in an
agnostic way.
"""

from abc import abstractmethod
from typing import Protocol

from app.domain.auth.token import TokenPayload
from app.domain.auth.user import AuthenticatedUser
from app.shared.functional.either import Either
from app.shared.functional.option import Option


class OAuth2Provider(Protocol):
    """
    OAuth2 provider interface.

    This protocol defines the contract that any OAuth2 provider implementation
    must follow. It abstracts away provider-specific details, making the
    application work with Supabase, Firebase, Cognito, Auth0, or any other
    OAuth2-compliant provider.

    Methods must return Either types for operations that can fail and Option
    types for operations that may not find data.
    """

    @abstractmethod
    def verify_token(self, token: str) -> Either[TokenPayload, Exception]:
        """
        Verify and decode an OAuth2 access token.

        Args:
            token: The access token to verify

        Returns:
            Either containing TokenPayload on success or Exception on failure

        Example:
            >>> provider = get_oauth2_provider()
            >>> result = provider.verify_token("eyJ...")
            >>> if isinstance(result, Success):
            ...     payload = result.unwrap()
            ...     user_id = payload.sub
        """
        ...

    @abstractmethod
    def get_user_info(
        self, token: str
    ) -> Either[AuthenticatedUser, Exception]:
        """
        Get authenticated user information from the provider.

        Args:
            token: Valid access token

        Returns:
            Either containing AuthenticatedUser on success or Exception on failure

        Example:
            >>> provider = get_oauth2_provider()
            >>> result = provider.get_user_info("eyJ...")
            >>> if isinstance(result, Success):
            ...     user = result.unwrap()
            ...     print(f"User: {user.email}")
        """
        ...

    @abstractmethod
    def refresh_token(
        self, refresh_token: str
    ) -> Either[dict[str, str], Exception]:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            Either containing new token data or Exception on failure
            Token data should include 'access_token' and optionally
            'refresh_token', 'expires_in', etc.

        Example:
            >>> provider = get_oauth2_provider()
            >>> result = provider.refresh_token("refresh_token_here")
            >>> if isinstance(result, Success):
            ...     tokens = result.unwrap()
            ...     new_access_token = tokens['access_token']
        """
        ...

    @abstractmethod
    def revoke_token(self, token: str) -> Either[bool, Exception]:
        """
        Revoke/invalidate an access token.

        Args:
            token: The access token to revoke

        Returns:
            Either containing True on success or Exception on failure

        Example:
            >>> provider = get_oauth2_provider()
            >>> result = provider.revoke_token("eyJ...")
            >>> if isinstance(result, Success):
            ...     print("Token revoked successfully")
        """
        ...

    @abstractmethod
    def validate_permissions(
        self, user: AuthenticatedUser, required_permissions: list[str]
    ) -> bool:
        """
        Validate if user has required permissions.

        Args:
            user: Authenticated user
            required_permissions: List of required permissions

        Returns:
            True if user has all required permissions, False otherwise

        Example:
            >>> provider = get_oauth2_provider()
            >>> has_access = provider.validate_permissions(
            ...     user,
            ...     ['read:users', 'write:users']
            ... )
        """
        ...

    @abstractmethod
    def validate_roles(
        self, user: AuthenticatedUser, required_roles: list[str]
    ) -> bool:
        """
        Validate if user has required roles.

        Args:
            user: Authenticated user
            required_roles: List of required roles

        Returns:
            True if user has at least one of the required roles

        Example:
            >>> provider = get_oauth2_provider()
            >>> is_admin = provider.validate_roles(user, ['admin', 'superuser'])
        """
        ...
