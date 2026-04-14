"""
Database session management and engine configuration.

This module provides the SQLAlchemy engine and session management for
database operations.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from app.db import get_engine


@lru_cache
def get_session_maker() -> sessionmaker[Session]:
    """Return cached SQLAlchemy session factory."""
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=get_engine(),
    )


def get_db():
    """
    Dependency function to get database session.

    Yields:
        Database session
    """
    session_maker = get_session_maker()
    db = session_maker()
    try:
        yield db
    finally:
        db.close()


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_db)]
