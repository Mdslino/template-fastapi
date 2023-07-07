from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI.unicode_string(), pool_pre_ping=True  # type: ignore
)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
