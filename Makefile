# authoringfw — Developer Makefile
# Usage: make <target>
# Requires: pip install -e ".[dev]" (run once after git clone / git pull)

.PHONY: install test test-v lint clean help

PYTHON := python3
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
