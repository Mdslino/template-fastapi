import contextlib
import os

import pytest
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


@pytest.fixture(scope='session', autouse=True)
def setup_test_env():
    """Setup test environment before any imports."""
    # Start PostgreSQL container
    postgres = PostgresContainer('postgres:alpine', driver='psycopg')
    postgres.start()

    # Set database environment variables from container
    connection_url = postgres.get_connection_url()
    # Parse connection URL
    # postgresql+psycopg://test:test@localhost:port/test
    parts = connection_url.replace('postgresql+psycopg://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')

    os.environ['POSTGRES_USER'] = user_pass[0]
    os.environ['POSTGRES_PASSWORD'] = user_pass[1]
    os.environ['POSTGRES_SERVER'] = host_port[0]
    os.environ['POSTGRES_PORT'] = host_port[1]
    os.environ['POSTGRES_DB'] = host_port_db[1]

    yield

    # Cleanup
    postgres.stop()


# Import after environment setup (noqa required - env must be set first)
from fastapi.testclient import TestClient  # noqa: E402

from app.main import create_app  # noqa: E402
from shared.models import Base  # noqa: E402


@pytest.fixture(scope='session')
def postgres_container():
    """Get PostgreSQL container connection info."""
    from core.config import settings

    connection_url = settings.SQLALCHEMY_DATABASE_URI.unicode_string()
    return connection_url


@pytest.fixture(scope='session')
def engine(setup_test_env):
    """Create SQLAlchemy engine connected to the test container."""
    from core.config import settings

    connection_url = settings.SQLALCHEMY_DATABASE_URI.unicode_string()
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
