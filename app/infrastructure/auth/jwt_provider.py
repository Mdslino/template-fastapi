"""
Generic JWT-based OAuth2 provider implementation.

This module provides a generic implementation of the OAuth2Provider
interface that works with JWT tokens from any provider (Supabase,
Firebase, Cognito, Auth0, etc.).
"""

import uuid
from datetime import datetime

import jwt
import structlog
from jwt import PyJWKClient

from app.application.auth.oauth2_provider import OAuth2Provider
from app.domain.auth.token import TokenPayload
from app.domain.auth.user import AuthenticatedUser
from app.shared.functional.either import Either, Failure, Success

logger = structlog.get_logger(__name__)


class JWTOAuth2Provider(OAuth2Provider):
    """
    Generic JWT-based OAuth2 provider implementation.

    This implementation works with any OAuth2 provider that uses JWT tokens
    and exposes a JWKS endpoint for key verification.

    Attributes:
        jwks_url: URL to the provider's JWKS (JSON Web Key Set) endpoint
        issuer: Expected token issuer
        audience: Expected token audience
        algorithms: List of allowed JWT algorithms
        jwks_client: JWT key client for token verification
    """

    def __init__(
        self,
        jwks_url: str,
        issuer: str,
        audience: str | None = None,
        algorithms: list[str] | None = None,
    ):
        """
        Initialize the JWT OAuth2 provider.

        Args:
            jwks_url: URL to JWKS endpoint (e.g., https://provider.com/.well-known/jwks.json)
            issuer: Expected token issuer (e.g., https://provider.com)
            audience: Expected token audience (optional)
            algorithms: List of allowed algorithms (default: ['RS256'])
        """
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.audience = audience
        self.algorithms = algorithms or ['RS256']
        self.jwks_client = PyJWKClient(jwks_url)

    def verify_token(self, token: str) -> Either[TokenPayload, Exception]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT access token

        Returns:
            Either containing TokenPayload on success or Exception on failure
        """
        try:
            # Get signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            # Decode and verify token
            options = {
                'verify_exp': True,
                'verify_aud': self.audience is not None,
            }

            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=self.algorithms,
                issuer=self.issuer,
                audience=self.audience,
                options=options,
            )

            # Extract token payload
            payload = TokenPayload(
                sub=decoded.get('sub', ''),
                exp=decoded.get('exp', 0),
                iat=decoded.get('iat'),
                email=decoded.get('email'),
                email_verified=decoded.get('email_verified', False),
                provider=decoded.get('provider', 'unknown'),
                roles=decoded.get('roles', []),
                permissions=decoded.get('permissions', []),
            )

            logger.debug('Token verified successfully', sub=payload.sub)
            return Success(payload)

        except jwt.ExpiredSignatureError as e:
            logger.warning('Token expired')
            return Failure(e)
        except jwt.InvalidTokenError as e:
            logger.warning('Invalid token', error=str(e))
            return Failure(e)
        except Exception as e:
            logger.error('Token verification error', exc_info=e)
            return Failure(e)

    def get_user_info(
        self, token: str
    ) -> Either[AuthenticatedUser, Exception]:
        """
        Get user information from a JWT token.

        Args:
            token: Valid JWT access token

        Returns:
            Either containing AuthenticatedUser on success or Exception on failure
        """
        try:
            # First verify the token
            token_result = self.verify_token(token)

            if isinstance(token_result, Failure):
                return token_result

            payload = token_result.unwrap()

            # Create authenticated user from token payload
            user = AuthenticatedUser(
                user_id=uuid.UUID(payload.sub)
                if self._is_uuid(payload.sub)
                else uuid.uuid5(uuid.NAMESPACE_DNS, payload.sub),
                email=payload.email or '',
                email_verified=payload.email_verified,
                provider=payload.provider or 'unknown',
                provider_user_id=payload.sub,
                roles=payload.roles,
                permissions=payload.permissions,
            )

            logger.info('User info retrieved', user_id=str(user.user_id))
            return Success(user)

        except Exception as e:
            logger.error('Error getting user info', exc_info=e)
            return Failure(e)

    def refresh_token(
        self, refresh_token: str
    ) -> Either[dict[str, str], Exception]:
        """
        Refresh an access token.

        Note: This is a placeholder. Actual token refresh requires
        provider-specific implementation as it typically involves
        making HTTP requests to the provider's token endpoint.

        Args:
            refresh_token: The refresh token

        Returns:
            Either containing new token data or Exception
        """
        return Failure(
            NotImplementedError(
                'Token refresh must be implemented per provider. '
                "Please use the provider's SDK or API."
            )
        )

    def revoke_token(self, token: str) -> Either[bool, Exception]:
        """
        Revoke a token.

        Note: This is a placeholder. Actual token revocation requires
        provider-specific implementation.

        Args:
            token: The access token to revoke

        Returns:
            Either containing True on success or Exception
        """
        return Failure(
            NotImplementedError(
                'Token revocation must be implemented per provider. '
                "Please use the provider's SDK or API."
            )
        )

    def validate_permissions(
        self, user: AuthenticatedUser, required_permissions: list[str]
    ) -> bool:
        """
        Validate if user has required permissions.

        Args:
            user: Authenticated user
            required_permissions: List of required permissions

        Returns:
            True if user has all required permissions
        """
        return all(
            permission in user.permissions
            for permission in required_permissions
        )

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
        """
        return any(role in user.roles for role in required_roles)

    @staticmethod
    def _is_uuid(value: str) -> bool:
        """Check if a string is a valid UUID."""
        try:
            uuid.UUID(value)
            return True
        except (ValueError, AttributeError):
            return False
