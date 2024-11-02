from typing import Annotated, Generator

import structlog
from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.db import engine

logger = structlog.get_logger(__name__)
security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
