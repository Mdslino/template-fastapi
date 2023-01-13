from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from sqlalchemy.orm import scoped_session

from app.auth.models import User
from app.core.security import get_password_hash
from app.db.session import SessionLocal


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = scoped_session(SessionLocal)
        sqlalchemy_session_persistence = "commit"

    email = Sequence(lambda n: Faker().email())
    hashed_password = get_password_hash("password")
    is_active = True
