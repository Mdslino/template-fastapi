# FastAPI Web Application Template

FastAPI template following a Django-like modular architecture, SOLID principles, and Object-Oriented Programming.

## 🏗️ Architecture

This project follows a **Django-like modular architecture** with clear separation of responsibilities:

- **`app/`**: Application modules (auth, api, db)
- **`core/`**: Application setup and configuration
- **`shared/`**: Shared utilities and base classes

## ✨ Features

- ✅ **Django-like Modular Structure**: Self-contained feature modules
- ✅ **SOLID Principles**: Maintainable and extensible code
- ✅ **Dependency Injection**: Extensive use of FastAPI DI
- ✅ **Pydantic**: Validation across all layers
- ✅ **Object-Oriented Design**: Clean OOP with abstract base classes and interfaces
- ✅ **Type Hints**: Complete typing throughout the codebase
- ✅ **Structured Logging**: Structured logs with structlog

##  Requirements

- Python >= 3.13
- PostgreSQL
- uv for dependency management

## How to Run

### 1. Environment Setup

**Important**: You must configure environment variables before running the application.

1. Copy `.example.env` to `.env`:
   ```bash
   make setup-env
   ```

2. Edit `.env` and set required variables:
   ```bash
   # Required: Set a strong secret key for cryptographic operations
   SECRET_KEY=your-strong-secret-key-here
   
   # Required: Set database password
   POSTGRES_PASSWORD=your-database-password
   ```

### 2. Install Dependencies

```bash
make install
```

### 3. Setup Pre-commit Hooks (Optional but Recommended)

Install git hooks to automatically check code quality before commits:

```bash
make setup-hooks
```

This will run linting and formatting checks automatically on every commit.

### 4. Run Application

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

##  API Documentation

After starting the application, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Development

### Adding New Features

1. Create a new module in `app/` (e.g., `app/products/`)
2. Add models, schemas, services, routes, and dependencies
3. Include the router in `app/api/v1/router.py`
4. Add tests for the new module

### SOLID Principles

- **S**ingle Responsibility: Each class has a single responsibility
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Interfaces can be replaced by implementations
- **I**nterface Segregation: Small, focused interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions

### Object-Oriented Design

The project uses clean OOP patterns with abstract base classes, dependency injection, and proper error handling through custom exceptions.

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

## 🚀 Release Management

This project uses [release-it](https://github.com/release-it/release-it) with [news-fragments](https://github.com/gbtech-oss/news-fragments) plugin for changelog generation.

### Creating changelog fragments

Before releasing, create fragment files in the `fragments/` folder to document changes using the interactive script:

```bash
make fragment
```

**Interactive workflow:**
1. The script will display a menu with 5 fragment types
2. Select a number (1-5) for the type:
   - `1` - **feature**: New features and functionality
   - `2` - **bugfix**: Bug fixes
   - `3` - **doc**: Documentation changes
   - `4` - **removal**: Deprecations and removals
   - `5` - **misc**: Miscellaneous changes (dependencies, refactoring, etc.)
3. Enter a brief description of your change
4. The script creates a timestamped file in `fragments/` folder

**Example:**
```bash
$ make fragment

Create a new changelog fragment

Select fragment type:
  1) feature       - New features and functionality
  2) bugfix        - Bug fixes
  3) doc           - Documentation changes
  4) removal       - Deprecations and removals
  5) misc          - Miscellaneous changes

Enter choice [1-5]: 1

Selected type: feature

Enter fragment message: Added user profile endpoint

✓ Created fragment: fragments/1736179200.feature
  Message: Added user profile endpoint
```

### Fragment types

- **`.feature`** - New features and functionality
- **`.bugfix`** - Bug fixes
- **`.doc`** - Documentation changes
- **`.removal`** - Deprecations and removals
- **`.misc`** - Miscellaneous changes (dependencies, refactoring, etc.)

### Creating a release

```bash
# Dry run (test without publishing)
make release-dry

# Create actual release
make release
```

The release process will:
1. Compile all fragments from `fragments/` folder into CHANGELOG.md
2. Remove the fragment files
3. Bump version in package.json
4. Create a git commit and tag
5. Push to GitHub and create a release

### Manual release workflow

```bash
# 1. Create fragments for your changes
make fragment
# Select type and enter message when prompted

# 2. Test the release
make release-dry

# 3. If everything looks good, create the release
make release
```

## Endpoints

- [x] `/healthcheck` - Returns application and database status

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