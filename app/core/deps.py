from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from gotrue import UserResponse
from sqlalchemy.orm import Session
from supabase import create_client

from app.core.config import settings
from app.db import engine

security = HTTPBearer()


def get_supabase_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserResponse:
    client = create_client(
        settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
    )
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Credentials required',
        )

    user = client.auth.get_user(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
        )

    return user


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[UserResponse, Depends(get_supabase_user)]
