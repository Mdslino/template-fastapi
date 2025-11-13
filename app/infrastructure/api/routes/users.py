"""
User API routes.

This module defines API endpoints for user operations using
FastAPI dependency injection for use cases.
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, status
from returns.result import Failure, Success

from app.application.dtos.user import CreateUserDTO
from app.infrastructure.api.dependencies import (
    CreateUserUseCaseDep,
    GetUserUseCaseDep,
    ListUsersUseCaseDep,
)
from app.infrastructure.api.schemas.user import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix='/users', tags=['users'])


@router.post(
    '/',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new user',
)
def create_user(
    request: UserCreateRequest,
    use_case: CreateUserUseCaseDep,
) -> UserResponse:
    """
    Create a new user.

    Args:
        request: User creation data
        use_case: CreateUserUseCase (injected via FastAPI)

    Returns:
        Created user data

    Raises:
        HTTPException: If user creation fails

    Example:
        POST /users/
        {
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe"
        }
    """
    logger.info('Creating user', username=request.username)

    dto = CreateUserDTO(
        username=request.username,
        email=request.email,
        full_name=request.full_name,
    )

    result = use_case.execute(dto)

    if isinstance(result, Success):
        user_dto = result.unwrap()
        logger.info('User created successfully', user_id=str(user_dto.id))
        return UserResponse(
            id=user_dto.id,
            username=user_dto.username,
            email=user_dto.email,
            full_name=user_dto.full_name,
            is_active=user_dto.is_active,
            created_at=user_dto.created_at,
            updated_at=user_dto.updated_at,
        )
    elif isinstance(result, Failure):
        error = result.failure()
        logger.error('Failed to create user', error=str(error))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        )


@router.get(
    '/{user_id}',
    response_model=UserResponse,
    summary='Get user by ID',
)
def get_user(
    user_id: UUID,
    use_case: GetUserUseCaseDep,
) -> UserResponse:
    """
    Get a user by their UUID.

    Args:
        user_id: User's UUID
        use_case: GetUserUseCase (injected via FastAPI)

    Returns:
        User data

    Raises:
        HTTPException: If user not found

    Example:
        GET /users/123e4567-e89b-12d3-a456-426614174000
    """
    logger.info('Getting user', user_id=str(user_id))

    result = use_case.execute(user_id)

    if isinstance(result, Success):
        user_dto = result.unwrap()
        return UserResponse(
            id=user_dto.id,
            username=user_dto.username,
            email=user_dto.email,
            full_name=user_dto.full_name,
            is_active=user_dto.is_active,
            created_at=user_dto.created_at,
            updated_at=user_dto.updated_at,
        )
    elif isinstance(result, Failure):
        error = result.failure()
        logger.error('Failed to get user', error=str(error))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        )


@router.get(
    '/',
    response_model=UserListResponse,
    summary='List all users',
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    use_case: ListUsersUseCaseDep = None,
) -> UserListResponse:
    """
    List all users with pagination.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        use_case: ListUsersUseCase (injected via FastAPI)

    Returns:
        List of users with pagination info

    Example:
        GET /users/?skip=0&limit=10
    """
    logger.info('Listing users', skip=skip, limit=limit)

    result = use_case.execute(skip=skip, limit=limit)

    if isinstance(result, Success):
        users_dto = result.unwrap()
        return UserListResponse(
            users=[
                UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                for user in users_dto
            ],
            total=len(users_dto),
            skip=skip,
            limit=limit,
        )
    elif isinstance(result, Failure):
        error = result.failure()
        logger.error('Failed to list users', error=str(error))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        )
