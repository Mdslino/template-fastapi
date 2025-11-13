"""
Pydantic schemas for User API endpoints.

This module defines request/response schemas for user-related endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    """
    Schema for user creation request.

    Attributes:
        username: Desired username (3-50 chars, alphanumeric + underscore)
        email: Email address
        full_name: Full name (optional)
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$',
        description='Username (alphanumeric and underscore only)',
    )
    email: EmailStr = Field(..., description='Valid email address')
    full_name: str | None = Field(
        None, max_length=100, description='Full name'
    )


class UserUpdateRequest(BaseModel):
    """
    Schema for user update request.

    Attributes:
        email: Updated email address (optional)
        full_name: Updated full name (optional)
    """

    email: EmailStr | None = Field(None, description='Valid email address')
    full_name: str | None = Field(
        None, max_length=100, description='Full name'
    )


class UserResponse(BaseModel):
    """
    Schema for user response.

    Attributes:
        id: User's UUID
        username: Username
        email: Email address
        full_name: Full name (optional)
        is_active: Whether the user is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: UUID
    username: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class UserListResponse(BaseModel):
    """
    Schema for list of users response.

    Attributes:
        users: List of users
        total: Total number of users
        skip: Number of records skipped
        limit: Maximum number of records returned
    """

    users: list[UserResponse]
    total: int
    skip: int
    limit: int
