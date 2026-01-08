"""
Tests for token verification service.

Following TDD approach: tests define the expected behavior of the service.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from jose import jwt

from app.auth.exceptions import (
    ExpiredTokenException,
    InvalidTokenException,
)
from app.auth.services.verify_token import VerifyTokenService
from core.config import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for Auth0."""
    settings = Mock(spec=Settings)
    settings.AUTH0_DOMAIN = 'test.auth0.com'
    settings.AUTH0_AUDIENCE = 'https://api.example.com'
    settings.AUTH0_ALGORITHM = 'RS256'
    return settings


@pytest.fixture
def private_key():
    """Generate RSA private key for testing."""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')


@pytest.fixture
def public_key(private_key):
    """Get public key from private key."""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.serialization import (
        load_pem_private_key,
    )

    key = load_pem_private_key(
        private_key.encode('utf-8'), password=None, backend=default_backend()
    )

    pub_key = key.public_key()

    return pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode('utf-8')


@pytest.fixture
def jwks_mock(public_key):
    """Create mock JWKS response."""
    from jose.backends import RSAKey

    # Create JWK from public key
    rsa_key = RSAKey(public_key, algorithm='RS256')
    jwk = rsa_key.to_dict()
    jwk['kid'] = 'test-key-id'
    jwk['use'] = 'sig'

    return {'keys': [jwk]}


@pytest.fixture
def valid_token(private_key, mock_settings):
    """Create a valid JWT token for testing."""
    payload = {
        'sub': 'auth0|123456',
        'permissions': ['read:data', 'write:data'],
        'iss': f'https://{mock_settings.AUTH0_DOMAIN}/',
        'aud': mock_settings.AUTH0_AUDIENCE,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
    }

    return jwt.encode(
        payload, private_key, algorithm='RS256', headers={'kid': 'test-key-id'}
    )


@pytest.fixture
def expired_token(private_key, mock_settings):
    """Create an expired JWT token for testing."""
    payload = {
        'sub': 'auth0|123456',
        'permissions': ['read:data'],
        'iss': f'https://{mock_settings.AUTH0_DOMAIN}/',
        'aud': mock_settings.AUTH0_AUDIENCE,
        'exp': datetime.utcnow() - timedelta(hours=1),  # Expired
        'iat': datetime.utcnow() - timedelta(hours=2),
    }

    return jwt.encode(
        payload, private_key, algorithm='RS256', headers={'kid': 'test-key-id'}
    )


class TestVerifyTokenService:
    """Test cases for VerifyTokenService."""

    def test_verify_valid_token_returns_authenticated_user(
        self, mock_settings, valid_token, jwks_mock
    ):
        """Test that a valid token returns an authenticated user."""
        # Arrange
        service = VerifyTokenService(mock_settings)

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act
            user = service.execute(valid_token)

        # Assert
        assert user.user_id == 'auth0|123456'
        assert 'read:data' in user.permissions
        assert 'write:data' in user.permissions
        assert len(user.permissions) == 2

    def test_verify_expired_token_raises_exception(
        self, mock_settings, expired_token, jwks_mock
    ):
        """Test that an expired token raises ExpiredTokenException."""
        # Arrange
        service = VerifyTokenService(mock_settings)

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act & Assert
            with pytest.raises(ExpiredTokenException):
                service.execute(expired_token)

    def test_verify_invalid_token_raises_exception(
        self, mock_settings, jwks_mock
    ):
        """Test that an invalid token raises InvalidTokenException."""
        # Arrange
        service = VerifyTokenService(mock_settings)
        invalid_token = 'invalid.token.string'

        # Act & Assert
        with pytest.raises(InvalidTokenException):
            service.execute(invalid_token)

    def test_token_without_kid_raises_exception(
        self, mock_settings, private_key
    ):
        """Test that a token without kid raises InvalidTokenException."""
        # Arrange
        service = VerifyTokenService(mock_settings)

        # Create token without kid in header
        payload = {
            'sub': 'auth0|123456',
            'permissions': [],
            'iss': f'https://{mock_settings.AUTH0_DOMAIN}/',
            'aud': mock_settings.AUTH0_AUDIENCE,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
        }

        token = jwt.encode(
            payload,
            private_key,
            algorithm='RS256',
            # No kid in headers
        )

        # Act & Assert
        with pytest.raises(InvalidTokenException) as exc_info:
            service.execute(token)

        # Check that it's an InvalidTokenException with appropriate message
        assert 'token' in str(exc_info.value).lower()

    def test_jwks_fetch_failure_raises_exception(self, mock_settings):
        """Test that JWKS fetch failure raises InvalidTokenException."""
        # Arrange
        service = VerifyTokenService(mock_settings)

        with patch('httpx.get') as mock_get:
            mock_get.side_effect = Exception('Network error')

            # Act & Assert
            with pytest.raises(InvalidTokenException) as exc_info:
                service.execute('any.token.here')

            # Check that it's an InvalidTokenException
            assert 'token' in str(exc_info.value).lower()

    def test_signing_key_not_found_raises_exception(
        self, mock_settings, valid_token
    ):
        """Test that missing signing key raises InvalidTokenException."""
        # Arrange
        service = VerifyTokenService(mock_settings)

        # JWKS with different kid
        jwks = {'keys': [{'kid': 'different-key-id', 'use': 'sig'}]}

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act & Assert
            with pytest.raises(InvalidTokenException) as exc_info:
                service.execute(valid_token)

            assert 'signing key not found' in str(exc_info.value).lower()

    def test_jwks_caching(self, mock_settings, valid_token, jwks_mock):
        """Test that JWKS is cached after first fetch."""
        # Arrange
        service = VerifyTokenService(mock_settings)

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act - verify token twice
            service.execute(valid_token)
            service.execute(valid_token)

        # Assert - httpx.get should only be called once (cached)
        assert mock_get.call_count == 1
