"""
FastAPI application entry point.

This module initializes and configures the FastAPI application with
middleware, logging, and routes.
"""

import logging
from logging.config import dictConfig

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from sqlalchemy import text

from app.db.session import SessionDep
from core.config import settings
from core.logging import setup_logging
from core.middleware import logging_middleware


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    # Setup logging
    setup_logging(json_logs=settings.JSON_LOGS, log_level=settings.LOG_LEVEL)
    logger = structlog.get_logger(__name__)
    
    dictConfig(settings.LOGGING_CONFIG)
    fastapi_app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        description='FastAPI Template',
    )

    # Include API routers
    from app.api.v1 import router as api_v1_router

    fastapi_app.include_router(api_v1_router)

    @fastapi_app.get('/healthcheck', tags=['health'])
    def healthcheck(db: SessionDep) -> dict:
        """
        Health check endpoint.

        Verifies application and database connectivity.

        Args:
            db: Database session (injected)

        Returns:
            Health status of app and database
        """
        db_status = 'ok'
        try:
            db.execute(text('SELECT 1'))
        except Exception as e:
            db_status = 'error'
            logger.error('Database is not available', exc_info=e)

        return {
            'app': 'ok',
            'db': db_status,
            'version': settings.APP_VERSION,
        }

    # Add middleware
    fastapi_app.middleware('http')(logging_middleware)
    fastapi_app.add_middleware(CorrelationIdMiddleware)

    return fastapi_app


# Create app instance for production
app = create_app()

if __name__ == '__main__':  # pragma: no cover
    # This is only for local development.
    import uvicorn

    fastapi_logger.setLevel(logging.DEBUG)
    uvicorn.run(app, host='0.0.0.0', port=8000)
else:
    fastapi_logger.setLevel(logging.DEBUG)
