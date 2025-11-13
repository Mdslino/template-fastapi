# FastAPI Web Application Template

FastAPI template following Clean Architecture, SOLID principles, and Functional Programming with **Provider-Agnostic OAuth2 Authentication**.

## 🏗️ Architecture

This project follows **Clean Architecture** with clear separation of responsibilities:

- **`domain/`**: Business entities and rules (AuthenticatedUser, Token)
- **`application/`**: Use cases and application logic (AuthenticationService, OAuth2Provider interface)
- **`infrastructure/`**: Frameworks, database, and APIs (JWT provider, routes, dependencies)
- **`shared/`**: Shared utilities (logging, functional, middleware)

For more details, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## ✨ Features

- ✅ **Clean Architecture**: Clear layer separation and responsibilities
- ✅ **SOLID Principles**: Maintainable and extensible code
- ✅ **OAuth2 Agnostic**: Works with any OAuth2 provider (Supabase, Firebase, Cognito, Auth0)
- ✅ **Dependency Injection**: Extensive use of FastAPI DI
- ✅ **Pydantic**: Validation across all layers
- ✅ **Functional Programming**: Either/Result monads for error handling
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

See [OAUTH2_SETUP.md](./OAUTH2_SETUP.md) for detailed configuration for each provider.

### Protected Endpoints

```python
from app.infrastructure.api.dependencies import CurrentUserDep, require_roles

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
- Poetry or uv for dependency management

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
app/
├── domain/                          # Enterprise Business Rules
│   ├── auth/                        # Authentication (AuthenticatedUser, Token)
│   ├── entities/                    # Domain entities
│   ├── value_objects/               # Immutable value objects
│   └── exceptions/                  # Domain-specific exceptions
├── application/                     # Application Business Rules
│   ├── auth/                        # AuthenticationService, OAuth2Provider interface
│   ├── use_cases/                   # Use case implementations
│   ├── ports/                       # Interfaces/Protocols (DIP)
│   └── dtos/                        # Data Transfer Objects
├── infrastructure/                  # Frameworks & Drivers
│   ├── auth/                        # JWT provider implementation
│   ├── database/
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── session.py               # Session management
│   │   └── repositories/            # Repository implementations
│   ├── api/                         # Interface Adapters
│   │   ├── dependencies.py          # FastAPI dependency injection
│   │   ├── routes/                  # API routes
│   │   └── schemas/                 # Pydantic schemas for API
│   └── config/
│       └── settings.py              # Settings (includes OAuth2)
├── shared/                          # Shared Utilities
│   ├── logging.py                   # Logging utilities
│   ├── middleware.py                # Custom middleware
│   └── functional/                  # Functional programming utilities
│       ├── either.py                # Result/Either monad
│       └── option.py                # Option/Maybe monad
└── core/                            # Constants and enums
    └── constants.py
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

1. **Domain**: Create entities and value objects in `domain/`
2. **Application**: Create DTOs, ports, and use cases in `application/`
3. **Infrastructure**: Implement repositories and routes in `infrastructure/`
4. **Tests**: Add tests for each layer

See [ARCHITECTURE.md](./ARCHITECTURE.md) for complete details.

### Configure Custom OAuth2 Provider

If you need provider-specific features (like token refresh), see [OAUTH2_SETUP.md](./OAUTH2_SETUP.md#custom-provider-implementation).

### SOLID Principles

- **S**ingle Responsibility: Each class has a single responsibility
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Interfaces can be replaced by implementations
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions

### Functional Programming

The project uses monads for error handling:

```python
# Either monad for operations that can fail
result = auth_service.authenticate(token)
if isinstance(result, Success):
    user = result.unwrap()
elif isinstance(result, Failure):
    error = result.failure()
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
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [returns Library](https://returns.readthedocs.io/)
- [OAuth 2.0](https://oauth.net/2/)
- [JWT.io](https://jwt.io/)