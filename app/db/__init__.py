from functools import lru_cache

from sqlalchemy import Engine, create_engine

from core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Return cached SQLAlchemy engine."""
    settings = get_settings()
    return create_engine(
        settings.SQLALCHEMY_DATABASE_URI.unicode_string(),
        pool_pre_ping=True,  # type: ignore[arg-type]
    )


__all__ = ['get_engine']
