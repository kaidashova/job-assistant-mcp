.PHONY: up down logs install test lint

up:                ## build and start the server (http://localhost:8000/mcp)
	docker compose up -d --build

down:              ## stop the server (data is kept)
	docker compose down

logs:              ## follow the server logs
	docker compose logs -f

install:           ## create .venv and install with dev deps
	uv venv --python 3.12 .venv
	VIRTUAL_ENV=$$PWD/.venv uv pip install -e ".[dev]"

test:              ## run the test-suite
	.venv/bin/pytest

lint:              ## ruff lint + format check + mypy
	.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy
