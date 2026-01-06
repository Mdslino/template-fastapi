"""
Database session management and engine configuration.

This module provides the SQLAlchemy engine and session management for
database operations.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from app.db import get_engine


def get_session_local():
    """Get or create SessionLocal (lazy initialization)."""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function to get database session.

    Yields:
        Database session
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_db)]
