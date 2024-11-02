import contextlib

import pytest
from fastapi.testclient import TestClient
from gotrue import UserResponse
from sqlalchemy import text
from sqlalchemy_utils import create_database, database_exists

from app.db.base import Base
from app.main import create_app
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


@pytest.fixture
def supabase_user():
    return UserResponse(**{
        'user': {
            'id': '1b278ccb-9ebb-4a96-b7ef-576b57a18931',
            'app_metadata': {'provider': 'email', 'providers': ['email']},
            'user_metadata': {},
            'aud': 'authenticated',
            'confirmation_sent_at': None,
            'recovery_sent_at': None,
            'email_change_sent_at': None,
            'new_email': None,
            'new_phone': None,
            'invited_at': None,
            'action_link': None,
            'email': 'email@domain.com',
            'phone': '',
            'created_at': '2024-09-02T22:32:00.411824Z',
            'confirmed_at': '2024-09-02T22:32:00.418600Z',
            'email_confirmed_at': '2024-09-02T22:32:00.418600Z',
            'phone_confirmed_at': None,
            'last_sign_in_at': '2024-09-02T22:36:58.736282Z',
            'role': 'authenticated',
            'updated_at': '2024-09-02T22:36:58.737969Z',
            'identities': [
                {
                    'id': '1b278ccb-9ebb-4a96-b7ef-576b57a18931',
                    'identity_id': '320dfa25-ad88-48a7-892a-079540688613',
                    'user_id': '1b278ccb-9ebb-4a96-b7ef-576b57a18931',
                    'identity_data': {
                        'email': 'email@domain.com',
                        'email_verified': True,
                        'phone_verified': False,
                        'sub': '1b278ccb-9ebb-4a96-b7ef-576b57a18931',
                    },
                    'provider': 'email',
                    'created_at': '2024-09-02T22:32:00.415439Z',
                    'last_sign_in_at': '2024-09-02T22:32:00.415382Z',
                    'updated_at': '2024-09-02T22:32:00.415439Z',
                }
            ],
            'is_anonymous': False,
            'factors': None,
        }
    })
