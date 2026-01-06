import contextlib
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists
from testcontainers.postgres import PostgresContainer

# Set test environment variables before importing app modules
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault(
    'OAUTH2_JWKS_URL', 'https://example.com/.well-known/jwks.json'
)
os.environ.setdefault('OAUTH2_ISSUER', 'https://example.com')

from app.main import create_app
from shared.models import Base


@pytest.fixture(scope='session')
def postgres_container():
    """Start a PostgreSQL container for the test session."""
    with PostgresContainer('postgres:alpine', driver='psycopg') as postgres:
        yield postgres


@pytest.fixture(scope='session')
def engine(postgres_container):
    """Create SQLAlchemy engine connected to the test container."""
    connection_url = postgres_container.get_connection_url()
    test_engine = create_engine(connection_url)

    # Create database if it doesn't exist
    if not database_exists(test_engine.url):
        create_database(test_engine.url)

    # Create UUID extension
    with test_engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        conn.commit()

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    yield test_engine

    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope='session')
def Session(engine):
    """Create a session factory."""
    return scoped_session(sessionmaker(bind=engine))


@pytest.fixture(scope='module')
def vcr_config():
    return {
        'filter_headers': ['authorization', 'apikey'],
        'filter_query_parameters': ['apikey'],
    }


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(scope='function', autouse=True)
def reset_db(engine):
    """Reset database tables between tests."""
    meta = Base.metadata
    with contextlib.closing(engine.connect()) as connection:
        transaction = connection.begin()
        for table in reversed(meta.sorted_tables):
            connection.execute(table.delete())
        transaction.commit()


@pytest.fixture
def db(Session):
    """Provide a database session for a test."""
    database = Session()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture
def anyio_backend():
    return 'asyncio'
