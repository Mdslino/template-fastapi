"""
Application settings and configuration management.

This module defines the application settings using Pydantic Settings,
including database configuration, API settings, and logging configuration.
"""

from typing import Any

from pydantic import PostgresDsn, field_validator
from pydantic_core import MultiHostUrl
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        APP_NAME: Application name
        APP_VERSION: Application version
        DEBUG: Debug mode flag
        SECRET_KEY: Secret key for cryptographic operations
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token expiration time
        POSTGRES_PROTOCOL: PostgreSQL protocol
        POSTGRES_SERVER: PostgreSQL server host
        POSTGRES_PORT: PostgreSQL server port
        POSTGRES_USER: PostgreSQL username
        POSTGRES_PASSWORD: PostgreSQL password
        POSTGRES_DB: PostgreSQL database name
        SQLALCHEMY_DATABASE_URI: Full database URI (auto-generated)
        API_V1_STR: API v1 prefix
        LOG_LEVEL: Logging level
        LOGGING_CONFIG: Logging configuration dict
        JSON_LOGS: Whether to use JSON format for logs
        SUPABASE_SERVICE_KEY: Supabase service key (optional)
        SUPABASE_JWT_SECRET: Supabase JWT secret (optional)
        SUPABASE_URL: Supabase URL (optional)
    """

    APP_NAME: str = 'FastAPI'
    APP_VERSION: str = '0.1.0'
    DEBUG: bool = False
    SECRET_KEY: str = 'secret'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    POSTGRES_PROTOCOL: str = 'postgresql'
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_PORT: str = '5432'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'postgres'
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None
    API_V1_STR: str = '/api/v1'
    LOG_LEVEL: str = 'INFO'
    LOGGING_CONFIG: dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
    }
    JSON_LOGS: bool = False

    SUPABASE_SERVICE_KEY: str = ''
    SUPABASE_JWT_SECRET: str = ''
    SUPABASE_URL: str = ''

    @field_validator('SQLALCHEMY_DATABASE_URI')
    def assemble_db_connection(
        cls, v: PostgresDsn | None, values: FieldValidationInfo
    ) -> Any:
        """
        Assemble database connection URI from individual components.

        Args:
            v: Provided database URI
            values: Other field values

        Returns:
            PostgreSQL database URI
        """
        if isinstance(v, (MultiHostUrl, str)):
            return v
        postgres_dsn = f'{values.data["POSTGRES_PROTOCOL"]}://{values.data["POSTGRES_USER"]}:{values.data["POSTGRES_PASSWORD"]}@{values.data["POSTGRES_SERVER"]}:{values.data["POSTGRES_PORT"]}/{values.data["POSTGRES_DB"]}'
        return PostgresDsn(postgres_dsn)


settings = Settings()
