"""
Get user use case.

This module implements the business logic for retrieving a user by ID.
"""

from uuid import UUID

from app.application.dtos.user import UserDTO
from app.application.ports.repositories import UserRepository
from app.domain.entities.user import User
from app.domain.exceptions import EntityNotFoundException
from app.shared.functional.either import Either, Failure, Success
from app.shared.functional.option import Nothing


class GetUserUseCase:
    """
    Use case for retrieving a user by ID.

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

    def execute(self, user_id: UUID) -> Either[UserDTO, Exception]:
        """
        Execute the get user use case.

        Args:
            user_id: UUID of the user to retrieve

        Returns:
            Either containing UserDTO on success or Exception on failure

        Example:
            >>> from uuid import uuid4
            >>> use_case = GetUserUseCase(user_repo)
            >>> result = use_case.execute(uuid4())
            >>> if isinstance(result, Success):
            ...     print(f"Found user: {result.unwrap().username}")
        """
        try:
            user_option = self.user_repository.find_by_id(user_id)

            if user_option == Nothing:
                return Failure(
                    EntityNotFoundException('User', str(user_id))
                )

            # Extract user from Option (we know it's Some here)
            user = user_option.value_or(None)
            if user is None:
                return Failure(
                    EntityNotFoundException('User', str(user_id))
                )

            return Success(self._to_dto(user))

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
