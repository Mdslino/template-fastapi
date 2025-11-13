"""
Authentication app module.

This module contains all authentication-related functionality:
- OAuth2 authentication
- Token verification
- User management
- Access control (roles and permissions)
"""

from app.auth.models import AuthenticatedUser, OAuth2Token, TokenPayload
from app.auth.services import AuthenticationService
from app.auth.dependencies import get_current_user, require_roles, require_permissions

__all__ = [
    "AuthenticatedUser",
    "OAuth2Token",
    "TokenPayload",
    "AuthenticationService",
    "get_current_user",
    "require_roles",
    "require_permissions",
]
