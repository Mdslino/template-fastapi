from fastapi import Depends, status
from fastapi.routing import APIRouter
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import repository
from app.auth import models, schemas
from app.core.deps import (
    get_current_active_superuser,
    get_current_active_user,
    get_db,
)

router = APIRouter()


@router.post(
    "/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return repository.user.create(db=db, obj_in=user)


@router.get("/users/", response_model=list[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    super_user: models.User = Depends(get_current_active_superuser),
):
    users = repository.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.patch("/users/me", response_model=schemas.User)
def update_user_me(
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    return repository.user.update(db=db, db_obj=current_user, obj_in=user)


@router.patch("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: UUID4,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    super_user: models.User = Depends(get_current_active_superuser),
):
    return repository.user.update(
        db=db,
        db_obj=repository.user.get_by_external_id(db, external_id=user_id),
        obj_in=user,
    )
