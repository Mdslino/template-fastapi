"""
List users use case.

This module implements the business logic for listing all users with
pagination support.
"""

from app.application.dtos.user import UserDTO
from app.application.ports.repositories import UserRepository
from app.domain.entities.user import User
from app.shared.functional.either import Either, Failure


class ListUsersUseCase:
    """
    Use case for listing users with pagination.

    Attributes:
        user_repository: Repository for user data access
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the use case with its dependencies.

        Args:
            user_repository: Repository for user operations
        """
        self.user_repository = user_repository

    def execute(
        self, skip: int = 0, limit: int = 100
    ) -> Either[list[UserDTO], Exception]:
        """
        Execute the list users use case.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            Either containing list of UserDTOs or Exception

        Example:
            >>> use_case = ListUsersUseCase(user_repo)
            >>> result = use_case.execute(skip=0, limit=10)
            >>> if isinstance(result, Success):
            ...     users = result.unwrap()
            ...     print(f"Found {len(users)} users")
        """
        try:
            result = self.user_repository.list_all(skip=skip, limit=limit)
            return result.map(
                lambda users: [self._to_dto(user) for user in users]
            )
        except Exception as e:
            return Failure(e)

    @staticmethod
    def _to_dto(user: User) -> UserDTO:
        """
        Convert domain entity to DTO.

        Args:
            user: User domain entity

        Returns:
            UserDTO for transfer to presentation layer
        """
        return UserDTO(
            id=user.id,
            username=str(user.username),
            email=str(user.email),
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
