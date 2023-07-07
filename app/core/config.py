from typing import Any, Dict, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    SECRET_KEY: str = "secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    POSTGRES_PROTOCOL: str = "postgresql+psycopg2"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    LOGGING_CONFIG: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
    }

    @field_validator("SQLALCHEMY_DATABASE_URI")
    def assemble_db_connection(
        cls, v: Optional[str], values: FieldValidationInfo
    ) -> Any:
        if isinstance(v, str):
            return v
        postgres_dsn = f"{values.data['POSTGRES_PROTOCOL']}://{values.data['POSTGRES_USER']}:{values.data['POSTGRES_PASSWORD']}@{values.data['POSTGRES_SERVER']}:{values.data['POSTGRES_PORT']}/{values.data['POSTGRES_DB']}"
        return PostgresDsn(postgres_dsn)


settings = Settings()
