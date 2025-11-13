"""Tests for user use cases."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from returns.result import Failure, Success

from app.application.dtos.user import CreateUserDTO
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.application.use_cases.user.get_user import GetUserUseCase
from app.application.use_cases.user.list_users import ListUsersUseCase
from app.domain.entities.user import User
from app.domain.exceptions import (
    DuplicateEntityException,
    EntityNotFoundException,
)
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username
from app.shared.functional.option import Nothing, Some


class TestCreateUserUseCase:
    """Test CreateUserUseCase."""

    def test_create_user_success(self):
        """Test successfully creating a user."""
        # Arrange
        mock_repo = Mock()
        mock_repo.find_by_username.return_value = Nothing
        mock_repo.find_by_email.return_value = Nothing

        created_user = User.create(
            username=Username(value='john_doe'),
            email=Email(value='john@example.com'),
            full_name='John Doe',
        )
        mock_repo.save.return_value = Success(created_user)

        use_case = CreateUserUseCase(mock_repo)
        dto = CreateUserDTO(
            username='john_doe',
            email='john@example.com',
            full_name='John Doe',
        )

        # Act
        result = use_case.execute(dto)

        # Assert
        assert isinstance(result, Success)
        user_dto = result.unwrap()
        assert user_dto.username == 'john_doe'
        assert user_dto.email == 'john@example.com'
        assert user_dto.full_name == 'John Doe'
        mock_repo.save.assert_called_once()

    def test_create_user_duplicate_username(self):
        """Test creating a user with duplicate username."""
        # Arrange
        existing_user = User.create(
            username=Username(value='john_doe'),
            email=Email(value='existing@example.com'),
        )
        mock_repo = Mock()
        mock_repo.find_by_username.return_value = Some(existing_user)

        use_case = CreateUserUseCase(mock_repo)
        dto = CreateUserDTO(username='john_doe', email='john@example.com')

        # Act
        result = use_case.execute(dto)

        # Assert
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, DuplicateEntityException)
        mock_repo.save.assert_not_called()

    def test_create_user_duplicate_email(self):
        """Test creating a user with duplicate email."""
        # Arrange
        existing_user = User.create(
            username=Username(value='existing_user'),
            email=Email(value='john@example.com'),
        )
        mock_repo = Mock()
        mock_repo.find_by_username.return_value = Nothing
        mock_repo.find_by_email.return_value = Some(existing_user)

        use_case = CreateUserUseCase(mock_repo)
        dto = CreateUserDTO(username='john_doe', email='john@example.com')

        # Act
        result = use_case.execute(dto)

        # Assert
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, DuplicateEntityException)
        mock_repo.save.assert_not_called()


class TestGetUserUseCase:
    """Test GetUserUseCase."""

    def test_get_user_success(self):
        """Test successfully getting a user."""
        # Arrange
        user_id = uuid4()
        user = User.create(
            username=Username(value='john_doe'),
            email=Email(value='john@example.com'),
        )
        user.id = user_id

        mock_repo = Mock()
        mock_repo.find_by_id.return_value = Some(user)

        use_case = GetUserUseCase(mock_repo)

        # Act
        result = use_case.execute(user_id)

        # Assert
        assert isinstance(result, Success)
        user_dto = result.unwrap()
        assert user_dto.id == user_id
        assert user_dto.username == 'john_doe'

    def test_get_user_not_found(self):
        """Test getting a non-existent user."""
        # Arrange
        user_id = uuid4()
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = Nothing

        use_case = GetUserUseCase(mock_repo)

        # Act
        result = use_case.execute(user_id)

        # Assert
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, EntityNotFoundException)


class TestListUsersUseCase:
    """Test ListUsersUseCase."""

    def test_list_users_success(self):
        """Test successfully listing users."""
        # Arrange
        users = [
            User.create(
                username=Username(value='john_doe'),
                email=Email(value='john@example.com'),
            ),
            User.create(
                username=Username(value='jane_doe'),
                email=Email(value='jane@example.com'),
            ),
        ]

        mock_repo = Mock()
        mock_repo.list_all.return_value = Success(users)

        use_case = ListUsersUseCase(mock_repo)

        # Act
        result = use_case.execute(skip=0, limit=10)

        # Assert
        assert isinstance(result, Success)
        users_dto = result.unwrap()
        assert len(users_dto) == 2
        assert users_dto[0].username == 'john_doe'
        assert users_dto[1].username == 'jane_doe'

    def test_list_users_empty(self):
        """Test listing users when there are none."""
        # Arrange
        mock_repo = Mock()
        mock_repo.list_all.return_value = Success([])

        use_case = ListUsersUseCase(mock_repo)

        # Act
        result = use_case.execute(skip=0, limit=10)

        # Assert
        assert isinstance(result, Success)
        users_dto = result.unwrap()
        assert len(users_dto) == 0
