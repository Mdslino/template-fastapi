# FastAPI Template - Django-Style Architecture

## Project Structure

This project follows a Django-inspired architecture with clear separation between application code, core setup, and shared utilities.

```
├── app/                          # Application code (Django "apps")
│   ├── auth/                     # Authentication app
│   │   ├── models.py            # Domain models (AuthenticatedUser, OAuth2Token)
│   │   ├── schemas.py           # API schemas (request/response models)
│   │   ├── services.py          # Business logic (AuthenticationService)
│   │   ├── dependencies.py      # FastAPI dependencies (DI)
│   │   ├── routes.py            # API endpoints
│   │   └── providers/           # OAuth2 provider implementations
│   │       ├── interface.py     # OAuth2Provider protocol
│   │       └── jwt_provider.py  # JWT-based implementation
│   ├── api/                      # API organization
│   │   └── v1/                  # API version 1
│   │       └── router.py        # Combines all v1 routes
│   ├── db/                       # Database setup
│   │   ├── base.py              # Base model classes
│   │   └── session.py           # Database session management
│   └── main.py                   # Application entry point
│
├── core/                         # Core application setup
│   ├── config.py                # Settings and configuration
│   ├── logging.py               # Logging setup
│   └── middleware.py            # Middleware configuration
│
├── shared/                       # Shared utilities
│   ├── exceptions.py            # Custom exceptions
│   ├── types.py                 # Common types and value objects
│   └── utils/                   # Utility functions
│       └── functional.py        # Either/Option monads, composition
│
├── tests/                        # Test suite
├── alembic/                      # Database migrations
└── pyproject.toml                # Project dependencies
```

## Architecture Principles

### 1. Django-Style Apps
Each feature is organized as a self-contained "app" (like Django apps):
- **auth/**: All authentication-related code in one place
- Future apps: users/, products/, orders/, etc.

### 2. Core vs App vs Shared
- **app/**: Business logic and features (what makes your app unique)
- **core/**: Application-wide setup (config, logging, middleware)
- **shared/**: Reusable utilities across features (can be extracted to a library)

### 3. Each App Contains
- **models.py**: Domain models (Pydantic)
- **schemas.py**: API request/response schemas
- **services.py**: Business logic
- **routes.py**: API endpoints
- **dependencies.py**: FastAPI dependency injection

## Key Features

### Provider-Agnostic OAuth2
Works with any OAuth2 provider (Supabase, Firebase, Auth0, Cognito):
```python
# Configure in .env
OAUTH2_JWKS_URL=https://your-provider/.well-known/jwks.json
OAUTH2_ISSUER=https://your-provider
```

### FastAPI Dependency Injection
```python
from app.auth.dependencies import CurrentUserDep

@router.get("/me")
def get_user(user: CurrentUserDep):
    return {"email": user.email}
```

### Functional Error Handling
```python
from shared.utils.functional import Either, Success, Failure

result = service.authenticate(token)
if isinstance(result, Success):
    user = result.unwrap()
else:
    error = result.failure()
```

## API Endpoints

```
GET  /api/v1/auth/me           - Get current user info
GET  /api/v1/auth/admin        - Admin only (requires 'admin' role)
GET  /api/v1/auth/write-data   - Permission protected
GET  /healthcheck              - Health check
```

## Adding a New App

To add a new feature (e.g., "products"):

1. Create the app directory:
```bash
mkdir -p app/products
```

2. Create the app files:
```
app/products/
├── __init__.py
├── models.py        # Product domain models
├── schemas.py       # Product API schemas
├── services.py      # Product business logic
├── routes.py        # Product API endpoints
└── dependencies.py  # Product-specific dependencies
```

3. Add routes to API:
```python
# app/api/v1/router.py
from app.products.routes import router as products_router

router.include_router(products_router, prefix='/products', tags=['products'])
```

## Development

### Install Dependencies
```bash
poetry install
```

### Run Development Server
```bash
poetry run uvicorn app.main:app --reload
```

### Run Tests
```bash
poetry run pytest
```

### Database Migrations
```bash
# Create migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```

## Configuration

Set environment variables in `.env`:
```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me-in-production
POSTGRES_DB=app

# OAuth2
OAUTH2_JWKS_URL=https://your-provider/.well-known/jwks.json
OAUTH2_ISSUER=https://your-provider
OAUTH2_AUDIENCE=your-audience  # Optional

# Application
SECRET_KEY=change-me-in-production
DEBUG=true
LOG_LEVEL=INFO
```

## Benefits of This Structure

✅ **Familiar**: Similar to Django's app-based organization
✅ **Simple**: Less complex than Clean Architecture
✅ **Modular**: Each app is self-contained
✅ **Scalable**: Easy to add new apps
✅ **Clear separation**: app/ (business), core/ (setup), shared/ (utilities)
✅ **Testable**: Easy to test individual apps
✅ **Reusable**: Shared utilities can be extracted

## Dependencies

- **FastAPI** 0.121.1: Web framework
- **uvicorn** 0.38.0: ASGI server
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **PyJWT**: JWT token handling
- **structlog**: Structured logging

## License

MIT
