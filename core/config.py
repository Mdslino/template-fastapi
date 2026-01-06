"""
Application settings and configuration management.

This module defines the application settings using Pydantic Settings,
including database configuration, API settings, logging configuration,
and OAuth2 authentication settings.
"""

from typing import Any

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        APP_NAME: Application name
        APP_VERSION: Application version
        DEBUG: Debug mode flag
        SECRET_KEY: Secret key for cryptographic operations
        POSTGRES_PROTOCOL: PostgreSQL protocol
        POSTGRES_SERVER: PostgreSQL server host
        POSTGRES_PORT: PostgreSQL server port
        POSTGRES_USER: PostgreSQL username
        POSTGRES_PASSWORD: PostgreSQL password
        POSTGRES_DB: PostgreSQL database name
        API_V1_STR: API v1 prefix
        LOG_LEVEL: Logging level
        LOGGING_CONFIG: Logging configuration dict
        JSON_LOGS: Whether to use JSON format for logs
    """

    APP_NAME: str = 'FastAPI'
    APP_VERSION: str = '0.1.0'
    DEBUG: bool = False
    SECRET_KEY: str = ''
    POSTGRES_PROTOCOL: str = 'postgresql+psycopg'
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_PORT: str = '5432'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = ''
    POSTGRES_DB: str = 'postgres'
    API_V1_STR: str = '/api/v1'
    LOG_LEVEL: str = 'INFO'
    LOGGING_CONFIG: dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
    }
    JSON_LOGS: bool = False

    model_config = SettingsConfigDict(env_file='.env')

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        Assemble database connection URI from individual components.

        Returns:
            PostgreSQL database URI
        """
        # Build the connection string from components
        if self.POSTGRES_PASSWORD:
            postgres_dsn = f'{self.POSTGRES_PROTOCOL}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        else:
            postgres_dsn = f'{self.POSTGRES_PROTOCOL}://{self.POSTGRES_USER}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

        return PostgresDsn(postgres_dsn)


_settings = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


settings = get_settings()
