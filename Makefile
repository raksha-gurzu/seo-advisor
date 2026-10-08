# Short names for the mise tasks. The task logic lives in mise.toml only.
# Run `make` to see the list.

.DEFAULT_GOAL := help
.PHONY: help setup dev check lint typecheck test audit db-up db-down migrate seed gen-client discover

help: ## Show the targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-11s %s\n", $$1, $$2}'

setup: ## Install tools and deps, make .env, start the database, save the sites
	mise run setup

dev: ## Start the database, the API (:8000) and the web app (:5173)
	mise run dev

check: ## Lint, types and tests (Python and web)
	mise run check

lint: ## Lint and format checks
	mise run lint

typecheck: ## mypy --strict and tsc
	mise run typecheck

test: ## Python tests
	mise run test

audit: ## Known vulnerabilities in Python and web packages
	mise run audit

db-up: ## Start PostgreSQL
	mise run db:up

db-down: ## Stop PostgreSQL (the data stays)
	mise run db:down

migrate: ## Apply database migrations
	mise run db:migrate

seed: ## Save the sites in infra/sites/*.toml
	mise run db:seed

gen-client: ## Export OpenAPI and make the TypeScript client again
	mise run gen-client

discover: ## Print MyPipit's pages (live, read-only)
	mise run inventory:discover -- infra/sites/mypipit.toml
