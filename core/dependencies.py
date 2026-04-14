"""
Core FastAPI dependencies available globally.

These dependencies can be used across all routes.
"""

from typing import Annotated

from fastapi import Depends

from app.db.session import SessionDep
from core.config import Settings, get_settings

# Type aliases for common dependencies
SettingsDep = Annotated[Settings, Depends(get_settings)]

__all__ = ['SessionDep', 'SettingsDep']
