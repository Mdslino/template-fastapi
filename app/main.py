from fastapi import FastAPI

from app.core.config import settings


def create_app():
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    @app.get("/healthcheck")
    def healthcheck():
        return {"status": "ok"}

    return app


if __name__ == "__main__":  # pragma: no cover
    # This is only for local development.
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
