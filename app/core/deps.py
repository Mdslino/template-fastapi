from fastapi.logger import logger
from fastapi.security import OAuth2PasswordBearer

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
