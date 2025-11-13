"""
FastAPI dependency injection functions.

This module provides dependency injection functions for FastAPI routes,
including database session management, repositories, and use cases.
"""

from typing import Annotated, Generator

import structlog
from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.infrastructure.database.session import engine

logger = structlog.get_logger(__name__)
security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """
    Provide database session dependency.

    Yields a database session and ensures it's properly closed after use.

    Yields:
        Database session

    Example:
        >>> from fastapi import Depends
        >>> @app.get("/items/")
        >>> def read_items(db: Session = Depends(get_db)):
        ...     return db.query(Item).all()
    """
    with Session(engine) as session:
        yield session


# Type alias for database session dependency
SessionDep = Annotated[Session, Depends(get_db)]


# Repository Dependencies
def get_user_repository(
    db: SessionDep,
) -> 'SQLAlchemyUserRepository':
    """
    Provide UserRepository dependency.

    Args:
        db: Database session (injected)

    Returns:
        UserRepository implementation

    Example:
        >>> from fastapi import Depends
        >>> @app.get("/users/")
        >>> def list_users(repo: UserRepository = Depends(get_user_repository)):
        ...     return repo.list_all()
    """
    from app.infrastructure.database.repositories.user_repository import (
        SQLAlchemyUserRepository,
    )

    return SQLAlchemyUserRepository(db)


UserRepositoryDep = Annotated[
    'SQLAlchemyUserRepository', Depends(get_user_repository)
]


# Use Case Dependencies
def get_create_user_use_case(
    user_repository: UserRepositoryDep,
) -> 'CreateUserUseCase':
    """
    Provide CreateUserUseCase dependency.

    Args:
        user_repository: User repository (injected)

    Returns:
        CreateUserUseCase instance

    Example:
        >>> from fastapi import Depends
        >>> @app.post("/users/")
        >>> def create_user(
        ...     use_case: CreateUserUseCase = Depends(get_create_user_use_case)
        ... ):
        ...     return use_case.execute(dto)
    """
    from app.application.use_cases.user.create_user import CreateUserUseCase

    return CreateUserUseCase(user_repository)


CreateUserUseCaseDep = Annotated[
    'CreateUserUseCase', Depends(get_create_user_use_case)
]


def get_get_user_use_case(
    user_repository: UserRepositoryDep,
) -> 'GetUserUseCase':
    """
    Provide GetUserUseCase dependency.

    Args:
        user_repository: User repository (injected)

    Returns:
        GetUserUseCase instance
    """
    from app.application.use_cases.user.get_user import GetUserUseCase

    return GetUserUseCase(user_repository)


GetUserUseCaseDep = Annotated['GetUserUseCase', Depends(get_get_user_use_case)]


def get_list_users_use_case(
    user_repository: UserRepositoryDep,
) -> 'ListUsersUseCase':
    """
    Provide ListUsersUseCase dependency.

    Args:
        user_repository: User repository (injected)

    Returns:
        ListUsersUseCase instance
    """
    from app.application.use_cases.user.list_users import ListUsersUseCase

    return ListUsersUseCase(user_repository)


ListUsersUseCaseDep = Annotated[
    'ListUsersUseCase', Depends(get_list_users_use_case)
]
