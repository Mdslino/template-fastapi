"""
Email value object for domain model.

This module provides an immutable Email value object with validation.
"""

import re

from pydantic import BaseModel, field_validator

from app.domain.exceptions import ValidationException


class Email(BaseModel):
    """
    Email value object (immutable).

    Ensures email addresses are valid and immutable. Follows value object
    pattern from DDD.

    Attributes:
        value: The email address string

    Raises:
        ValidationException: If email format is invalid

    Example:
        >>> email = Email(value="user@example.com")
        >>> email.value
        'user@example.com'
    """

    value: str

    model_config = {'frozen': True}

    @field_validator('value')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """
        Validate email format using regex.

        Args:
            v: Email string to validate

        Returns:
            Validated email string

        Raises:
            ValidationException: If email format is invalid
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValidationException(f'Invalid email format: {v}')
        return v

    def __str__(self) -> str:
        """Return string representation of email."""
        return self.value
