"""
Domain-specific exceptions.

This module defines exceptions that represent domain rule violations
and business logic errors.
"""


class DomainException(Exception):
    """Base exception for domain-related errors."""

    pass


class EntityNotFoundException(DomainException):
    """Exception raised when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f'{entity_type} with id {entity_id} not found')


class ValidationException(DomainException):
    """Exception raised when domain validation fails."""

    pass


class DuplicateEntityException(DomainException):
    """Exception raised when attempting to create a duplicate entity."""

    def __init__(self, entity_type: str, field: str, value: str):
        self.entity_type = entity_type
        self.field = field
        self.value = value
        super().__init__(f'{entity_type} with {field}={value} already exists')
