"""
Authentication service.

This module provides authentication operations using the OAuth2
provider abstraction.
"""

import structlog

from app.auth.providers.interface import OAuth2Provider
from app.auth.models import AuthenticatedUser
from shared.exceptions import AuthenticationException

logger = structlog.get_logger(__name__)


class AuthenticationService:
    """
    Authentication service for managing user authentication.

    This service uses the OAuth2Provider interface, making it
    work with any OAuth2-compliant provider.

    Attributes:
        oauth2_provider: OAuth2 provider implementation
    """

    def __init__(self, oauth2_provider: OAuth2Provider):
        """
        Initialize the authentication service.

        Args:
            oauth2_provider: OAuth2 provider implementation
        """
        self.oauth2_provider = oauth2_provider

    def authenticate(self, access_token: str) -> AuthenticatedUser:
        """
        Authenticate a user using an access token.

        Args:
            access_token: OAuth2 access token

        Returns:
            AuthenticatedUser on success

        Raises:
            AuthenticationException: If authentication fails

        Example:
            >>> service = AuthenticationService(provider)
            >>> user = service.authenticate("eyJ...")
            >>> print(f"Authenticated: {user.email}")
        """
        try:
            # Verify the token first
            self.oauth2_provider.verify_token(access_token)

            # Get user info
            user = self.oauth2_provider.get_user_info(access_token)

            logger.info(
                'User authenticated',
                user_id=str(user.user_id),
                provider=user.provider,
            )
            return user

        except AuthenticationException:
            logger.warning('Authentication failed')
            raise
        except Exception as e:
            logger.error('Authentication error', exc_info=e)
            raise AuthenticationException(
                f'Authentication failed: {str(e)}'
            ) from e

    def refresh_authentication(
        self, refresh_token: str
    ) -> dict[str, str]:
        """
        Refresh authentication using a refresh token.

        Args:
            refresh_token: OAuth2 refresh token

        Returns:
            Dict containing new token data

        Raises:
            AuthenticationException: If token refresh fails

        Example:
            >>> service = AuthenticationService(provider)
            >>> tokens = service.refresh_authentication("refresh_token")
            >>> new_token = tokens['access_token']
        """
        try:
            tokens = self.oauth2_provider.refresh_token(refresh_token)
            logger.info('Token refreshed successfully')
            return tokens

        except Exception as e:
            logger.warning('Token refresh failed', error=str(e))
            raise AuthenticationException(
                f'Token refresh failed: {str(e)}'
            ) from e

    def logout(self, access_token: str) -> bool:
        """
        Logout a user by revoking their access token.

        Args:
            access_token: OAuth2 access token to revoke

        Returns:
            True on success

        Raises:
            AuthenticationException: If logout fails

        Example:
            >>> service = AuthenticationService(provider)
            >>> service.logout("eyJ...")
            >>> print("Logged out successfully")
        """
        try:
            result = self.oauth2_provider.revoke_token(access_token)
            logger.info('User logged out successfully')
            return result

        except Exception as e:
            logger.warning('Logout failed', error=str(e))
            raise AuthenticationException(
                f'Logout failed: {str(e)}'
            ) from e

    def check_permissions(
        self, user: AuthenticatedUser, required_permissions: list[str]
    ) -> bool:
        """
        Check if user has required permissions.

        Args:
            user: Authenticated user
            required_permissions: List of required permissions

        Returns:
            True if user has all required permissions

        Example:
            >>> service = AuthenticationService(provider)
            >>> has_access = service.check_permissions(
            ...     user,
            ...     ['read:data', 'write:data']
            ... )
        """
        return self.oauth2_provider.validate_permissions(
            user, required_permissions
        )

    def check_roles(
        self, user: AuthenticatedUser, required_roles: list[str]
    ) -> bool:
        """
        Check if user has required roles.

        Args:
            user: Authenticated user
            required_roles: List of required roles

        Returns:
            True if user has at least one required role

        Example:
            >>> service = AuthenticationService(provider)
            >>> is_admin = service.check_roles(user, ['admin', 'moderator'])
        """
        return self.oauth2_provider.validate_roles(user, required_roles)
