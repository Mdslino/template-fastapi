# FastAPI Web Application Template

FastAPI template following a Django-like modular architecture, SOLID principles, and Object-Oriented Programming with **Provider-Agnostic OAuth2 Authentication**.

## 🏗️ Architecture

This project follows a **Django-like modular architecture** with clear separation of responsibilities:

- **`app/`**: Application modules (auth, api, db)
- **`core/`**: Application setup and configuration
- **`shared/`**: Shared utilities and base classes

## ✨ Features

- ✅ **Django-like Modular Structure**: Self-contained feature modules
- ✅ **SOLID Principles**: Maintainable and extensible code
- ✅ **OAuth2 Agnostic**: Works with any OAuth2 provider (Supabase, Firebase, Cognito, Auth0)
- ✅ **Dependency Injection**: Extensive use of FastAPI DI
- ✅ **Pydantic**: Validation across all layers
- ✅ **Object-Oriented Design**: Clean OOP with abstract base classes and interfaces
- ✅ **Type Hints**: Complete typing throughout the codebase
- ✅ **Structured Logging**: Structured logs with structlog
- ✅ **JWT Verification**: Secure JWT token verification
- ✅ **Role & Permission Based Access**: Access control by roles and permissions

## 🔐 OAuth2 Authentication

The template supports OAuth2 authentication in a **provider-agnostic** way:

### Supported Providers
- Supabase
- Firebase
- AWS Cognito  
- Auth0
- Keycloak
- Any OAuth2 provider that uses JWT

### Configuration

Set environment variables:

```bash
OAUTH2_JWKS_URL=https://your-provider.com/.well-known/jwks.json
OAUTH2_ISSUER=https://your-provider.com
OAUTH2_AUDIENCE=your-audience  # Optional
```

### Protected Endpoints

```python
from app.auth.dependencies import CurrentUserDep, require_roles

@router.get("/protected")
def protected_route(user: CurrentUserDep):
    return {"user": user.email}

@router.get("/admin")
def admin_route(
    user: CurrentUserDep,
    _: None = Depends(require_roles(['admin']))
):
    return {"message": "Admin only"}
```

## 📋 Requirements

- Python >= 3.13
- PostgreSQL
- uv for dependency management

## How to Run

### 1. Environment Setup

**Important**: You must configure environment variables before running the application.

1. Copy `.example.env` to `.env`:
   ```bash
   cp .example.env .env
   ```

2. Edit `.env` and set required variables:
   ```bash
   # Required: Set a strong secret key for JWT and cryptographic operations
   SECRET_KEY=your-strong-secret-key-here
   
   # Required: Set database password
   POSTGRES_PASSWORD=your-database-password
   
   # Required for OAuth2: Configure your OAuth2 provider
   OAUTH2_JWKS_URL=https://your-provider.com/.well-known/jwks.json
   OAUTH2_ISSUER=https://your-provider.com
   OAUTH2_AUDIENCE=your-audience  # Optional
   ```

### 2. Install Dependencies

```bash
make install
```

### 3. Run Application

Ensure the `.env` file is configured correctly, then start the database and application:

```bash
# Start database
make run-db

# Start application
make run
```

### Run with Docker

```bash
make docker-run
```

### Run Tests

```bash
make test
```

### Run Linter

```bash
make lint
```

### Run Formatter

```bash
make format-code
```

## 📁 Project Structure

```
├── app/                     # Application code (feature modules)
│   ├── auth/               # Authentication module
│   │   ├── models.py       # Domain models (AuthenticatedUser, Token)
│   │   ├── schemas.py      # API schemas
│   │   ├── services.py     # AuthenticationService
│   │   ├── routes.py       # API endpoints
│   │   ├── dependencies.py # FastAPI DI
│   │   └── providers/      # OAuth2 implementations
│   │       ├── interface.py   # OAuth2Provider abstract class
│   │       └── jwt_provider.py # JWT implementation
│   ├── api/v1/             # API versioning
│   ├── db/                 # Database setup
│   └── main.py             # Application entry point
│
├── core/                    # Application-wide setup
│   ├── config.py           # Settings
│   ├── logging.py          # Logging configuration
│   ├── middleware.py       # Middleware setup
│   ├── constants.py        # Application constants
│   └── dependencies.py     # Global dependencies
│
└── shared/                  # Reusable components
    ├── models.py           # Base model classes
    ├── schemas.py          # Base schema classes
    ├── exceptions.py       # Custom exceptions
    ├── types.py            # Common types
    └── utils/              # Utility functions
```

## 🚀 OAuth2 Usage Examples

### Get authenticated user information

```bash
curl -X GET "http://localhost:8000/api/v1/protected/me" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Role-protected endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/protected/admin" \
  -H "Authorization: Bearer <your-jwt-token-with-admin-role>"
```

### Permission-protected endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/protected/write-data" \
  -H "Authorization: Bearer <your-jwt-token-with-write-permission>"
```

## 📚 API Documentation

After starting the application, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Development

### Adding New Features

1. Create a new module in `app/` (e.g., `app/products/`)
2. Add models, schemas, services, routes, and dependencies
3. Include the router in `app/api/v1/router.py`
4. Add tests for the new module

### Configure Custom OAuth2 Provider

If you need provider-specific features (like token refresh):

```python
from app.auth.providers.interface import OAuth2Provider

class CustomOAuth2Provider(OAuth2Provider):
    def verify_token(self, token: str) -> TokenPayload:
        # Your implementation
        pass
    
    def get_user_info(self, token: str) -> AuthenticatedUser:
        # Your implementation
        pass
    
    # Implement other abstract methods...
```

### SOLID Principles

- **S**ingle Responsibility: Each class has a single responsibility
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Interfaces can be replaced by implementations
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions

### Object-Oriented Design

The project uses clean OOP patterns:

```python
# Abstract base class for OAuth2 providers
class OAuth2Provider(ABC):
    @abstractmethod
    def verify_token(self, token: str) -> TokenPayload:
        ...
    
    @abstractmethod
    def get_user_info(self, token: str) -> AuthenticatedUser:
        ...

# Concrete implementation
class JWTOAuth2Provider(OAuth2Provider):
    def verify_token(self, token: str) -> TokenPayload:
        # JWT verification logic
        ...
```

Error handling uses exceptions:

```python
try:
    user = auth_service.authenticate(token)
except AuthenticationException as e:
    # Handle authentication error
    pass
except TokenExpiredException as e:
    # Handle expired token
    pass
```

## 📝 Database Migrations

### Create a migration

```bash
make migration m="migration description"
```

### Apply migrations

```bash
make migrate
```

### Revert last migration

```bash
make migrate-down
```

## Endpoints

- [x] `/healthcheck` - Returns application and database status
- [x] `/api/v1/protected/me` - Authenticated user information
- [x] `/api/v1/protected/admin` - Admin role-protected endpoint
- [x] `/api/v1/protected/write-data` - Permission-protected endpoint

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT license.

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OAuth 2.0](https://oauth.net/2/)
- [JWT.io](https://jwt.io/)