"""
Database session management and engine configuration.

This module provides the SQLAlchemy engine and session management for
database operations.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings

# Create database engine with connection pooling
if settings.SQLALCHEMY_DATABASE_URI is None:
    raise ValueError("SQLALCHEMY_DATABASE_URI is not configured")

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI.unicode_string(),
    pool_pre_ping=True,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function to get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_db)]
