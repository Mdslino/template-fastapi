from app import repository


def test_get_user_by_id(user_factory, db):
    user = repository.user.get_by_id(db=db, user_id=user_factory.id)
    assert user.id == user_factory.id
    assert user.email == user_factory.email
    assert user.is_superuser == user_factory.is_superuser
    assert user.is_active == user_factory.is_active
