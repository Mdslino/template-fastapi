"""
Example protected routes demonstrating OAuth2 authentication.

This module shows how to use OAuth2 authentication with the
provider-agnostic implementation.
"""

import structlog
from fastapi import APIRouter, Depends

from app.infrastructure.api.dependencies import (
    CurrentUserDep,
    require_permissions,
    require_roles,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix='/protected', tags=['protected'])


@router.get('/me')
def get_current_user_info(user: CurrentUserDep) -> dict:
    """
    Get current authenticated user information.

    This endpoint demonstrates basic authentication. Any user with a
    valid OAuth2 token can access it.

    Args:
        user: Current authenticated user (injected)

    Returns:
        User information

    Example:
        GET /api/v1/protected/me
        Headers: Authorization: Bearer <token>
    """
    logger.info('User info requested', user_id=str(user.user_id))

    return {
        'user_id': str(user.user_id),
        'email': user.email,
        'email_verified': user.email_verified,
        'name': user.name,
        'provider': user.provider,
        'roles': user.roles,
        'permissions': user.permissions,
    }


@router.get('/admin')
def admin_only_route(
    user: CurrentUserDep,
    _: None = Depends(require_roles(['admin', 'superuser'])),
) -> dict:
    """
    Admin-only endpoint.

    This endpoint demonstrates role-based access control. Only users
    with 'admin' or 'superuser' role can access it.

    Args:
        user: Current authenticated user (injected)
        _: Role validation dependency

    Returns:
        Admin data

    Example:
        GET /api/v1/protected/admin
        Headers: Authorization: Bearer <token_with_admin_role>
    """
    logger.info('Admin endpoint accessed', user_id=str(user.user_id))

    return {
        'message': 'Admin access granted',
        'user': user.email,
        'roles': user.roles,
    }


@router.get('/write-data')
def write_data_route(
    user: CurrentUserDep,
    _: None = Depends(require_permissions(['write:data'])),
) -> dict:
    """
    Permission-protected endpoint.

    This endpoint demonstrates permission-based access control. Only users
    with 'write:data' permission can access it.

    Args:
        user: Current authenticated user (injected)
        _: Permission validation dependency

    Returns:
        Success message

    Example:
        GET /api/v1/protected/write-data
        Headers: Authorization: Bearer <token_with_write_permission>
    """
    logger.info('Write data endpoint accessed', user_id=str(user.user_id))

    return {
        'message': 'Write permission verified',
        'user': user.email,
        'permissions': user.permissions,
    }
