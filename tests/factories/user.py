from factory.alchemy import SQLAlchemyModelFactory

from app.auth.models import User
from app.core.security import get_password_hash
from tests.factories.session import Session


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"

    email = "email@domain.com"
    hashed_password = get_password_hash("my_password")
    is_superuser = False
