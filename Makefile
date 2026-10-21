.PHONY: up down ingest transform test lint
up: 
	docker compose up -d
down:
	docker compose down
ingest:
	uv run python -m airq ingest
transform:
	cd dbt && uv run dbt build
test:
	uv run pytest -q
lint:
	uv run ruff check . && uv run ruff format --check .