from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from app import repository
from app.auth.schemas import User, UserCreate, UserUpdate
from app.core.deps import get_db, get_current_active_superuser

router = APIRouter()


@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return repository.user.create(db=db, obj_in=user)

@router.get("/users/", response_model=list[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_superuser)):
    users = repository.user.get_multi(db, skip=skip, limit=limit)
    return users
