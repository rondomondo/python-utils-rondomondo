# python-utils-rondomondo - Makefile
.DEFAULT_GOAL := help
SHELL := /bin/bash

CYAN  := \033[36m
GREEN := \033[32m
RED   := \033[31m
RESET := \033[0m

VENV   := .venv
UV     := uv
PYTEST := $(VENV)/bin/pytest
RUFF   := $(VENV)/bin/ruff
MYPY   := $(VENV)/bin/mypy

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Create virtual environment (if absent)
	@if [ ! -d "$(VENV)" ]; then \
	  echo "  creating venv in $(VENV)..."; \
	  $(UV) venv $(VENV); \
	  echo "  done - activate with: source $(VENV)/bin/activate"; \
	else \
	  echo "  venv already exists"; \
	fi

.PHONY: check-venv
check-venv: venv ## Verify the virtual environment is active
	@if [ -z "$${VIRTUAL_ENV:-}" ]; then \
	  printf "$(RED)ERROR:$(RESET) venv not active. Run: source $(VENV)/bin/activate\n"; \
	  exit 1; \
	fi

.PHONY: install
install: venv ## Install package and dev dependencies
	$(UV) pip install -e ".[dev]"
	@echo "  installed. activate with: source $(VENV)/bin/activate"

.PHONY: lint
lint: check-venv ## Lint (ruff + mypy)
	$(RUFF) check --fix src/
	$(MYPY) src/

.PHONY: test
test: check-venv ## Run tests
	$(PYTEST) tests/ -v --tb=short

.PHONY: bump-patch bump-minor bump-major

bump-patch: ## Bump patch version in pyproject.toml (0.1.2 -> 0.1.3)
	@old=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	maj=$$(echo $$old | cut -d. -f1); \
	min=$$(echo $$old | cut -d. -f2); \
	pat=$$(echo $$old | cut -d. -f3); \
	new="$$maj.$$min.$$((pat + 1))"; \
	sed -i '' "s/^version = \"$$old\"/version = \"$$new\"/" pyproject.toml; \
	printf "  $(GREEN)$$old$(RESET) -> $(GREEN)$$new$(RESET)\n"

bump-minor: ## Bump minor version in pyproject.toml (0.1.2 -> 0.2.0)
	@old=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	maj=$$(echo $$old | cut -d. -f1); \
	min=$$(echo $$old | cut -d. -f2); \
	new="$$maj.$$((min + 1)).0"; \
	sed -i '' "s/^version = \"$$old\"/version = \"$$new\"/" pyproject.toml; \
	printf "  $(GREEN)$$old$(RESET) -> $(GREEN)$$new$(RESET)\n"

bump-major: ## Bump major version in pyproject.toml (0.1.2 -> 1.0.0)
	@old=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	maj=$$(echo $$old | cut -d. -f1); \
	new="$$((maj + 1)).0.0"; \
	sed -i '' "s/^version = \"$$old\"/version = \"$$new\"/" pyproject.toml; \
	printf "  $(GREEN)$$old$(RESET) -> $(GREEN)$$new$(RESET)\n"

.PHONY: build
build: check-venv ## Build wheel and sdist into dist/
	$(UV) build

.PHONY: publish-test
publish-test: build ## Upload to TestPyPI
	$(UV) publish --index testpypi dist/*.whl dist/*.tar.gz

.PHONY: publish
publish: build ## Upload to PyPI (live)
	@printf "$(RED)WARNING:$(RESET) publishing to live PyPI. Ctrl-C to abort, Enter to continue.\n" && read _
	$(UV) publish dist/*.whl dist/*.tar.gz

.PHONY: clean
clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache  -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache  -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist         -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build        -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ 2>/dev/null || true
