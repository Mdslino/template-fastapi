# FastAPI Template - AI Agent Instructions

## Architecture Overview

This is a **Django-like modular FastAPI template** emphasizing SOLID principles and clean OOP architecture:

- **`app/`**: Feature modules (API routes, database session management)
- **`core/`**: Application-wide setup (config, middleware, logging, dependencies)
- **`shared/`**: Reusable base classes and utilities (models, schemas, exceptions)
- **`alembic/`**: Database migrations (SQLAlchemy + Alembic)

### Key Architectural Patterns

**Base Classes**: All DB models inherit from `BaseDBModel` in [shared/models.py](shared/models.py), which provides `id`, `external_id` (UUID), `created_at`, `updated_at`. Pydantic schemas inherit from `BaseSchema` in [shared/schemas.py](shared/schemas.py).

**Dependency Injection**: Use type-annotated dependencies extensively. Database sessions use `SessionDep = Annotated[Session, Depends(get_db)]`. Settings use `SettingsDep`. See [app/db/session.py](app/db/session.py) and [core/dependencies.py](core/dependencies.py).

**Structured Logging**: All logging uses `structlog` with correlation IDs via `asgi-correlation-id` middleware. Request context is automatically bound. See [core/logging.py](core/logging.py) and [core/middleware.py](core/middleware.py).

**API Versioning**: Routes are organized under `/api/v1` prefix. Add new routes to [app/api/v1/router.py](app/api/v1/router.py).

## Development Workflows

### Essential Commands (via Makefile)

- **`make install`**: Install dependencies with `uv sync` (requires uv package manager)
- **`make setup-env`**: Copy `.example.env` to `.env` (do this first!)
- **`make run-db`**: Start PostgreSQL in Docker
- **`make run-dev`**: Run with hot reload (`--reload` flag)
- **`make test`**: Run pytest in Docker container
- **`make lint`**: Check with ruff (import sorting + formatting)
- **`make lint MODE=fix`**: Auto-fix linting issues
- **`make migrate`**: Apply pending migrations (`alembic upgrade head`)
- **`make migration m="description"`**: Create new migration

### Database Migrations

1. Import new models in [alembic/env.py](alembic/env.py) to register with `Base.metadata`
2. Create migration: `make migration m="add_users_table"`
3. Review generated file in `alembic/versions/`
4. Apply: `make migrate` or `make docker-migrate` for Docker

**Important**: Migrations autogenerate by comparing `Base.metadata` to DB state. Always import models in alembic/env.py.

### Testing & TDD

**Follow Test-Driven Development (TDD)**: Write tests before implementation. Red → Green → Refactor cycle.

**Prefer integration tests with minimal mocking**. Test real components working together using actual database connections and dependencies. Use mocks only when external services are involved (APIs, email, etc.).

Tests use pytest with Docker Compose. Test fixtures in [tests/conftest.py](tests/conftest.py) automatically create/drop test database. Database factories in `tests/factories/session.py`. Environment variables are set in conftest for test isolation.

**TDD Workflow**:
1. **Write failing test first** for the new feature/use case
2. **Run test** to confirm it fails (`make test`)
3. **Implement minimum code** to make test pass
4. **Run test** to confirm it passes
5. **Refactor** while keeping tests green

**Test Organization** (mirror app structure):

```
tests/
├── conftest.py
├── endpoints/             # API endpoint tests
│   └── test_products.py
├── services/              # Service layer tests (business logic)
│   └── test_create_product.py
├── models/                # Model tests
│   └── test_product.py
└── factories/             # Test data factories
    └── session.py
```

**Service Test Example** (integration test with real database):

```python
# tests/services/test_create_product.py
import pytest
from app.products.services.create_product import CreateProductService
from app.products.schemas import ProductCreate

def test_create_product_success(db):
    # Arrange: Use real database session, no mocks
    service = CreateProductService(db)
    data = ProductCreate(name='Test Product', price=99.99)

    # Act
    product = service.execute(data)

    # Assert
    assert product.id is not None
    assert product.name == 'Test Product'
    assert product.price == 99.99
    # Verify it's actually in the database
    db.refresh(product)
    assert product.created_at is not None

def test_create_product_duplicate_name_raises_exception(db):
    # Arrange: Real database with existing data
    service = CreateProductService(db)
    data = ProductCreate(name='Duplicate', price=50.0)
    service.execute(data)

    # Act & Assert
    with pytest.raises(DuplicateEntityException):
        service.execute(data)
```

**Endpoint Test Example** (full integration):

```python
# tests/endpoints/test_products.py
def test_get_product_returns_200(client, db):
    # Arrange: Create test data in real database
    product = Product(name='Test', price=10.0)
    db.add(product)
    db.commit()

    # Act: Make real HTTP request
    response = client.get(f'/api/v1/products/{product.id}')

    # Assert
    assert response.status_code == 200
    assert response.json()['name'] == 'Test'

def test_create_product_endpoint(client):
    # Act: Full stack integration test
    response = client.post(
        '/api/v1/products/',
        json={'name': 'New Product', 'price': 29.99}
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == 'New Product'
    assert data['id'] is not None
```

**When to use mocks** (only for external dependencies):

```python
# Use pytest-vcr to record/replay external HTTP calls
import pytest

@pytest.mark.vcr()
def test_service_with_external_api(db):
    # First run records the HTTP interaction to cassettes/
    # Subsequent runs replay the recorded response
    service = MyService(db)
    result = service.execute(data)

    assert result.status == 'success'
    # Uses real database, but recorded external API responses

# Configure VCR in tests/conftest.py to filter sensitive data
@pytest.fixture(scope='module')
def vcr_config():
    return {
        'filter_headers': ['authorization', 'apikey'],
        'filter_query_parameters': ['apikey'],
    }
```

**Run tests**: `make test` (runs in Docker with isolated database)

## Code Conventions

### Style & Formatting

- **Line length**: 79 characters (enforced by ruff)
- **Quotes**: Single quotes for strings (`'example'`)
- **Import sorting**: Handled by ruff with `--select I`
- **Type hints**: Required throughout (Python 3.14+ syntax)
- **Target**: Python 3.14+

### Database Models

```python
from shared.models import BaseDBModel

class User(BaseDBModel):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    # id, external_id, created_at, updated_at inherited from BaseDBModel
```

### API Schemas

```python
from shared.schemas import BaseSchema, BaseResponse

class UserCreate(BaseSchema):
    email: str
    name: str

class UserResponse(BaseResponse):
    email: str
    name: str
    # id, created_at, updated_at inherited from BaseResponse
```

### Custom Exceptions

Domain exceptions in [shared/exceptions.py](shared/exceptions.py) follow patterns like `EntityNotFoundException`, `DuplicateEntityException`, `ValidationException`. Always inherit from `DomainException`.

## Feature Module Organization

When creating new features in `app/`, follow this modular structure pattern:

```
app/
└── products/              # Feature module
    ├── __init__.py
    ├── models.py          # SQLAlchemy models (inherit from BaseDBModel)
    ├── schemas.py         # Pydantic schemas (inherit from BaseSchema)
    ├── services/          # Business logic by intention/use case
    │   ├── create_product.py
    │   ├── get_product.py
    │   └── update_product.py
    ├── repository.py      # Data access layer (optional, for complex queries)
    ├── routes.py          # FastAPI route handlers
    └── dependencies.py    # Module-specific dependencies
```

### Service Layer Pattern

**Services represent business intentions/use cases**, not domain entities. Each service class encapsulates a single business operation:

```python
# app/products/services/create_product.py
from sqlalchemy.orm import Session
from app.products.models import Product
from app.products.schemas import ProductCreate

class CreateProductService:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

# app/products/services/get_product.py
from shared.exceptions import EntityNotFoundException

class GetProductService:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, product_id: int) -> Product:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise EntityNotFoundException('Product', str(product_id))
        return product
```

**Service dependencies** injected via FastAPI DI:

```python
# app/products/dependencies.py
from typing import Annotated
from fastapi import Depends
from app.db.session import SessionDep

def get_create_product_service(db: SessionDep) -> CreateProductService:
    return CreateProductService(db)

def get_get_product_service(db: SessionDep) -> GetProductService:
    return GetProductService(db)

CreateProductServiceDep = Annotated[CreateProductService, Depends(get_create_product_service)]
GetProductServiceDep = Annotated[GetProductService, Depends(get_get_product_service)]
```

**Routes use intention-based services**:

```python
# app/products/routes.py
from fastapi import APIRouter
from app.products.dependencies import CreateProductServiceDep, GetProductServiceDep

router = APIRouter(prefix='/products', tags=['products'])

@router.get('/{product_id}')
def get_product(product_id: int, service: GetProductServiceDep) -> ProductResponse:
    product = service.execute(product_id)
    return ProductResponse.model_validate(product)

@router.post('/')
def create_product(data: ProductCreate, service: CreateProductServiceDep) -> ProductResponse:
    product = service.execute(data)
    return ProductResponse.model_validate(product)
```

### Repository Pattern (Optional)

For complex queries or data access patterns, use **repository classes**:

```python
# app/products/repository.py
from sqlalchemy.orm import Session
from sqlalchemy import select

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_category(self, category: str) -> list[Product]:
        stmt = select(Product).where(Product.category == category)
        return list(self.db.scalars(stmt))

    def find_active_products(self) -> list[Product]:
        stmt = select(Product).where(Product.is_active == True)
        return list(self.db.scalars(stmt))
```

Services can then use repositories for data access while maintaining separation of concerns.

### Module Registration

Register new feature modules in [app/api/v1/router.py](app/api/v1/router.py):

```python
from app.products.routes import router as products_router

router = APIRouter(prefix='/api/v1')
router.include_router(products_router)
```

## SOLID Principles

This template enforces SOLID principles throughout. Apply them when adding new features:

### Single Responsibility Principle (SRP)
**Each class/module has one reason to change**. Service classes handle ONE business operation:

```python
# ✅ Good: One service per use case
class CreateProductService:
    def execute(self, data: ProductCreate) -> Product: ...

class UpdateProductService:
    def execute(self, product_id: int, data: ProductUpdate) -> Product: ...

# ❌ Bad: Multiple responsibilities in one class
class ProductService:
    def create(self, data): ...
    def update(self, id, data): ...
    def delete(self, id): ...
    def send_notification(self, product): ...  # Different responsibility!
```

### Open/Closed Principle (OCP)
**Open for extension, closed for modification**. Use dependency injection and Protocol:

```python
# Protocol defines interface (structural typing)
from typing import Protocol

class ProductRepositoryProtocol(Protocol):
    def find_by_id(self, product_id: int) -> Product | None: ...

# Service depends on protocol, not concrete implementation
class GetProductService:
    def __init__(self, repository: ProductRepositoryProtocol):
        self.repository = repository

    def execute(self, product_id: int) -> Product:
        product = self.repository.find_by_id(product_id)
        if not product:
            raise EntityNotFoundException('Product', str(product_id))
        return product
```

### Liskov Substitution Principle (LSP)
**Subtypes must be substitutable for their base types**. All implementations honor the contract:

```python
# Base schema defines contract
class BaseResponse(BaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# All responses honor the contract
class ProductResponse(BaseResponse):
    name: str
    price: float
    # Still has id, created_at, updated_at
```

### Interface Segregation Principle (ISP)
**Clients shouldn't depend on interfaces they don't use**. Keep dependencies minimal:

```python
# ✅ Good: Focused dependencies
class CreateProductService:
    def __init__(self, db: Session):  # Only needs DB session
        self.db = db

# ❌ Bad: Too many dependencies
class CreateProductService:
    def __init__(self, db: Session, email: EmailService, cache: Cache, logger: Logger):
        # Only uses db, others unused
```

### Dependency Inversion Principle (DIP)
**Depend on abstractions, not concretions**. Use FastAPI DI and type annotations:

```python
# ✅ Good: Inject dependencies via FastAPI
@router.post('/')
def create_product(
    data: ProductCreate,
    service: CreateProductServiceDep  # Injected, testable
) -> ProductResponse:
    return service.execute(data)

# ❌ Bad: Direct instantiation
@router.post('/')
def create_product(data: ProductCreate, db: Session) -> ProductResponse:
    service = CreateProductService(db)  # Hard to test, tight coupling
    return service.execute(data)
```

**Key practices**:
- One service class per use case (SRP)
- Services depend on `SessionDep`, not concrete `Session` (DIP)
- Use Protocol for shared contracts (OCP, LSP)
- Keep dependencies minimal and focused (ISP)
- Always use dependency injection via FastAPI (DIP)

## Configuration

Settings use Pydantic Settings with `.env` file. See [core/config.py](core/config.py). Access via singleton: `from core.config import settings`.

**Required env vars**: `SECRET_KEY`, `POSTGRES_PASSWORD`. Database URI is auto-constructed from individual components (`POSTGRES_SERVER`, `POSTGRES_PORT`, etc.).

## Release Management

This project uses **news fragments** for changelog generation:

1. Create fragment: `echo "Added feature X" > fragments/feature-name.feature`
2. Types: `.feature`, `.bugfix`, `.doc`, `.removal`, `.misc`
3. Run `make release` to compile fragments into [CHANGELOG.md](CHANGELOG.md)

See [fragments/README.md](fragments/README.md) for details.

## Common Patterns

**Router registration**: Include routers in [app/api/v1/router.py](app/api/v1/router.py) with `router.include_router()`.

**Health checks**: Use `/healthcheck` endpoint pattern with DB connectivity test (see [app/main.py](app/main.py#L26-L45)).

**Middleware order**: Logging middleware runs first, then `CorrelationIdMiddleware`. Registered in [app/main.py](app/main.py#L79-L80).

**Session management**: Always use `SessionDep` for route dependencies, never create sessions manually. Sessions are auto-closed via finally block in [app/db/session.py](app/db/session.py#L33-L38).
