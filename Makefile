.PHONY: help dev stop build migrate upgrade seed test lint format typecheck shell logs

help:
	@echo "Caros — available commands"
	@echo ""
	@echo "  make dev          Start all services (docker compose up)"
	@echo "  make stop         Stop all services"
	@echo "  make build        Rebuild docker images"
	@echo "  make migrate      Generate a new Alembic migration"
	@echo "  make upgrade      Apply all pending migrations"
	@echo "  make test         Run test suite"
	@echo "  make lint         Run ruff linter"
	@echo "  make format       Run ruff formatter"
	@echo "  make typecheck    Run mypy"
	@echo "  make shell        Open Python shell in app container"
	@echo "  make logs         Tail app logs"

dev:
	docker compose up

stop:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec app alembic revision --autogenerate -m "$(msg)"

upgrade:
	docker compose exec app alembic upgrade head

downgrade:
	docker compose exec app alembic downgrade -1

test:
	docker compose exec app pytest -v --cov=app --cov-report=term-missing

lint:
	uv run ruff check app tests

format:
	uv run ruff format app tests

typecheck:
	uv run mypy app

shell:
	docker compose exec app python

logs:
	docker compose logs -f app

worker-logs:
	docker compose logs -f worker
