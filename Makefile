SHELL := /bin/bash
.PHONY: all clean install test black isort format-code sort-imports flake8 mypy black-check isort-check lint run run-dev

# Misc Section
help:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

all: clean install test

install:
	poetry install

clean:
	@find . -name '*.pyc' -exec rm -rf {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@find . -name 'Thumbs.db' -exec rm -rf {} \;
	@find . -name '*~' -exec rm -rf {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build

# Test Section
test:
	pytest tests/ -vv

test-coverage:
	pytest --cov-branch --cov-report term-missing --cov=app tests/ -vv

#Run Serction
run:
	@gunicorn "app.main:create_app()" -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 -w 4 --preload --access-logfile=- --error-logfile=- --log-level info

run-dev:
	@gunicorn "app.main:create_app()" -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --preload --reload --access-logfile=- --error-logfile=- --log-level debug

# Lint Section
black:
	@black .

isort:
	@isort .

format-code: black isort

sort-imports:
	@isort .

flake8:
	@flake8 app/

mypy:
	@mypy app/

black-check:
	@black --check app/

isort-check:
	@isort --check-only app/

lint: flake8 black-check isort-check

migrate:
	@PYTHONPATH=. alembic upgrade head

migration:
	@PYTHONPATH=. alembic revision --autogenerate -m "$(m)"

migrate-down:
	@PYTHONPATH=. alembic downgrade -1