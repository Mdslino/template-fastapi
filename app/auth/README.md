# OAuth2/Auth0 Authentication Module

This module implements authentication and authorization using OAuth2 with Auth0, following SOLID principles and the project's modular architecture.

## Architecture

### Main Components

- **Services**: Business logic for token validation and permissions
  - `VerifyTokenService`: Validates Auth0 JWT tokens
  - `CheckPermissionsService`: Checks user permissions

- **Dependencies**: FastAPI dependency injection
  - `get_current_user`: Extracts and validates user from token
  - `RequirePermissions`: Class to check specific permissions

- **Schemas**: Pydantic models for authentication data
  - `TokenPayload`: JWT claims
  - `AuthenticatedUser`: Authenticated user with permissions

- **Exceptions**: Authentication domain-specific exceptions

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://your-api-identifier
AUTH0_ALGORITHM=RS256
```

### Getting Auth0 Credentials

1. Create an API in the Auth0 dashboard
2. Configure the identifier URL (audience)
3. Copy the tenant domain
4. Default algorithm is RS256

## Usage

### Protect an Endpoint (Basic Authentication)

```python
from fastapi import APIRouter
from app.auth.dependencies import CurrentUserDep

router = APIRouter()

@router.get('/protected')
def protected_endpoint(user: CurrentUserDep):
    return {'user_id': user.user_id, 'permissions': user.permissions}
```

### Require Specific Permissions

```python
from typing import Annotated
from fastapi import Depends
from app.auth.dependencies import RequirePermissions
from app.auth.schemas import AuthenticatedUser

# Create dependency with required permissions
require_admin = RequirePermissions(['admin:write'])

@router.post('/admin')
def admin_endpoint(
    user: Annotated[AuthenticatedUser, Depends(require_admin)]
):
    return {'message': 'Admin access granted'}
```

### Check Permissions Manually

```python
@router.get('/flexible')
def flexible_endpoint(user: CurrentUserDep):
    if user.has_permission('admin:write'):
        # Admin logic
        pass

    if user.has_any_permission(['read:data', 'write:data']):
        # Logic for users with any of the permissions
        pass

    if user.has_all_permissions(['read:data', 'write:data']):
        # Logic for users with all permissions
        pass
```

### Multiple Permissions

```python
# Requires ALL listed permissions
require_multiple = RequirePermissions(['read:data', 'write:data'])

@router.post('/data')
def data_endpoint(
    user: Annotated[AuthenticatedUser, Depends(require_multiple)]
):
    return {'message': 'Access granted'}
```

## Token Format

Clients must send the JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Example with curl

```bash
curl -H "Authorization: Bearer eyJhbGc..." https://api.example.com/api/v1/auth/me
```

### Example with httpx (Python)

```python
import httpx

response = httpx.get(
    'https://api.example.com/api/v1/auth/me',
    headers={'Authorization': f'Bearer {token}'}
)
```

## Example Endpoints

The module includes example endpoints in [app/auth/routes.py](./routes.py):

- `GET /api/v1/auth/me`: Returns authenticated user information
- `GET /api/v1/auth/admin`: Requires `admin:write` permission
- `GET /api/v1/auth/data/read`: Requires `read:data` permission
- `POST /api/v1/auth/data/write`: Requires `write:data` permission

## Error Handling

### HTTP 401 Unauthorized

Returned when:
- Token is not present
- Token is malformed
- Token is invalid or expired

```json
{
  "detail": "Token has expired"
}
```

### HTTP 403 Forbidden

Returned when the user doesn't have the required permissions:

```json
{
  "detail": "Insufficient permissions. Required: admin:write"
}
```

## Authentication Flow

1. Client obtains JWT token from Auth0
2. Client sends request with `Authorization: Bearer <token>` header
3. FastAPI calls `get_current_user` dependency
4. `VerifyTokenService` validates the token:
   - Fetches Auth0 public keys (JWKS)
   - Verifies token signature
   - Validates claims (issuer, audience, expiration)
5. Extracts user_id and permissions from token
6. If needed, `CheckPermissionsService` validates permissions
7. Endpoint receives `AuthenticatedUser` with user data

## Tests

### Run Tests

```bash
make test
```

### Unit Tests

- `tests/services/test_verify_token.py`: Tests token validation
- `tests/services/test_check_permissions.py`: Tests permission checking

### Integration Tests

- `tests/endpoints/test_auth.py`: Tests complete endpoints

## JWKS Cache

The service maintains a cache of Auth0 public keys (JWKS) for better performance. The cache is kept in memory during the application's lifetime.

## Security

- **Tokens are validated against Auth0 public keys**: Cannot be forged
- **Signature verification**: RSA256 by default
- **Claims validation**: Issuer, audience, and expiration are verified
- **No token storage**: Tokens are validated on each request
- **Structured logs**: All operations are logged with correlation ID

## SOLID Principles Applied

- **SRP**: Each service has a single responsibility
- **OCP**: Extensible via dependency injection
- **LSP**: Schemas follow consistent hierarchy
- **ISP**: Minimal and focused dependencies
- **DIP**: Depends on abstractions (FastAPI DI), not concrete implementations

## Adding New Features

### New Protected Endpoint

1. Create your router normally
2. Add `CurrentUserDep` as parameter
3. Optionally use `RequirePermissions` for specific permissions

```python
from app.auth.dependencies import CurrentUserDep, RequirePermissions

@router.post('/new-feature')
def new_feature(
    user: Annotated[AuthenticatedUser, Depends(RequirePermissions(['feature:write']))]
):
    # Your logic here
    pass
```

### New Authentication Service

If you need to add custom authentication logic:

1. Create new service in `app/auth/services/`
2. Inject via dependency in `app/auth/dependencies.py`
3. Write tests in `tests/services/`
