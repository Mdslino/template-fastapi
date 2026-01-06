# Testing with Testcontainers

This project uses [Testcontainers](https://testcontainers.com/) to automatically manage PostgreSQL database containers during testing.

## How it works

Testcontainers automatically:
- Starts a PostgreSQL container before tests run
- Creates and configures the test database
- Runs migrations and seeds test data
- Tears down the container after tests complete

No manual database setup required!

## Prerequisites

- Docker must be installed and running on your machine
- Python dependencies installed (`make install` or `uv sync`)

## Running Tests

### Run all tests
```bash
make test
```

### Run with coverage
```bash
make test-coverage
```

### Run specific test file
```bash
pytest tests/endpoints/test_healthcheck.py -vv
```

### Run specific test
```bash
pytest tests/endpoints/test_healthcheck.py::test_healthcheck -vv
```

## Test Structure

Tests are organized following the app structure:

```
tests/
├── conftest.py              # Test fixtures and Testcontainers setup
├── endpoints/               # API endpoint integration tests
├── services/                # Business logic tests
├── models/                  # Database model tests
└── factories/               # Test data factories
```

## Key Fixtures

### `postgres_container` (session scope)
Starts a PostgreSQL container for the entire test session.

### `engine` (session scope)
SQLAlchemy engine connected to the test container.

### `Session` (session scope)
Session factory for creating database sessions.

### `db` (function scope)
Database session for individual tests. Auto-rollback after each test.

### `client` (function scope)
FastAPI TestClient for making HTTP requests to the API.

## Writing Tests

### Integration test example
```python
def test_create_product(client, db):
    """Test creating a product via API."""
    response = client.post(
        '/api/v1/products/',
        json={'name': 'Test Product', 'price': 99.99}
    )

    assert response.status_code == 201
    assert response.json()['name'] == 'Test Product'
```

### Service layer test example
```python
def test_create_product_service(db):
    """Test product creation business logic."""
    from app.products.services.create_product import CreateProductService
    from app.products.schemas import ProductCreate

    service = CreateProductService(db)
    data = ProductCreate(name='Test', price=50.0)

    product = service.execute(data)

    assert product.id is not None
    assert product.name == 'Test'
```

## Test Isolation

Each test runs with a clean database state:
- The `reset_db` fixture (autouse) clears all tables before each test
- Database schema is created once per session
- Containers are reused across tests for performance

## Debugging

### View container logs
Testcontainers outputs container logs to stdout during test failures.

### Keep container running after test failure
```python
@pytest.fixture(scope='session')
def postgres_container():
    with PostgresContainer('postgres:alpine').with_bind_ports(5432, 5433) as postgres:
        # Container will stay up until you manually stop it
        yield postgres
```

Then connect with: `psql -h localhost -p 5433 -U test -d test`

## Performance Tips

- Containers are session-scoped (start once per test session)
- Database schema is created once and tables are truncated between tests
- Use `reset_db` instead of recreating the entire database

## CI/CD

Testcontainers works seamlessly in CI environments (GitHub Actions, GitLab CI, etc.) as long as Docker is available. No special configuration needed!

Example GitHub Actions:
```yaml
- name: Run tests
  run: make test
  # Docker is available by default in GitHub Actions
```
