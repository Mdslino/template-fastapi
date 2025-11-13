import contextlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists
from testcontainers.postgres import PostgresContainer

from app.db.base import Base
from app.main import create_app


@pytest.fixture(scope='session')
def postgres_container():
    """Start a PostgreSQL container for the test session."""
    with PostgresContainer('postgres:alpine') as postgres:
        yield postgres


@pytest.fixture(scope='session')
def engine(postgres_container):
    """Create a database engine using the testcontainer."""
    connection_url = postgres_container.get_connection_url()
    engine = create_engine(connection_url)
    return engine


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
def app(engine, Session):
    """Create app with overridden database dependency."""
    from app.core.deps import get_db
    
    def override_get_db():
        database = Session()
        try:
            yield database
        finally:
            database.close()
    
    test_app = create_app()
    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(scope='session', autouse=True)
def create_test_database(engine, Session):
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
def reset_db(engine):
    meta = Base.metadata
    with contextlib.closing(engine.connect()) as connection:
        transaction = connection.begin()
        for table in reversed(meta.sorted_tables):
            connection.execute(table.delete())
        transaction.commit()


@pytest.fixture
def db(Session):
    database = Session()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture
def anyio_backend():
    return 'asyncio'
