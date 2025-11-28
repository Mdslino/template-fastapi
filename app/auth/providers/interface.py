"""
OAuth2 provider interface.

This module defines the abstract interface for OAuth2 providers,
allowing the application to work with any OAuth2 provider in an
agnostic way.
"""

from abc import ABC, abstractmethod

from app.auth.models import TokenPayload, AuthenticatedUser


class OAuth2Provider(ABC):
    """
    OAuth2 provider interface.

    This abstract class defines the contract that any OAuth2 provider 
    implementation must follow. It abstracts away provider-specific details, 
    making the application work with Supabase, Firebase, Cognito, Auth0, 
    or any other OAuth2-compliant provider.

    Methods raise exceptions on failure for clean error handling.
    """

    @abstractmethod
    def verify_token(self, token: str) -> TokenPayload:
        """
        Verify and decode an OAuth2 access token.

        Args:
            token: The access token to verify

        Returns:
            TokenPayload on success

        Raises:
            TokenExpiredException: If the token has expired
            InvalidTokenException: If the token is invalid
            AuthenticationException: For other authentication errors

        Example:
            >>> provider = get_oauth2_provider()
            >>> payload = provider.verify_token("eyJ...")
            >>> user_id = payload.sub
        """
        ...

    @abstractmethod
    def get_user_info(self, token: str) -> AuthenticatedUser:
        """
        Get authenticated user information from the provider.

        Args:
            token: Valid access token

        Returns:
            AuthenticatedUser on success

        Raises:
            AuthenticationException: If getting user info fails

        Example:
            >>> provider = get_oauth2_provider()
            >>> user = provider.get_user_info("eyJ...")
            >>> print(f"User: {user.email}")
        """
        ...

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> dict[str, str]:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            Dict containing new token data with 'access_token' and optionally
            'refresh_token', 'expires_in', etc.

        Raises:
            NotImplementedProviderException: If not implemented
            AuthenticationException: If token refresh fails

        Example:
            >>> provider = get_oauth2_provider()
            >>> tokens = provider.refresh_token("refresh_token_here")
            >>> new_access_token = tokens['access_token']
        """
        ...

    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """
        Revoke/invalidate an access token.

        Args:
            token: The access token to revoke

        Returns:
            True on success

        Raises:
            NotImplementedProviderException: If not implemented
            AuthenticationException: If token revocation fails

        Example:
            >>> provider = get_oauth2_provider()
            >>> provider.revoke_token("eyJ...")
            >>> print("Token revoked successfully")
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
