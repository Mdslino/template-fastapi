import logging
from logging.config import dictConfig

from fastapi import FastAPI

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_app():
    dictConfig(settings.LOGGING_CONFIG)
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    @app.get("/healthcheck")
    def healthcheck():
        logger.info("App is healthy!")
        return {"status": "ok"}

    return app


if __name__ == "__main__":  # pragma: no cover
    # This is only for local development.
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
