import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from core.config import get_settings

# Set test environment variables before creating settings
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('POSTGRES_PASSWORD', 'test-password')
os.environ.setdefault('POSTGRES_DB', 'test_db')
os.environ.setdefault('OAUTH2_JWKS_URL', 'https://example.com/.well-known/jwks.json')
os.environ.setdefault('OAUTH2_ISSUER', 'https://example.com')

settings = get_settings()

engine = create_engine(
    f'{settings.POSTGRES_PROTOCOL}://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}'
)
Session = scoped_session(sessionmaker(bind=engine))
