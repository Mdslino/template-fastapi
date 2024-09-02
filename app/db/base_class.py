import uuid
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
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
