"""
Application settings and configuration management.

This module defines the application settings using Pydantic Settings,
including database configuration, API settings, logging configuration,
and OAuth2 authentication settings.
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
        OAUTH2_JWKS_URL: OAuth2 JWKS URL for token verification
        OAUTH2_ISSUER: OAuth2 token issuer
        OAUTH2_AUDIENCE: OAuth2 token audience (optional)
    """

    APP_NAME: str = 'FastAPI'
    APP_VERSION: str = '0.1.0'
    DEBUG: bool = False
    # SECURITY WARNING: Change this in production! Use environment variable.
    SECRET_KEY: str = 'change-me-in-production'
    POSTGRES_PROTOCOL: str = 'postgresql'
    POSTGRES_SERVER: str = 'localhost'
    POSTGRES_PORT: str = '5432'
    POSTGRES_USER: str = 'postgres'
    # SECURITY WARNING: Change this in production! Use environment variable.
    POSTGRES_PASSWORD: str = 'change-me-in-production'
    POSTGRES_DB: str = 'postgres'
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None
    API_V1_STR: str = '/api/v1'
    LOG_LEVEL: str = 'INFO'
    LOGGING_CONFIG: dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
    }
    JSON_LOGS: bool = False

    # OAuth2 Settings (provider-agnostic)
    # Configure these based on your OAuth2 provider:
    # - Supabase: https://<project>.supabase.co/auth/v1/.well-known/jwks.json
    # - Firebase: https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com
    # - Auth0: https://<domain>/.well-known/jwks.json
    # - Cognito: https://cognito-idp.<region>.amazonaws.com/<pool-id>/.well-known/jwks.json
    OAUTH2_JWKS_URL: str = ''
    OAUTH2_ISSUER: str = ''
    OAUTH2_AUDIENCE: str | None = None

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
