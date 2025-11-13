"""
FastAPI dependency injection functions.

This module provides dependency injection functions for FastAPI routes,
including database session management and OAuth2 authentication.
"""

from typing import Annotated, Generator

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.auth.authentication_service import AuthenticationService
from app.application.auth.oauth2_provider import OAuth2Provider
from app.domain.auth.user import AuthenticatedUser
from app.infrastructure.config.settings import settings
from app.infrastructure.database.session import engine
from app.shared.functional.either import Failure, Success

logger = structlog.get_logger(__name__)
security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """
    Provide database session dependency.

    Yields a database session and ensures it's properly closed after use.

    Yields:
        Database session

    Example:
        >>> from fastapi import Depends
        >>> @app.get("/items/")
        >>> def read_items(db: Session = Depends(get_db)):
        ...     return db.query(Item).all()
    """
    with Session(engine) as session:
        yield session


# Type alias for database session dependency
SessionDep = Annotated[Session, Depends(get_db)]


# OAuth2 Provider Dependencies
def get_oauth2_provider() -> OAuth2Provider:
    """
    Provide OAuth2 provider dependency.

    This should be configured based on the OAuth2 provider you're using.
    Examples:
    - Supabase: Set OAUTH2_JWKS_URL, OAUTH2_ISSUER in settings
    - Firebase: Use Firebase Admin SDK
    - Cognito: Use AWS Cognito settings
    - Auth0: Use Auth0 settings

    Returns:
        OAuth2Provider implementation

    Raises:
        ValueError: If OAuth2 settings are not configured
    """
    from app.infrastructure.auth.jwt_provider import JWTOAuth2Provider

    if not settings.OAUTH2_JWKS_URL or not settings.OAUTH2_ISSUER:
        raise ValueError(
            'OAuth2 settings not configured. Please set OAUTH2_JWKS_URL '
            'and OAUTH2_ISSUER in your environment variables.'
        )

    return JWTOAuth2Provider(
        jwks_url=settings.OAUTH2_JWKS_URL,
        issuer=settings.OAUTH2_ISSUER,
        audience=settings.OAUTH2_AUDIENCE,
    )


OAuth2ProviderDep = Annotated[OAuth2Provider, Depends(get_oauth2_provider)]


def get_authentication_service(
    oauth2_provider: OAuth2ProviderDep,
) -> AuthenticationService:
    """
    Provide AuthenticationService dependency.

    Args:
        oauth2_provider: OAuth2 provider (injected)

    Returns:
        AuthenticationService instance
    """
    return AuthenticationService(oauth2_provider)


AuthenticationServiceDep = Annotated[
    AuthenticationService, Depends(get_authentication_service)
]


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_service: AuthenticationServiceDep = None,
) -> AuthenticatedUser:
    """
    Get the current authenticated user from the request.

    This dependency extracts the Bearer token from the Authorization header,
    verifies it with the OAuth2 provider, and returns the authenticated user.

    Args:
        credentials: HTTP authorization credentials (injected)
        auth_service: Authentication service (injected)

    Returns:
        Authenticated user

    Raises:
        HTTPException: If authentication fails

    Example:
        >>> @app.get("/protected")
        >>> def protected_route(user: CurrentUserDep):
        ...     return {"user_id": str(user.user_id), "email": user.email}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    token = credentials.credentials
    result = auth_service.authenticate(token)

    if isinstance(result, Success):
        return result.unwrap()
    elif isinstance(result, Failure):
        error = result.failure()
        logger.warning('Authentication failed', error=str(error))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


# Type alias for current user dependency
CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


def require_permissions(required_permissions: list[str]):
    """
    Dependency factory to require specific permissions.

    Args:
        required_permissions: List of required permissions

    Returns:
        Dependency function that validates permissions

    Example:
        >>> @app.get("/admin")
        >>> def admin_route(
        ...     user: CurrentUserDep,
        ...     _: None = Depends(require_permissions(['admin:read', 'admin:write']))
        ... ):
        ...     return {"message": "Admin access granted"}
    """

    def check_permissions(
        user: CurrentUserDep,
        auth_service: AuthenticationServiceDep,
    ) -> None:
        if not auth_service.check_permissions(user, required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Insufficient permissions',
            )

    return Depends(check_permissions)


def require_roles(required_roles: list[str]):
    """
    Dependency factory to require specific roles.

    Args:
        required_roles: List of required roles (user needs at least one)

    Returns:
        Dependency function that validates roles

    Example:
        >>> @app.get("/admin")
        >>> def admin_route(
        ...     user: CurrentUserDep,
        ...     _: None = Depends(require_roles(['admin', 'moderator']))
        ... ):
        ...     return {"message": "Admin access granted"}
    """

    def check_roles(
        user: CurrentUserDep,
        auth_service: AuthenticationServiceDep,
    ) -> None:
        if not auth_service.check_roles(user, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Insufficient roles',
            )

    return Depends(check_roles)
