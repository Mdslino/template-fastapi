"""
Data Transfer Objects for User use cases.

This module defines DTOs used for transferring data between layers
without exposing domain entities directly.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CreateUserDTO(BaseModel):
    """
    DTO for creating a new user.

    Attributes:
        username: Desired username
        email: Email address
        full_name: Full name (optional)
    """

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = None


class UpdateUserDTO(BaseModel):
    """
    DTO for updating user information.

    Attributes:
        full_name: Updated full name (optional)
        email: Updated email (optional)
    """

    full_name: str | None = None
    email: EmailStr | None = None


class UserDTO(BaseModel):
    """
    DTO for user data transfer.

    Used to transfer user data from domain to presentation layer.

    Attributes:
        id: User's UUID
        username: Username
        email: Email address
        full_name: Full name (optional)
        is_active: Active status
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
