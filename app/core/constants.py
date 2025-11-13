"""
Core application constants and enums.

This module defines application-wide constants and enumerations.
"""

from enum import Enum


class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'
    TESTING = 'testing'


class UserRole(str, Enum):
    """User role types."""

    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'
