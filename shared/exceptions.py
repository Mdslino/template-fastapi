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


class AuthenticationException(DomainException):
    """Exception raised when authentication fails."""

    pass


class TokenExpiredException(AuthenticationException):
    """Exception raised when a token has expired."""

    pass


class InvalidTokenException(AuthenticationException):
    """Exception raised when a token is invalid."""

    pass


class InsufficientPermissionsException(DomainException):
    """Exception raised when user lacks required permissions."""

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions
        super().__init__(
            f'Insufficient permissions. Required: {required_permissions}'
        )


class InsufficientRolesException(DomainException):
    """Exception raised when user lacks required roles."""

    def __init__(self, required_roles: list[str]):
        self.required_roles = required_roles
        super().__init__(f'Insufficient roles. Required: {required_roles}')


class NotImplementedProviderException(DomainException):
    """Exception raised when a provider method is not implemented."""

    def __init__(self, method_name: str, provider_name: str = 'OAuth2Provider'):
        self.method_name = method_name
        self.provider_name = provider_name
        super().__init__(
            f'{method_name} must be implemented per provider. '
            f"Please use the provider's SDK or API."
        )
