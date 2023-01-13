import pytest

from app import repository
from app.auth.schemas import UserCreate, UserUpdate


def test_get_user_by_email(user_factory, db):
    user = user_factory
    found_user = repository.user.get_by_email(db=db, email=user.email)
    assert found_user
    assert found_user.email == user.email
    assert found_user.hashed_password == user.hashed_password
    assert found_user.is_active
    assert not found_user.is_superuser


def test_create_user(db, faker):
    password = faker.password()
    user_in = UserCreate(
        email=faker.email(), password=password, password2=password
    )
    user = repository.user.create(db=db, obj_in=user_in)
    assert user
    assert user.email == user_in.email
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.hashed_password is not None
    assert user.hashed_password != user_in.password


@pytest.mark.parametrize(
    "data",
    [
        {"password": "new_password", "email": "new_email@domain.com"},
        UserUpdate(
            password="new_password",
            email="new_email@domain.com",
            password2="new_password",
        ),
    ],
)
def test_update_user(user_factory, db, data):
    user_create = user_factory
    user = repository.user.get_by_email(db=db, email=user_create.email)
    user = repository.user.update(db=db, db_obj=user, obj_in=data)
    assert user
    assert user.email != user_factory.email
    assert user.hashed_password != user_factory.hashed_password


def test_authenticate_user(user_factory, db):
    user = user_factory
    authenticated_user = repository.user.authenticate(
        db=db, email=user.email, password="password"
    )
    assert authenticated_user
    assert authenticated_user.email == user.email
