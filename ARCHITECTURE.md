# Architecture Documentation

This document describes the architecture of this FastAPI application, which follows Clean Architecture principles, SOLID design principles, and incorporates Functional Programming concepts.

## Overview

The application is structured in layers, with dependencies pointing inward. This ensures that business logic is independent of frameworks, databases, and external systems.

```
┌─────────────────────────────────────────────────────┐
│                    Frameworks                        │
│              (FastAPI, SQLAlchemy)                   │
│                infrastructure/                       │
├─────────────────────────────────────────────────────┤
│               Interface Adapters                     │
│           (API Routes, Repositories)                 │
│      infrastructure/api/ + infrastructure/database/  │
├─────────────────────────────────────────────────────┤
│              Application Business Rules              │
│         (Use Cases, Ports, DTOs)                     │
│                application/                          │
├─────────────────────────────────────────────────────┤
│            Enterprise Business Rules                 │
│         (Entities, Value Objects)                    │
│                   domain/                            │
└─────────────────────────────────────────────────────┘
```

## Directory Structure

### `app/domain/` - Domain Layer (Enterprise Business Rules)

The innermost layer containing enterprise-wide business rules and entities.

- **`entities/`**: Domain entities with business logic
  - Pure Python/Pydantic models
  - No dependencies on external libraries (except Pydantic for validation)
  - Example: `User` entity with methods like `activate()`, `deactivate()`

- **`value_objects/`**: Immutable value objects
  - Example: `Email`, `Username`
  - Self-validating using Pydantic validators
  - Ensures data integrity at the domain level

- **`exceptions/`**: Domain-specific exceptions
  - Business rule violations
  - Example: `ValidationException`, `EntityNotFoundException`

### `app/application/` - Application Layer (Application Business Rules)

Contains application-specific business logic and orchestrates the flow between layers.

- **`use_cases/`**: Use case implementations
  - One use case class per action
  - Example: `CreateUserUseCase`, `GetUserUseCase`
  - Uses repositories through ports (interfaces)
  - Returns Either monads for functional error handling

- **`ports/`**: Interfaces (Dependency Inversion Principle)
  - Repository interfaces using Python Protocols
  - Allows domain/application to be independent of infrastructure

- **`dtos/`**: Data Transfer Objects
  - Pydantic models for transferring data between layers
  - Separate from domain entities to maintain boundaries

### `app/infrastructure/` - Infrastructure Layer (Frameworks & Drivers)

Contains implementation details and external framework concerns.

- **`database/`**:
  - `models.py`: SQLAlchemy ORM models
  - `session.py`: Database session management
  - `repositories/`: Concrete repository implementations
    - Example: `SQLAlchemyUserRepository`
    - Implements repository ports from application layer

- **`api/`**:
  - `routes/`: FastAPI route definitions
  - `schemas/`: Pydantic request/response schemas for API
  - `dependencies.py`: FastAPI dependency injection setup
    - Database session dependencies
    - Repository dependencies
    - Use case dependencies

- **`config/`**:
  - `settings.py`: Application configuration using Pydantic Settings

### `app/shared/` - Shared Utilities

Cross-cutting concerns and utilities used across layers.

- **`functional/`**: Functional programming utilities
  - `either.py`: Either/Result monad for error handling
  - `option.py`: Option/Maybe monad for optional values
  - `compose.py`: Function composition utilities

- **`logging.py`**: Structured logging configuration
- **`middleware.py`**: Custom middleware (logging, timing, etc.)

### `app/core/` - Core

Application-wide constants and enumerations.

- `constants.py`: Enums and constants

## Key Architectural Principles

### 1. Clean Architecture

**Dependency Rule**: Dependencies only point inward. Inner layers know nothing about outer layers.

- Domain layer has no dependencies
- Application layer depends only on domain
- Infrastructure depends on application and domain
- Each layer has clear boundaries and responsibilities

### 2. SOLID Principles

**Single Responsibility**: Each class has one reason to change
- `CreateUserUseCase`: Only handles user creation logic
- `SQLAlchemyUserRepository`: Only handles user data access

**Open/Closed**: Open for extension, closed for modification
- New use cases can be added without modifying existing ones
- Repository pattern allows switching implementations

**Liskov Substitution**: Interfaces can be substituted with implementations
- Any `UserRepository` implementation works with use cases

**Interface Segregation**: Small, focused interfaces
- `UserRepository` protocol defines only necessary methods
- Clients don't depend on methods they don't use

**Dependency Inversion**: Depend on abstractions, not concretions
- Use cases depend on `UserRepository` protocol, not SQLAlchemy
- FastAPI dependency injection provides concrete implementations

### 3. Dependency Injection

FastAPI's powerful dependency injection system is used extensively:

```python
# In dependencies.py
def get_user_repository(db: SessionDep) -> UserRepository:
    return SQLAlchemyUserRepository(db)

def get_create_user_use_case(
    user_repository: UserRepositoryDep
) -> CreateUserUseCase:
    return CreateUserUseCase(user_repository)

# In routes
@router.post("/users/")
def create_user(
    request: UserCreateRequest,
    use_case: CreateUserUseCaseDep,  # Injected!
) -> UserResponse:
    result = use_case.execute(...)
```

Benefits:
- Easy testing (mock dependencies)
- Loose coupling
- Clean, readable route handlers

### 4. Functional Programming

**Either/Result Monad**: For error handling without exceptions

```python
result = use_case.execute(dto)

if isinstance(result, Success):
    user = result.unwrap()
elif isinstance(result, Failure):
    error = result.failure()
```

**Option/Maybe Monad**: For handling optional values

```python
user_option = repository.find_by_id(user_id)
if user_option == Nothing:
    # User not found
else:
    user = user_option.value_or(None)
```

Benefits:
- Explicit error handling
- Type-safe
- Composable operations

### 5. Pydantic for Validation

All models use Pydantic for validation:
- Domain value objects (Email, Username)
- Domain entities (User)
- DTOs
- API schemas

Benefits:
- Runtime validation
- Type safety
- Automatic documentation
- JSON serialization

## Example Flow: Creating a User

1. **Request** arrives at FastAPI route in `infrastructure/api/routes/users.py`
2. **API Schema** (`UserCreateRequest`) validates request data
3. **Use Case** (`CreateUserUseCase`) is injected via FastAPI DI
4. **DTO** (`CreateUserDTO`) transfers data to use case
5. **Domain entities** (`User`, `Email`, `Username`) validate business rules
6. **Repository** (`SQLAlchemyUserRepository`) saves to database
7. **Result** (Either monad) is returned up the chain
8. **Response** is mapped to `UserResponse` schema and returned

```
HTTP Request
     ↓
FastAPI Route → UserCreateRequest (Pydantic)
     ↓
CreateUserUseCase (Injected via DI)
     ↓
CreateUserDTO
     ↓
Domain Entity (User, Email, Username)
     ↓
UserRepository (Protocol/Interface)
     ↓
SQLAlchemyUserRepository (Implementation)
     ↓
Database
     ↓
Either[User, Exception]
     ↓
UserResponse (Pydantic)
     ↓
HTTP Response (JSON)
```

## Testing Strategy

### Unit Tests
- **Domain entities**: Test business logic in isolation
- **Value objects**: Test validation rules
- **Use cases**: Test with mocked repositories

### Integration Tests
- **API endpoints**: Test complete request/response cycle
- **Repository**: Test with test database

### Benefits of This Architecture for Testing
- Easy to mock dependencies (repository interfaces)
- Business logic isolated from frameworks
- Clear boundaries make testing straightforward

## Adding New Features

### To add a new entity (e.g., Product):

1. **Domain Layer**:
   - Create `domain/entities/product.py`
   - Create value objects if needed
   - Create domain exceptions if needed

2. **Application Layer**:
   - Create `application/dtos/product.py`
   - Create `application/ports/repositories.py` (add ProductRepository)
   - Create use cases in `application/use_cases/product/`

3. **Infrastructure Layer**:
   - Create SQLAlchemy model in `infrastructure/database/repositories/product_repository.py`
   - Implement repository
   - Create API schemas in `infrastructure/api/schemas/product.py`
   - Create routes in `infrastructure/api/routes/products.py`
   - Add dependencies in `infrastructure/api/dependencies.py`

4. **Register** routes in `main.py`

## Benefits of This Architecture

1. **Maintainability**: Clear structure makes code easy to understand
2. **Testability**: Easy to test with mocked dependencies
3. **Flexibility**: Easy to swap implementations (database, cache, etc.)
4. **Scalability**: Clear boundaries allow independent scaling
5. **Type Safety**: Pydantic and type hints throughout
6. **Error Handling**: Functional approach with Either monads
7. **Developer Experience**: FastAPI DI makes code clean and readable

## Migration from Old Structure

The old structure has been refactored:

- `app/core/config.py` → `app/infrastructure/config/settings.py`
- `app/db/` → `app/infrastructure/database/`
- `app/core/deps.py` → `app/infrastructure/api/dependencies.py` (enhanced with DI)
- `app/custom_logging.py` → `app/shared/logging.py`

## Resources

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Functional Programming in Python with returns](https://returns.readthedocs.io/)
