.PHONY: install install-dev uninstall dev test lint format check docs docs-serve clean help

PYTHON  ?= python3
VENV    := .venv
PIP     := $(VENV)/bin/pip
PYTEST  := $(VENV)/bin/pytest
BLACK   := $(VENV)/bin/black
PYLINT  := $(VENV)/bin/pylint
RUFF    := $(VENV)/bin/ruff
MKDOCS  := $(VENV)/bin/python -m mkdocs

# ----------------------------------------------------------------------
# Installation
# ----------------------------------------------------------------------

## Install dawos-cli system-wide (requires pipx)
install:
	@command -v pipx >/dev/null 2>&1 || { echo "Error: pipx is required. Install with: brew install pipx"; exit 1; }
	pipx install --force .
	@echo ""
	@echo "dawos-cli installed! Run: dawos --version"

## Uninstall dawos-cli from system
uninstall:
	@command -v pipx >/dev/null 2>&1 && pipx uninstall dawos-cli || pip uninstall -y dawos-cli
	@echo "dawos-cli uninstalled."

# ----------------------------------------------------------------------
# Development
# ----------------------------------------------------------------------

## Set up development environment (venv + editable install + dev deps)
dev: $(VENV)/bin/activate
	@echo ""
	@echo "Dev environment ready. Activate with: source .venv/bin/activate"

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@touch $(VENV)/bin/activate

## Install dev deps into existing venv
install-dev:
	$(PIP) install -e ".[dev]"

# ----------------------------------------------------------------------
# Quality
# ----------------------------------------------------------------------

## Run all tests
test:
	$(PYTEST) --cov=dawos_cli --cov-report=term-missing

## Run linters (black --check + pylint + ruff)
lint:
	$(BLACK) --check dawos_cli/ tests/
	$(PYLINT) dawos_cli/
	$(RUFF) check dawos_cli/ tests/
	@echo ""
	@echo "All lint checks passed."

## Format code with black
format:
	$(BLACK) dawos_cli/ tests/
	@echo ""
	@echo "Code formatted."

## Run all checks (format-check + lint + test) -- CI gate
check: lint test
	@echo ""
	@echo "All checks passed -- ready to commit."

# ----------------------------------------------------------------------
# Documentation
# ----------------------------------------------------------------------

## Build MkDocs documentation (strict mode)
docs:
	$(MKDOCS) build --strict
	@echo ""
	@echo "Docs built in site/ directory."

## Serve docs locally for preview
docs-serve:
	$(MKDOCS) serve

# ----------------------------------------------------------------------
# Cleanup
# ----------------------------------------------------------------------

## Remove build artifacts and caches
clean:
	rm -rf build/ dist/ *.egg-info .eggs/
	rm -rf .pytest_cache/ htmlcov/ .coverage
	rm -rf site/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."

# ----------------------------------------------------------------------
# Help
# ----------------------------------------------------------------------

## Show this help
help:
	@echo "dawos-cli Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install      Install system-wide via pipx"
	@echo "  make uninstall    Remove system-wide install"
	@echo "  make dev          Set up dev environment (.venv + deps)"
	@echo "  make test         Run tests with coverage"
	@echo "  make lint         Run black --check + pylint + ruff"
	@echo "  make format       Format code with black"
	@echo "  make check        Run all checks (lint + test)"
	@echo "  make docs         Build MkDocs documentation"
	@echo "  make docs-serve   Serve docs locally (http://localhost:8000)"
	@echo "  make clean        Remove build artifacts"
	@echo "  make help         Show this help"
