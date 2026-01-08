"""
Service for verifying JWT tokens from Auth0.

This service validates JWT tokens, checks their signature against Auth0's
public keys, and extracts user information and permissions.
"""

import httpx
import structlog
from jose import JWTError, jwt

from app.auth.exceptions import (
    ExpiredTokenException,
    InvalidTokenException,
)
from app.auth.schemas import AuthenticatedUser, TokenPayload
from core.config import Settings

logger = structlog.get_logger()


class VerifyTokenService:
    """
    Service for verifying and decoding Auth0 JWT tokens.

    This service:
    1. Fetches Auth0 public keys (JWKS)
    2. Validates JWT signature and claims
    3. Extracts user information and permissions
    """

    def __init__(self, settings: Settings):
        """
        Initialize the token verification service.

        Args:
            settings: Application settings containing Auth0 configuration
        """
        self.settings = settings
        self.jwks_uri = (
            f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
        )
        self._jwks_cache: dict | None = None

    def _get_jwks(self) -> dict:
        """
        Fetch JWKS (JSON Web Key Set) from Auth0.

        Returns:
            JWKS dictionary containing public keys

        Raises:
            InvalidTokenException: If JWKS cannot be fetched
        """
        if self._jwks_cache is not None:
            return self._jwks_cache

        try:
            response = httpx.get(self.jwks_uri, timeout=10.0)
            response.raise_for_status()
            self._jwks_cache = response.json()
            return self._jwks_cache
        except httpx.HTTPError as e:
            logger.error('Failed to fetch JWKS', error=str(e))
            raise InvalidTokenException('Unable to fetch signing keys')

    def _get_signing_key(self, token: str) -> str:
        """
        Get the signing key for the token from JWKS.

        Args:
            token: JWT token string

        Returns:
            Signing key in PEM format

        Raises:
            InvalidTokenException: If signing key cannot be found
        """
        try:
            # Get the key ID from token header
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')

            if not kid:
                raise InvalidTokenException('Token missing key ID')

            # Find the matching key in JWKS
            jwks = self._get_jwks()
            for key in jwks.get('keys', []):
                if key.get('kid') == kid:
                    # Convert JWK to PEM format
                    from jose.backends import RSAKey

                    rsa_key = RSAKey(
                        key, algorithm=self.settings.AUTH0_ALGORITHM
                    )
                    return rsa_key.to_pem().decode('utf-8')

            raise InvalidTokenException('Signing key not found')

        except (JWTError, KeyError) as e:
            logger.error('Error getting signing key', error=str(e))
            raise InvalidTokenException(f'Invalid token header: {str(e)}')

    def execute(self, token: str) -> AuthenticatedUser:
        """
        Verify token and extract user information.

        Args:
            token: JWT token string (without 'Bearer' prefix)

        Returns:
            AuthenticatedUser with user ID and permissions

        Raises:
            InvalidTokenException: If token is invalid
            ExpiredTokenException: If token has expired
        """
        try:
            # Get signing key
            signing_key = self._get_signing_key(token)

            # Decode and validate token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=[self.settings.AUTH0_ALGORITHM],
                audience=self.settings.AUTH0_AUDIENCE,
                issuer=f'https://{self.settings.AUTH0_DOMAIN}/',
            )

            # Parse payload
            token_payload = TokenPayload.model_validate(payload)

            logger.info(
                'Token verified successfully',
                user_id=token_payload.sub,
                permissions_count=len(token_payload.permissions),
            )

            # Return authenticated user
            return AuthenticatedUser(
                user_id=token_payload.sub,
                permissions=token_payload.permissions,
            )

        except jwt.ExpiredSignatureError:
            logger.warning('Token expired')
            raise ExpiredTokenException()

        except JWTError as e:
            logger.warning('JWT validation failed', error=str(e))
            raise InvalidTokenException(str(e))

        except Exception as e:
            logger.error('Unexpected error verifying token', error=str(e))
            raise InvalidTokenException(f'Token verification failed: {str(e)}')
