from fastapi import FastAPI


def create_app():
    app = FastAPI()

    @app.get("/healthcheck")
    def healthcheck():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
