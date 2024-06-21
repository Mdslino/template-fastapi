SHELL := /bin/bash
PYTHON_PATH := $(shell pwd)
export PYTHONPATH=$(PYTHON_PATH)

.PHONY: all clean install test black isort format-code sort-imports flake8 mypy black-check isort-check lint run run-dev run-db migrate migration migrate-down help run-docker

# Misc Section
help:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

all: clean install test

install:
	poetry install

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
	@uvicorn app.main:app --workers 4 --host 0.0.0.0

run-dev:
	@uvicorn app.main:app --reload --host 0.0.0.0

run-db:
	docker-compose up -d migrations

run-docker:
	docker-compose up -d

# Lint Section
ruff:
	@ruff check . --fix

isort:
	@isort .

format-code: ruff isort

sort-imports:
	@isort .

flake8:
	@flake8 app/

mypy:
	@mypy app/

ruff-check:
	@ruff check .

isort-check:
	@isort --check-only app/

lint: ruff-check isort-check

# Migration Section

migrate:
	@alembic upgrade head

migration:
	@alembic revision --autogenerate -m "$(m)"

migrate-down:
	@alembic downgrade -1