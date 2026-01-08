"""
Integration tests for authentication endpoints.

Tests the full authentication flow from HTTP request to response.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from jose import jwt


@pytest.fixture
def auth_settings(monkeypatch):
    """Configure Auth0 settings for testing."""
    monkeypatch.setenv('AUTH0_DOMAIN', 'test.auth0.com')
    monkeypatch.setenv('AUTH0_AUDIENCE', 'https://api.example.com')
    monkeypatch.setenv('AUTH0_ALGORITHM', 'RS256')

    # Force settings reload
    import core.config

    core.config._settings = None


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

    rsa_key = RSAKey(public_key, algorithm='RS256')
    jwk = rsa_key.to_dict()
    jwk['kid'] = 'test-key-id'
    jwk['use'] = 'sig'

    return {'keys': [jwk]}


def create_token(private_key, permissions=None, expired=False):
    """Helper to create JWT tokens."""
    if permissions is None:
        permissions = []

    exp_time = (
        datetime.utcnow() - timedelta(hours=1)
        if expired
        else datetime.utcnow() + timedelta(hours=1)
    )

    payload = {
        'sub': 'auth0|test-user',
        'permissions': permissions,
        'iss': 'https://test.auth0.com/',
        'aud': 'https://api.example.com',
        'exp': exp_time,
        'iat': datetime.utcnow(),
    }

    return jwt.encode(
        payload, private_key, algorithm='RS256', headers={'kid': 'test-key-id'}
    )


class TestAuthenticationEndpoints:
    """Integration tests for authentication endpoints."""

    def test_get_me_without_token_returns_401(self, client, auth_settings):
        """Test that /me without token returns 401."""
        # Act
        response = client.get('/api/v1/auth/me')

        # Assert
        assert response.status_code == 401
        assert 'authorization' in response.json()['detail'].lower()

    def test_get_me_with_invalid_format_returns_401(
        self, client, auth_settings
    ):
        """Test that /me with invalid header format returns 401."""
        # Act
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': 'InvalidFormat token123'},
        )

        # Assert
        assert response.status_code == 401
        assert 'bearer' in response.json()['detail'].lower()

    def test_get_me_with_valid_token_returns_user_info(
        self, client, auth_settings, private_key, jwks_mock
    ):
        """Test that /me with valid token returns user info."""
        # Arrange
        token = create_token(
            private_key, permissions=['read:data', 'write:data']
        )

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act
            response = client.get(
                '/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'}
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['user_id'] == 'auth0|test-user'
        assert 'read:data' in data['permissions']
        assert 'write:data' in data['permissions']

    def test_get_me_with_expired_token_returns_401(
        self, client, auth_settings, private_key, jwks_mock
    ):
        """Test that /me with expired token returns 401."""
        # Arrange
        token = create_token(private_key, expired=True)

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act
            response = client.get(
                '/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'}
            )

        # Assert
        assert response.status_code == 401
        assert 'expired' in response.json()['detail'].lower()

    def test_admin_endpoint_with_admin_permission_returns_200(
        self, client, auth_settings, private_key, jwks_mock
    ):
        """Test admin endpoint with correct permission."""
        # Arrange
        token = create_token(private_key, permissions=['admin:write'])

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act
            response = client.get(
                '/api/v1/auth/admin',
                headers={'Authorization': f'Bearer {token}'},
            )

        # Assert
        assert response.status_code == 200
        assert 'Admin access granted' in response.json()['message']

    def test_admin_endpoint_without_permission_returns_403(
        self, client, auth_settings, private_key, jwks_mock
    ):
        """Test admin endpoint without required permission."""
        # Arrange
        token = create_token(private_key, permissions=['read:data'])

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act
            response = client.get(
                '/api/v1/auth/admin',
                headers={'Authorization': f'Bearer {token}'},
            )

        # Assert
        assert response.status_code == 403
        assert 'permission' in response.json()['detail'].lower()

    def test_read_data_endpoint_with_permission(
        self, client, auth_settings, private_key, jwks_mock
    ):
        """Test read data endpoint with correct permission."""
        # Arrange
        token = create_token(private_key, permissions=['read:data'])

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act
            response = client.get(
                '/api/v1/auth/data/read',
                headers={'Authorization': f'Bearer {token}'},
            )

        # Assert
        assert response.status_code == 200
        assert 'data' in response.json()

    def test_write_data_endpoint_requires_write_permission(
        self, client, auth_settings, private_key, jwks_mock
    ):
        """Test write data endpoint requires write:data permission."""
        # Arrange - token with only read permission
        token = create_token(private_key, permissions=['read:data'])

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act
            response = client.post(
                '/api/v1/auth/data/write',
                headers={'Authorization': f'Bearer {token}'},
            )

        # Assert
        assert response.status_code == 403

    def test_write_data_endpoint_with_correct_permission(
        self, client, auth_settings, private_key, jwks_mock
    ):
        """Test write data endpoint with correct permission."""
        # Arrange
        token = create_token(private_key, permissions=['write:data'])

        with patch('httpx.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = jwks_mock
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # Act
            response = client.post(
                '/api/v1/auth/data/write',
                headers={'Authorization': f'Bearer {token}'},
            )

        # Assert
        assert response.status_code == 200
        assert 'successfully' in response.json()['message'].lower()
