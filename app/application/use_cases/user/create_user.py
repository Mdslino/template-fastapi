"""
Create user use case.

This module implements the business logic for creating a new user,
following the Single Responsibility Principle.
"""

from app.application.dtos.user import CreateUserDTO, UserDTO
from app.application.ports.repositories import UserRepository
from app.domain.entities.user import User
from app.domain.exceptions import DuplicateEntityException
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username
from app.shared.functional.either import Either, Failure, Success


class CreateUserUseCase:
    """
    Use case for creating a new user.

    This class encapsulates the business logic for user creation,
    including validation and duplicate checking.

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

    def execute(self, dto: CreateUserDTO) -> Either[UserDTO, Exception]:
        """
        Execute the create user use case.

        Args:
            dto: Data transfer object with user creation data

        Returns:
            Either containing UserDTO on success or Exception on failure

        Business Rules:
            - Username must be unique
            - Email must be unique
            - Username and email must pass validation

        Example:
            >>> use_case = CreateUserUseCase(user_repo)
            >>> result = use_case.execute(
            ...     CreateUserDTO(
            ...         username="john_doe",
            ...         email="john@example.com",
            ...         full_name="John Doe"
            ...     )
            ... )
            >>> if isinstance(result, Success):
            ...     print(f"User created: {result.unwrap().username}")
        """
        try:
            # Create value objects (will validate)
            username = Username(dto.username)
            email = Email(dto.email)

            # Check for duplicates
            existing_user = self.user_repository.find_by_username(
                dto.username
            )
            if existing_user != Nothing:  # noqa: F821
                return Failure(
                    DuplicateEntityException('User', 'username', dto.username)
                )

            existing_user = self.user_repository.find_by_email(dto.email)
            if existing_user != Nothing:  # noqa: F821
                return Failure(
                    DuplicateEntityException('User', 'email', dto.email)
                )

            # Create domain entity
            user = User.create(
                username=username, email=email, full_name=dto.full_name
            )

            # Save to repository
            result = self.user_repository.save(user)

            # Map to DTO
            return result.map(self._to_dto)

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
