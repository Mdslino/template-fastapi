from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False


settings = Settings()
