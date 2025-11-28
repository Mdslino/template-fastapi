"""
OAuth2 providers.

This package contains OAuth2 provider implementations:
- interface: OAuth2Provider protocol definition
- jwt_provider: Generic JWT-based implementation
"""

from app.auth.providers.interface import OAuth2Provider
from app.auth.providers.jwt_provider import JWTOAuth2Provider

__all__ = ["OAuth2Provider", "JWTOAuth2Provider"]
