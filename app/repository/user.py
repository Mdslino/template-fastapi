# SQLAlchemy User Repository
from typing import Optional

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.exceptions import (
    UserNotFoundException,
    UserWrongPasswordException,
)
from app.auth.models import User
from app.auth.schemas import UserCreate, UserUpdate
from app.core.security import create_access_token
from app.repository.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def create(self, *, db: Session, obj_in: UserCreate) -> User:
        user = User(email=obj_in.email)
        user.set_password(obj_in.password)
        db.add(user)
        db.commit()

        return user

    def get_by_email(self, *, db: Session, email: str) -> Optional[User]:
        query = select(self.model).where(self.model.email == email)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_by_external_id(
        self, *, db: Session, external_id: UUID4
    ) -> Optional[User]:
        query = select(self.model).where(self.model.external_id == external_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_by_id(self, *, db: Session, user_id: int) -> Optional[User]:
        query = select(self.model).where(self.model.id == user_id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def authenticate(
        self, *, db: Session, email: str, password: str
    ) -> Optional[User]:
        user_obj = self.get_by_email(db=db, email=email)
        if not user_obj:
            raise UserNotFoundException(email=email)
        if not user_obj.check_password(password):
            raise UserWrongPasswordException(email=email)
        return user_obj

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        return create_access_token(user.external_id)

    @staticmethod
    def is_active(user: User) -> bool:
        return user.is_active


user = UserRepository(User)
