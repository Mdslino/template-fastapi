SHELL := /bin/bash
PYTHON_PATH := $(shell pwd)
export PYTHONPATH=$(PYTHON_PATH)

.PHONY: all clean install test black isort format-code sort-imports flake8 mypy black-check isort-check lint run run-dev run-db migrate migration migrate-down help run-docker

# Misc Section
help:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

all: clean install test

install:
	uv sync

setup-env:
	@if [ ! -f .env ]; then \
		cp .example.env .env; \
		echo "✓ Created .env file from .example.env"; \
		echo "⚠ Please update .env with your configuration"; \
	else \
		echo "✗ .env file already exists"; \
	fi

clean:
	@find . -name '*.pyc' -exec rm -rf {} +
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name 'Thumbs.db' -exec rm -rf {} +
	@find . -name '*~' -exec rm -rf {} +
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build
	rm -rf .pytest_cache
	rm -rf .mypy_cache

# Test Section
test:
	@docker compose run app pytest tests/ -vv

test-coverage:
	@docker compose run app pytest --cov-branch --cov-report term-missing --cov=app tests/ -vv

#Run Section
run:
	@./scripts/run.sh --workers 4 --host 0.0.0.0

run-dev:
	@./scripts/run.sh --reload --host 0.0.0.0

run-db:
	docker-compose up -d db

run-docker:
	docker-compose up -d

# Lint Section
mypy:
	@mypy app/

lint:
	@./scripts/lint.sh $(MODE)

# Migration Section

migrate:
	@./scripts/migrate.sh upgrade head

docker-migrate:
	@docker compose run app alembic upgrade head

migration:
	@./scripts/migrate.sh revision --autogenerate -m "$(m)"

migrate-down:
	@./scripts/migrate.sh downgrade -1