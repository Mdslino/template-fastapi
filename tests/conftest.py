import contextlib
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy_utils import create_database, database_exists

# Set test environment variables before importing app modules
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('POSTGRES_PASSWORD', 'test-password')
os.environ.setdefault('POSTGRES_DB', 'test_db')
os.environ.setdefault('OAUTH2_JWKS_URL', 'https://example.com/.well-known/jwks.json')
os.environ.setdefault('OAUTH2_ISSUER', 'https://example.com')

from app.main import create_app
from shared.models import Base
from tests.factories.session import Session, engine


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


@pytest.fixture(scope='session', autouse=True)
def create_test_database():
    # Create the database and tables if they don't exist
    if database_exists(engine.url):
        # Drop tables
        Base.metadata.drop_all(bind=engine)  # type: ignore
    else:
        create_database(engine.url)

    # Create UUID extension
    database = Session()
    database.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
    database.commit()
    database.close()

    # Create tables
    Base.metadata.create_all(bind=engine)  # type: ignore

    yield


@pytest.fixture(scope='function', autouse=True)
def reset_db():
    meta = Base.metadata
    with contextlib.closing(engine.connect()) as connection:
        transaction = connection.begin()
        for table in reversed(meta.sorted_tables):
            connection.execute(table.delete())
        transaction.commit()


@pytest.fixture
def db():
    database = Session()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture
def anyio_backend():
    return 'asyncio'
