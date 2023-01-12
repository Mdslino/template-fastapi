from fastapi import Depends, HTTPException, status
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordBearer
from jose import exceptions, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import repository
from app.auth.models import User
from app.core import schemas, security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        logger.exception("Rolling back transaction")
        db.rollback()
        raise
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (exceptions.JWTError, ValidationError):
        detail = "Could not validate credentials"
        logger.exception(detail)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
    user = repository.user.get(db, id=token_data.sub)
    if not user:
        detail = f"User {token_data.sub} not found"
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail
        )
    logger.info(f"User {user.external_id} found")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not repository.user.is_active(current_user):
        detail = "User {current_user.external_id} is inactive"
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )
    logger.info(f"User {current_user.external_id} is active")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not repository.user.is_superuser(current_user):
        detail = f"User {current_user.external_id} is not a superuser"
        logger.error(detail)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
    logger.info(f"User {current_user.external_id} is a superuser")
    return current_user
