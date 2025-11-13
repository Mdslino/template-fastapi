"""
FastAPI application entry point.

This module initializes and configures the FastAPI application with
middleware, logging, and routes following Clean Architecture principles.
"""

import logging
from logging.config import dictConfig

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from sqlalchemy import text

from app.infrastructure.api.dependencies import SessionDep
from app.infrastructure.config.settings import settings
from app.shared.logging import setup_logging
from app.shared.middleware import logging_middleware

logger = structlog.get_logger(__name__)

setup_logging(json_logs=settings.JSON_LOGS, log_level=settings.LOG_LEVEL)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    dictConfig(settings.LOGGING_CONFIG)
    fastapi_app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        description='FastAPI Template with Clean Architecture and OAuth2',
    )

    # Include routers
    from app.infrastructure.api.routes import protected

    fastapi_app.include_router(protected.router, prefix=settings.API_V1_STR)

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

    return fastapi_app


app = create_app()

# Add middleware
app.middleware('http')(logging_middleware)
app.add_middleware(CorrelationIdMiddleware)

if __name__ == '__main__':  # pragma: no cover
    # This is only for local development.
    import uvicorn

    fastapi_logger.setLevel(logger.level)
    app = create_app()
    uvicorn.run(app, host='0.0.0.0', port=8000)
else:
    fastapi_logger.setLevel(logging.DEBUG)
