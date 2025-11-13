"""
SQLAlchemy base models and ORM definitions.

This module defines the base declarative class and common model attributes
for all database models.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class BaseModel(Base):
    """
    Base model with common fields for all entities.

    Provides id, external_id, created_at, and updated_at fields that are
    common across all entities in the system.

    Attributes:
        id: Primary key (internal use only)
        external_id: UUID for external API exposure
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[uuid.UUID] = mapped_column(
        index=True, unique=True, default_factory=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default_factory=datetime.now, onupdate=datetime.now
    )

    def __repr__(self) -> str:
        """Return string representation of the model."""
        return f'<{self.__class__.__name__} {self.id}>'

    def __str__(self) -> str:
        """Return string representation of the model."""
        return f'{self.__class__.__name__} {self.id}'
