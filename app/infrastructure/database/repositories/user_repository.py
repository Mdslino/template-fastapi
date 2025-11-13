"""
SQLAlchemy User repository implementation.

This module implements the UserRepository interface using SQLAlchemy
for database operations.
"""

from uuid import UUID

import structlog
from sqlalchemy import String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.application.ports.repositories import UserRepository
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username
from app.infrastructure.database.models import Base, BaseModel
from app.shared.functional.either import Either, Failure, Success
from app.shared.functional.option import Nothing, Option, Some

logger = structlog.get_logger(__name__)


# SQLAlchemy ORM Model for User
class UserModel(BaseModel, Base):
    """
    SQLAlchemy ORM model for User entity.

    Maps domain User entity to database table.
    """

    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class SQLAlchemyUserRepository(UserRepository):
    """
    SQLAlchemy implementation of UserRepository.

    Implements data access operations for User entities using SQLAlchemy.

    Attributes:
        session: SQLAlchemy database session
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations
        """
        self.session = session

    def save(self, user: User) -> Either[User, Exception]:
        """
        Save or update a user in the database.

        Args:
            user: User entity to save

        Returns:
            Either containing the saved user or an exception
        """
        try:
            # Check if user exists
            stmt = select(UserModel).where(
                UserModel.external_id == user.id
            )
            db_user = self.session.scalar(stmt)

            if db_user:
                # Update existing user
                db_user.username = str(user.username)
                db_user.email = str(user.email)
                db_user.full_name = user.full_name
                db_user.is_active = user.is_active
                db_user.updated_at = user.updated_at
            else:
                # Create new user
                db_user = UserModel(
                    external_id=user.id,
                    username=str(user.username),
                    email=str(user.email),
                    full_name=user.full_name,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                self.session.add(db_user)

            self.session.commit()
            self.session.refresh(db_user)

            # Convert back to domain entity
            domain_user = self._to_domain(db_user)
            return Success(domain_user)

        except IntegrityError as e:
            self.session.rollback()
            logger.error('Database integrity error', exc_info=e)
            return Failure(e)
        except Exception as e:
            self.session.rollback()
            logger.error('Error saving user', exc_info=e)
            return Failure(e)

    def find_by_id(self, user_id: UUID) -> Option[User]:
        """
        Find a user by UUID.

        Args:
            user_id: User's UUID

        Returns:
            Option containing the user if found, Nothing otherwise
        """
        try:
            stmt = select(UserModel).where(
                UserModel.external_id == user_id
            )
            db_user = self.session.scalar(stmt)

            if db_user:
                return Some(self._to_domain(db_user))
            return Nothing

        except Exception as e:
            logger.error('Error finding user by id', exc_info=e)
            return Nothing

    def find_by_username(self, username: str) -> Option[User]:
        """
        Find a user by username.

        Args:
            username: Username to search for

        Returns:
            Option containing the user if found, Nothing otherwise
        """
        try:
            stmt = select(UserModel).where(UserModel.username == username)
            db_user = self.session.scalar(stmt)

            if db_user:
                return Some(self._to_domain(db_user))
            return Nothing

        except Exception as e:
            logger.error('Error finding user by username', exc_info=e)
            return Nothing

    def find_by_email(self, email: str) -> Option[User]:
        """
        Find a user by email.

        Args:
            email: Email to search for

        Returns:
            Option containing the user if found, Nothing otherwise
        """
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            db_user = self.session.scalar(stmt)

            if db_user:
                return Some(self._to_domain(db_user))
            return Nothing

        except Exception as e:
            logger.error('Error finding user by email', exc_info=e)
            return Nothing

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
        try:
            stmt = select(UserModel).offset(skip).limit(limit)
            db_users = self.session.scalars(stmt).all()

            users = [self._to_domain(db_user) for db_user in db_users]
            return Success(users)

        except Exception as e:
            logger.error('Error listing users', exc_info=e)
            return Failure(e)

    def delete(self, user_id: UUID) -> Either[bool, Exception]:
        """
        Delete a user by UUID.

        Args:
            user_id: User's UUID

        Returns:
            Either containing True if deleted, or an exception
        """
        try:
            stmt = select(UserModel).where(
                UserModel.external_id == user_id
            )
            db_user = self.session.scalar(stmt)

            if db_user:
                self.session.delete(db_user)
                self.session.commit()
                return Success(True)

            return Success(False)

        except Exception as e:
            self.session.rollback()
            logger.error('Error deleting user', exc_info=e)
            return Failure(e)

    @staticmethod
    def _to_domain(db_user: UserModel) -> User:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            db_user: SQLAlchemy UserModel instance

        Returns:
            Domain User entity
        """
        return User(
            id=db_user.external_id,
            username=Username(value=db_user.username),
            email=Email(value=db_user.email),
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
