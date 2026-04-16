# ---------------------------------------------------------------------------
# LicitScope – developer shortcuts
# ---------------------------------------------------------------------------

.DEFAULT_GOAL := help
SHELL := /bin/bash

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---- Environment ---------------------------------------------------------

install-api: ## Install API Python deps into a venv
	cd apps/api && python -m venv .venv && . .venv/Scripts/activate && pip install -e ".[dev]"

install-web: ## Install web deps
	cd apps/web && npm install

install: install-api install-web ## Install everything

# ---- Run -----------------------------------------------------------------

api: ## Run API locally (sqlite mode by default)
	cd apps/api && . .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000

web: ## Run Next.js dev server
	cd apps/web && npm run dev

seed: ## Load bundled demo fixtures into the configured database
	cd apps/api && . .venv/Scripts/activate && python -m app.scripts.seed

ingest: ## Run a one-shot ingestion cycle
	cd apps/api && . .venv/Scripts/activate && python -m app.scripts.run_ingestion

enrich: ## Run enrichment over pending notices
	cd apps/api && . .venv/Scripts/activate && python -m app.scripts.run_enrichment

# ---- Quality -------------------------------------------------------------

test: ## Run backend tests
	cd apps/api && . .venv/Scripts/activate && pytest -q

lint: ## Lint backend + frontend
	cd apps/api && . .venv/Scripts/activate && ruff check app tests
	cd apps/web && npm run lint

format: ## Format backend + frontend
	cd apps/api && . .venv/Scripts/activate && ruff format app tests
	cd apps/web && npm run format

typecheck: ## Typecheck frontend
	cd apps/web && npm run typecheck

# ---- Docker --------------------------------------------------------------

up: ## Start the full stack via docker compose
	docker compose -f infra/docker-compose.yml up --build

down: ## Stop the stack
	docker compose -f infra/docker-compose.yml down

logs: ## Tail all logs
	docker compose -f infra/docker-compose.yml logs -f

reset-db: ## Nuke + recreate the postgres volume (careful)
	docker compose -f infra/docker-compose.yml down -v

# ---- Release helpers -----------------------------------------------------

clean: ## Remove caches and build artefacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf apps/api/.pytest_cache apps/api/.ruff_cache
	rm -rf apps/web/.next apps/web/node_modules/.cache
