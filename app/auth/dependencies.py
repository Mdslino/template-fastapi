"""
FastAPI dependencies for authentication and authorization.

This module provides dependency functions for use with FastAPI's
dependency injection system.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.auth.exceptions import (
    AuthenticationException,
    InsufficientPermissionsException,
)
from app.auth.schemas import AuthenticatedUser
from app.auth.services.check_permissions import CheckPermissionsService
from app.auth.services.verify_token import VerifyTokenService
from core.dependencies import SettingsDep


def get_verify_token_service(
    settings: SettingsDep,
) -> VerifyTokenService:
    """
    Get token verification service instance.

    Args:
        settings: Application settings

    Returns:
        VerifyTokenService instance
    """
    return VerifyTokenService(settings)


VerifyTokenServiceDep = Annotated[
    VerifyTokenService, Depends(get_verify_token_service)
]


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    verify_service: VerifyTokenServiceDep = None,
) -> AuthenticatedUser:
    """
    Extract and validate JWT token from Authorization header.

    This dependency can be used in any FastAPI route to require authentication.

    Example:
        @router.get('/protected')
        def protected_endpoint(user: CurrentUserDep):
            return {'user_id': user.user_id}

    Args:
        authorization: Authorization header value (Bearer token)
        verify_service: Token verification service

    Returns:
        AuthenticatedUser with user ID and permissions

    Raises:
        HTTPException: 401 if authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing authorization header',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authorization header format. Expected: Bearer <token>',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    token = parts[1]

    try:
        return verify_service.execute(token)
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'},
        )


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


class RequirePermissions:
    """
    Dependency class for requiring specific permissions.

    This creates a reusable dependency that checks if the current user
    has the required permissions.

    Example:
        require_admin = RequirePermissions(['admin:write'])

        @router.post('/admin')
        def admin_endpoint(user: Annotated[AuthenticatedUser, Depends(require_admin)]):
            return {'message': 'Admin access granted'}
    """

    def __init__(self, permissions: list[str]):
        """
        Initialize the permission requirement.

        Args:
            permissions: List of required permissions
        """
        self.permissions = permissions

    def __call__(self, current_user: CurrentUserDep) -> AuthenticatedUser:
        """
        Check if current user has required permissions.

        Args:
            current_user: The authenticated user

        Returns:
            The authenticated user if they have permissions

        Raises:
            HTTPException: 403 if user lacks required permissions
        """
        service = CheckPermissionsService(self.permissions)
        try:
            service.execute(current_user)
            return current_user
        except InsufficientPermissionsException as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
