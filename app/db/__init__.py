from sqlmodel import create_engine
from app.core.config import settings
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI.unicode_string(), pool_pre_ping=True  # type: ignore
)
