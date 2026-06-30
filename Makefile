.DEFAULT_GOAL := help
.PHONY: help setup build test lint fmt deploy frontend-setup frontend-build

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

setup: ## Install Python + frontend dev dependencies
	uv sync --dev
	uv run pre-commit install
	cd frontend && npm install

build: ## Build all packages (frontend + python wheels)
	cd frontend && npm run build

test: ## Run the test suite
	uv run pytest

lint: ## Lint and format-check the codebase
	uv run ruff check .
	uv run ruff format --check .

fmt: ## Auto-format the codebase
	uv run ruff check --fix .
	uv run ruff format .

deploy: ## Deploy via Argo CD / Helm (wired up in feature 04-cicd)
	@echo "deploy target is implemented in feature 04-cicd"

frontend-setup: ## Install frontend dependencies only
	cd frontend && npm install

frontend-build: ## Build the frontend only
	cd frontend && npm run build
