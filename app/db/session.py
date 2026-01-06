"""
Database session management and engine configuration.

This module provides the SQLAlchemy engine and session management for
database operations.
"""

from sqlalchemy import create_engine

from core.config import settings

# Create database engine with connection pooling
if settings.SQLALCHEMY_DATABASE_URI is None:
    raise ValueError("SQLALCHEMY_DATABASE_URI is not configured")

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI.unicode_string(),
    pool_pre_ping=True,  # type: ignore
)
