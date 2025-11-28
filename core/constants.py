"""
Application-wide constants and enumerations.
"""

from enum import Enum


class Environment(str, Enum):
    """Application environment."""

    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'
