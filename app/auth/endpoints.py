from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import repository
from app.auth.models import User
from app.auth.schemas import User as UserSchema
from app.auth.schemas import UserCreate
from app.core.deps import get_current_active_user, get_db
from app.core.schemas import Token

router = APIRouter()


@router.get("/users/me")
def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> UserSchema:
    return current_user


@router.post("/login/access-token")
def login_access_token(
    user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    user = repository.user.authenticate(
        db=db, email=user.username, password=user.password
    )

    access_token = repository.user.create_access_token_for_user(user)

    return Token(access_token=access_token)


@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserSchema:
    user = repository.user.create(db=db, obj_in=user)

    return user
