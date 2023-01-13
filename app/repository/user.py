from typing import Any, Dict, Optional, Union

from fastapi.logger import logger
from pydantic import UUID4, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.utils import hide_email
from app.repository.base import RepositoryBase


class UserRepository(RepositoryBase[User, UserCreate, UserUpdate]):
    def get_by_external_id(
        self, db: Session, external_id: UUID4
    ) -> Optional[User]:
        stmt = select(self.model).where(self.model.external_id == external_id)
        result = db.execute(stmt)
        return result.scalars().first()

    def get_by_email(self, db: Session, *, email: EmailStr) -> Optional[User]:
        logger.info(f"Getting user by email {hide_email(email)}")
        stmt = select(User).where(User.email == email)
        result = db.execute(stmt)
        return result.scalars().first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        logger.info(f"Creating user {hide_email(obj_in.email)}")
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=False,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"User {hide_email(obj_in.email)} created")
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
            return self.update(
                db=db, db_obj=db_obj, obj_in=UserUpdate(**update_data)
            )
        else:
            update_data = obj_in.dict(
                exclude_unset=True, exclude={"password2"}
            )

        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.commit()
        db.refresh(db_obj)
        logger.info(f"User {hide_email(db_obj.email)} updated")
        return db_obj

    def authenticate(
        self, db: Session, *, email: EmailStr, password: str
    ) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            logger.warning(f"User {hide_email(email)} not found")

        if not verify_password(password, user.hashed_password):  # type: ignore
            logger.warning(f"Wrong password for user {hide_email(email)}")

        if self.is_active(user):
            logger.info(f"User {hide_email(email)} authenticated")
            return user

        return None

    def is_active(self, user: User) -> bool:
        return user.is_active  # type: ignore

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser  # type: ignore


user = UserRepository(User)
