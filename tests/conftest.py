import contextlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import create_app
from tests.factories.user_factory import UserFactory


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    # Create the database and tables if they don't exist
    if database_exists(engine.url):
        # Drop tables
        Base.metadata.drop_all(bind=engine)  # type: ignore
    else:
        create_database(engine.url)

    # Create UUID extension
    db = SessionLocal()
    db.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    db.commit()
    db.close()

    # Create tables
    Base.metadata.create_all(bind=engine)  # type: ignore

    yield

    # Drop tables
    Base.metadata.drop_all(bind=engine)  # type: ignore


@pytest.fixture(scope="function", autouse=True)
def reset_db():
    meta = Base.metadata
    with contextlib.closing(engine.connect()) as connection:
        transaction = connection.begin()
        for table in reversed(meta.sorted_tables):
            connection.execute(table.delete())
        transaction.commit()


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_factory():
    user = UserFactory()
    return user


@pytest.fixture
def superuser_factory():
    user = UserFactory(is_superuser=True)
    return user


@pytest.fixture
def super_user_token(superuser_factory):
    return create_access_token(superuser_factory.external_id)


@pytest.fixture
def user_token(user_factory):
    return create_access_token(user_factory.external_id)


@pytest.fixture
def anyio_backend():
    return "asyncio"
