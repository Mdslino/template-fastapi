"""
Core FastAPI dependencies available globally.

These dependencies can be used across all routes.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from core.config import Settings, get_settings

# Type aliases for common dependencies
SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_session)]
