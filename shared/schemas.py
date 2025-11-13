"""
Shared base schemas for API request/response models.

These provide common patterns for API schemas across the application.
"""

import uuid
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema for all API models."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class BaseResponse(BaseSchema):
    """Base response schema with common fields."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response schema."""

    items: list[T]
    total: int
    page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)
    pages: int


class ErrorResponse(BaseSchema):
    """Standard error response schema."""

    error: str
    detail: str | None = None
    code: str | None = None


class SuccessResponse(BaseSchema):
    """Standard success response schema."""

    message: str
    data: dict | None = None
