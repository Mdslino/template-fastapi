"""
Shared base models for domain entities and database models.

These can be used across the application for consistency.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# SQLAlchemy Base
class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all database models."""

    pass


class BaseDBModel(Base):
    """Base database model with common fields for all tables."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[uuid.UUID] = mapped_column(
        index=True, unique=True, default_factory=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default_factory=datetime.now, onupdate=datetime.now
    )

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

    def __str__(self):
        return f'{self.__class__.__name__} {self.id}'


# Pydantic Base Models for Domain
class BaseDomainModel(PydanticBaseModel):
    """Base Pydantic model for domain entities."""

    model_config = {'frozen': True, 'arbitrary_types_allowed': True}


class BaseEntity(BaseDomainModel):
    """Base entity with ID fields."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
