import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger

from app.core.config import settings

gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

fastapi_logger.handlers = gunicorn_error_logger.handlers


def create_app():
    dictConfig(settings.LOGGING_CONFIG)
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    @app.get("/healthcheck")
    def healthcheck():
        fastapi_logger.info("App is healthy!")
        return {"status": "ok"}

    return app


if __name__ == "__main__":  # pragma: no cover
    # This is only for local development.
    import uvicorn

    fastapi_logger.setLevel(gunicorn_logger.level)
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
else:
    fastapi_logger.setLevel(logging.DEBUG)
