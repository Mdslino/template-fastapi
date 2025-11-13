# OAuth2 Authentication Setup Guide

This guide explains how to configure OAuth2 authentication with different providers in an agnostic way.

## Overview

The application uses a **provider-agnostic OAuth2 implementation** that works with any OAuth2-compliant provider:
- Supabase
- Firebase
- AWS Cognito
- Auth0
- Keycloak
- Or any other OAuth2 provider

## Architecture

The authentication system follows Clean Architecture:

```
domain/auth/          # Domain entities (AuthenticatedUser, Token)
application/auth/     # Authentication service and OAuth2 provider interface
infrastructure/auth/  # JWT provider implementation
```

## Configuration

### Environment Variables

Set these environment variables based on your OAuth2 provider:

```bash
# OAuth2 Configuration
OAUTH2_JWKS_URL=<your_provider_jwks_url>
OAUTH2_ISSUER=<your_provider_issuer>
OAUTH2_AUDIENCE=<your_provider_audience>  # Optional
```

### Provider-Specific Examples

#### Supabase

```bash
OAUTH2_JWKS_URL=https://<project-id>.supabase.co/auth/v1/.well-known/jwks.json
OAUTH2_ISSUER=https://<project-id>.supabase.co/auth/v1
OAUTH2_AUDIENCE=<your-project-url>  # Optional
```

#### Firebase

```bash
OAUTH2_JWKS_URL=https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com
OAUTH2_ISSUER=https://securetoken.google.com/<project-id>
OAUTH2_AUDIENCE=<project-id>
```

#### Auth0

```bash
OAUTH2_JWKS_URL=https://<domain>/.well-known/jwks.json
OAUTH2_ISSUER=https://<domain>/
OAUTH2_AUDIENCE=<your-api-identifier>
```

#### AWS Cognito

```bash
OAUTH2_JWKS_URL=https://cognito-idp.<region>.amazonaws.com/<pool-id>/.well-known/jwks.json
OAUTH2_ISSUER=https://cognito-idp.<region>.amazonaws.com/<pool-id>
OAUTH2_AUDIENCE=<app-client-id>
```

## Usage

### Protected Endpoints

Use the `CurrentUserDep` dependency to protect endpoints:

```python
from fastapi import APIRouter
from app.infrastructure.api.dependencies import CurrentUserDep

router = APIRouter()

@router.get("/protected")
def protected_route(user: CurrentUserDep):
    return {"user_id": str(user.user_id), "email": user.email}
```

### Role-Based Access Control

Use `require_roles` to check for specific roles:

```python
from fastapi import Depends
from app.infrastructure.api.dependencies import CurrentUserDep, require_roles

@router.get("/admin")
def admin_only(
    user: CurrentUserDep,
    _: None = Depends(require_roles(['admin', 'superuser']))
):
    return {"message": "Admin access granted"}
```

### Permission-Based Access Control

Use `require_permissions` to check for specific permissions:

```python
from fastapi import Depends
from app.infrastructure.api.dependencies import CurrentUserDep, require_permissions

@router.post("/data")
def create_data(
    user: CurrentUserDep,
    _: None = Depends(require_permissions(['write:data']))
):
    return {"message": "Data created"}
```

## Token Format

The JWT token should include the following claims:

```json
{
  "sub": "user-id",
  "email": "user@example.com",
  "email_verified": true,
  "exp": 1234567890,
  "iat": 1234567890,
  "provider": "supabase",
  "roles": ["admin", "user"],
  "permissions": ["read:data", "write:data"]
}
```

## API Request Example

```bash
# Get current user info
curl -X GET "http://localhost:8000/api/v1/protected/me" \
  -H "Authorization: Bearer <your-jwt-token>"

# Access admin endpoint (requires admin role)
curl -X GET "http://localhost:8000/api/v1/protected/admin" \
  -H "Authorization: Bearer <your-jwt-token>"

# Access permission-protected endpoint
curl -X GET "http://localhost:8000/api/v1/protected/write-data" \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Custom Provider Implementation

If you need provider-specific features (like token refresh or revoke), create a custom provider:

```python
# app/infrastructure/auth/my_provider.py
from app.application.auth.oauth2_provider import OAuth2Provider
from app.shared.functional.either import Either, Success, Failure

class MyCustomProvider(OAuth2Provider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def verify_token(self, token: str) -> Either[TokenPayload, Exception]:
        # Your custom implementation
        pass
    
    def refresh_token(self, refresh_token: str) -> Either[dict[str, str], Exception]:
        # Call your provider's API to refresh token
        pass
    
    # Implement other methods...
```

Then update the dependency in `dependencies.py`:

```python
def get_oauth2_provider() -> OAuth2Provider:
    from app.infrastructure.auth.my_provider import MyCustomProvider
    return MyCustomProvider(api_key=settings.MY_PROVIDER_API_KEY)
```

## Security Best Practices

1. **Always use HTTPS** in production
2. **Store tokens securely** on the client side (e.g., httpOnly cookies)
3. **Validate token expiration** (handled automatically by PyJWT)
4. **Use short-lived access tokens** (configured in your OAuth2 provider)
5. **Rotate refresh tokens** regularly
6. **Implement rate limiting** on authentication endpoints
7. **Log authentication attempts** for security monitoring

## Troubleshooting

### Token Verification Fails

- Check that `OAUTH2_JWKS_URL` is correct and accessible
- Verify that `OAUTH2_ISSUER` matches the token's `iss` claim
- Ensure the token hasn't expired
- Check that the token algorithm is in the allowed list (`RS256` by default)

### Missing Roles or Permissions

- Verify that your OAuth2 provider includes `roles` and `permissions` in the token
- Check the token payload using jwt.io
- Configure your provider to include custom claims

### Authentication Returns 401

- Verify the Authorization header format: `Bearer <token>`
- Check that the token is valid and not expired
- Ensure OAuth2 settings are properly configured

## Testing

For testing, you can create mock tokens:

```python
import jwt
from datetime import datetime, timedelta

def create_test_token(user_id: str, roles: list[str] = None):
    payload = {
        "sub": user_id,
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "roles": roles or ["user"],
        "permissions": ["read:data"]
    }
    # Use a test key for development
    return jwt.encode(payload, "test-secret", algorithm="HS256")
```

## Further Reading

- [OAuth 2.0 Specification](https://oauth.net/2/)
- [JWT.io](https://jwt.io/) - Decode and verify JWT tokens
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
