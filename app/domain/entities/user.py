"""
User domain entity.

This module defines the User entity with business logic and domain rules.
"""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username


class User(BaseModel):
    """
    User domain entity.

    Represents a user in the system with business logic and validation.
    This is a pure domain entity that does not depend on any infrastructure
    concerns (databases, APIs, etc.).

    Attributes:
        id: User's UUID (external identifier)
        username: User's username (value object)
        email: User's email address (value object)
        full_name: User's full name (optional)
        is_active: Whether the user account is active
        created_at: When the user was created
        updated_at: When the user was last updated

    Example:
        >>> from app.domain.value_objects.email import Email
        >>> from app.domain.value_objects.username import Username
        >>> user = User.create(
        ...     username=Username(value="john_doe"),
        ...     email=Email(value="john@example.com"),
        ...     full_name="John Doe"
        ... )
        >>> user.is_active
        True
    """

    id: UUID = Field(default_factory=uuid4)
    username: Username
    email: Email
    full_name: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {'arbitrary_types_allowed': True}

    @classmethod
    def create(
        cls,
        username: Username,
        email: Email,
        full_name: str | None = None,
    ) -> 'User':
        """
        Factory method to create a new user.

        Args:
            username: User's username
            email: User's email
            full_name: User's full name (optional)

        Returns:
            New User entity with generated ID and timestamps
        """
        return cls(username=username, email=email, full_name=full_name)

    def deactivate(self) -> None:
        """
        Deactivate the user account.

        Business rule: A deactivated user cannot access the system.
        """
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """
        Activate the user account.

        Business rule: An activated user can access the system.
        """
        self.is_active = True
        self.updated_at = datetime.now()

    def update_profile(
        self, full_name: str | None = None, email: Email | None = None
    ) -> None:
        """
        Update user profile information.

        Args:
            full_name: New full name (optional)
            email: New email (optional)
        """
        if full_name is not None:
            self.full_name = full_name
        if email is not None:
            self.email = email
        self.updated_at = datetime.now()
