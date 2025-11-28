"""
Database session management and engine configuration.

This module provides the SQLAlchemy engine and session management for
database operations.
"""

from sqlalchemy import create_engine

from core.config import settings

# Create database engine with connection pooling
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI.unicode_string(),
    pool_pre_ping=True,  # type: ignore
)
