from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:  # noqa
        return cls.__name__.lower()


class BaseModel(Base):  # type: ignore
    __abstract__ = True

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False,
        unique=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=True, default=None, onupdate=datetime.utcnow
    )
