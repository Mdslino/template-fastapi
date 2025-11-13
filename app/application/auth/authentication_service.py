"""
Authentication service (use case).

This module provides authentication operations using the OAuth2
provider abstraction.
"""

import structlog

from app.application.auth.oauth2_provider import OAuth2Provider
from app.domain.auth.user import AuthenticatedUser
from app.shared.functional.either import Either, Failure, Success

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

    def authenticate(
        self, access_token: str
    ) -> Either[AuthenticatedUser, Exception]:
        """
        Authenticate a user using an access token.

        Args:
            access_token: OAuth2 access token

        Returns:
            Either containing AuthenticatedUser on success or Exception on failure

        Example:
            >>> service = AuthenticationService(provider)
            >>> result = service.authenticate("eyJ...")
            >>> if isinstance(result, Success):
            ...     user = result.unwrap()
            ...     print(f"Authenticated: {user.email}")
        """
        try:
            # Verify the token first
            token_result = self.oauth2_provider.verify_token(access_token)

            if isinstance(token_result, Failure):
                logger.warning('Token verification failed')
                return token_result

            # Get user info
            user_result = self.oauth2_provider.get_user_info(access_token)

            if isinstance(user_result, Success):
                user = user_result.unwrap()
                logger.info(
                    'User authenticated',
                    user_id=str(user.user_id),
                    provider=user.provider,
                )
                return Success(user)
            else:
                logger.error('Failed to get user info')
                return user_result

        except Exception as e:
            logger.error('Authentication error', exc_info=e)
            return Failure(e)

    def refresh_authentication(
        self, refresh_token: str
    ) -> Either[dict[str, str], Exception]:
        """
        Refresh authentication using a refresh token.

        Args:
            refresh_token: OAuth2 refresh token

        Returns:
            Either containing new token data or Exception on failure

        Example:
            >>> service = AuthenticationService(provider)
            >>> result = service.refresh_authentication("refresh_token")
            >>> if isinstance(result, Success):
            ...     tokens = result.unwrap()
            ...     new_token = tokens['access_token']
        """
        try:
            result = self.oauth2_provider.refresh_token(refresh_token)

            if isinstance(result, Success):
                logger.info('Token refreshed successfully')
            else:
                logger.warning('Token refresh failed')

            return result

        except Exception as e:
            logger.error('Token refresh error', exc_info=e)
            return Failure(e)

    def logout(self, access_token: str) -> Either[bool, Exception]:
        """
        Logout a user by revoking their access token.

        Args:
            access_token: OAuth2 access token to revoke

        Returns:
            Either containing True on success or Exception on failure

        Example:
            >>> service = AuthenticationService(provider)
            >>> result = service.logout("eyJ...")
            >>> if isinstance(result, Success):
            ...     print("Logged out successfully")
        """
        try:
            result = self.oauth2_provider.revoke_token(access_token)

            if isinstance(result, Success):
                logger.info('User logged out successfully')
            else:
                logger.warning('Logout failed')

            return result

        except Exception as e:
            logger.error('Logout error', exc_info=e)
            return Failure(e)

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
