from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, text
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    id: int
    __name__: str

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:  # noqa
        return cls.__name__.lower()


class BaseModel(Base):  # type: ignore
    __abstract__ = True

    id = Column(  # type: ignore
        BigInteger,
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False,
        unique=True,
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=text("now()"),
    )
    updated_at = Column(
        DateTime,
        nullable=True,
        default=None,
        onupdate=datetime.utcnow,
        server_default=text("now()"),
    )
