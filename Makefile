# authoringfw — Developer Makefile
# Usage: make <target>
# Requires: pip install -e ".[dev]" (run once after git clone / git pull)

.PHONY: install test test-v lint clean help

# venv-first (platform#2591 K3): make setup fuellt ./.venv, make test soll es auch nutzen
PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PIP    := pip

help:
	@echo "Available targets:"
	@echo "  install   — pip install -e '.[dev]' (editable + dev deps)"
	@echo "  test      — run pytest (quiet)"
	@echo "  test-v    — run pytest (verbose)"
	@echo "  lint      — run ruff check"
	@echo "  clean     — remove __pycache__ and .pytest_cache"

install:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ --tb=short -q

test-v:
	$(PYTHON) -m pytest tests/ --tb=short -v

lint:
	ruff check src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	@echo "Cleaned."

# Fleet-Standard-Einstieg (pkg-agents-v1, platform #2075 K2): make setup && make test
setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e ".[dev]" || .venv/bin/pip install -e .
	.venv/bin/pip install pytest
