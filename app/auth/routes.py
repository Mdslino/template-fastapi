"""
Authentication routes.

This module provides endpoints for authentication-related operations.
These serve as examples of how to use the authentication dependencies.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import CurrentUserDep, RequirePermissions
from app.auth.schemas import AuthenticatedUser

router = APIRouter(prefix='/auth', tags=['authentication'])


@router.get('/me')
def get_current_user_info(user: CurrentUserDep) -> dict:
    """
    Get current authenticated user information.

    This endpoint demonstrates basic authentication using CurrentUserDep.
    Any request with a valid Auth0 token can access this endpoint.

    Returns:
        User information including ID and permissions
    """
    return {
        'user_id': user.user_id,
        'permissions': user.permissions,
    }


# Example: Require specific permissions
require_admin = RequirePermissions(['admin:write'])


@router.get('/admin')
def admin_only_endpoint(
    user: Annotated[AuthenticatedUser, Depends(require_admin)],
) -> dict:
    """
    Admin-only endpoint.

    This endpoint demonstrates permission-based authorization.
    Only users with 'admin:write' permission can access this.

    Returns:
        Success message with user info
    """
    return {
        'message': 'Admin access granted',
        'user_id': user.user_id,
    }


@router.get('/data/read')
def read_data_endpoint(
    user: Annotated[
        AuthenticatedUser, Depends(RequirePermissions(['read:data']))
    ],
) -> dict:
    """
    Read data endpoint.

    Requires 'read:data' permission.

    Returns:
        Mock data response
    """
    return {
        'data': ['item1', 'item2', 'item3'],
        'user_id': user.user_id,
    }


@router.post('/data/write')
def write_data_endpoint(
    user: Annotated[
        AuthenticatedUser, Depends(RequirePermissions(['write:data']))
    ],
) -> dict:
    """
    Write data endpoint.

    Requires 'write:data' permission.

    Returns:
        Success message
    """
    return {
        'message': 'Data written successfully',
        'user_id': user.user_id,
    }
