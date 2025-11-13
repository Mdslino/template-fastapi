"""
Repository interfaces (ports) for dependency inversion.

This module defines abstract interfaces for repositories, allowing
the application layer to depend on abstractions rather than concrete
implementations.
"""

from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from app.domain.entities.user import User
from app.shared.functional.either import Either
from app.shared.functional.option import Option


class UserRepository(Protocol):
    """
    User repository interface.

    Defines the contract for user data access without specifying
    implementation details. This follows the Dependency Inversion Principle.

    Methods must return Either or Option types for functional error handling.
    """

    def save(self, user: User) -> Either[User, Exception]:
        """
        Save or update a user.

        Args:
            user: User entity to save

        Returns:
            Either containing the saved user or an exception
        """
        ...

    def find_by_id(self, user_id: UUID) -> Option[User]:
        """
        Find a user by ID.

        Args:
            user_id: User's UUID

        Returns:
            Option containing the user if found, Nothing otherwise
        """
        ...

    def find_by_username(self, username: str) -> Option[User]:
        """
        Find a user by username.

        Args:
            username: Username to search for

        Returns:
            Option containing the user if found, Nothing otherwise
        """
        ...

    def find_by_email(self, email: str) -> Option[User]:
        """
        Find a user by email.

        Args:
            email: Email to search for

        Returns:
            Option containing the user if found, Nothing otherwise
        """
        ...

    def list_all(
        self, skip: int = 0, limit: int = 100
    ) -> Either[list[User], Exception]:
        """
        List all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Either containing list of users or an exception
        """
        ...

    def delete(self, user_id: UUID) -> Either[bool, Exception]:
        """
        Delete a user by ID.

        Args:
            user_id: User's UUID

        Returns:
            Either containing True if deleted, or an exception
        """
        ...
