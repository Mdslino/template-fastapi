"""Healthcheck service logic."""

import structlog
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.config import settings

logger = structlog.get_logger(__name__)


def check_health(db: Session) -> dict[str, str]:
    """Validate app and database availability."""
    db_status = 'ok'
    try:
        db.execute(text('SELECT 1'))
    except Exception as exc:
        db_status = 'error'
        logger.error('Database is not available', exc_info=exc)

    return {
        'app': 'ok',
        'db': db_status,
        'version': settings.APP_VERSION,
    }
