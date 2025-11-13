"""
Username value object for domain model.

This module provides an immutable Username value object with validation.
"""

from pydantic import BaseModel, field_validator

from app.domain.exceptions import ValidationException


class Username(BaseModel):
    """
    Username value object (immutable).

    Ensures usernames are valid and immutable. Follows value object
    pattern from DDD.

    Attributes:
        value: The username string

    Raises:
        ValidationException: If username format is invalid

    Example:
        >>> username = Username(value="john_doe")
        >>> username.value
        'john_doe'
    """

    value: str

    model_config = {'frozen': True}

    @field_validator('value')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.

        Username must be 3-50 characters, alphanumeric with underscores.

        Args:
            v: Username string to validate

        Returns:
            Validated username string

        Raises:
            ValidationException: If username format is invalid
        """
        if not v:
            raise ValidationException('Username cannot be empty')
        if len(v) < 3:
            raise ValidationException('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValidationException('Username must be at most 50 characters')
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValidationException(
                'Username can only contain letters, numbers, and underscores'
            )
        return v

    def __str__(self) -> str:
        """Return string representation of username."""
        return self.value
