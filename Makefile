.PHONY: help install format lint type-check test test-cov checks clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies using poetry"
	@echo "  format       - Format code with black"
	@echo "  lint         - Lint code with ruff"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  test         - Run tests with pytest"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  checks       - Run format, lint, type-check, and test-cov"
	@echo "  clean        - Remove build artifacts and cache files"

# Install dependencies
install:
	poetry install

# Format code with black
format:
	@echo "==> Formatting code with black..."
	poetry run black json_mapper/

# Lint code with ruff
lint:
	@echo "==> Linting code with ruff..."
	poetry run ruff check json_mapper/

# Run type checking with mypy
type-check:
	@echo "==> Running type checks with mypy..."
	poetry run mypy json_mapper/

# Run tests without coverage
test:
	@echo "==> Running tests..."
	poetry run pytest

# Run tests with coverage
test-cov:
	@echo "==> Running tests with coverage..."
	poetry run pytest --cov=json_mapper --cov-report=term-missing --cov-report=html

# Run all checks (format, lint, type-check, and test with coverage)
checks: format lint type-check test-cov
	@echo "==> All checks passed! ✓"

# Clean build artifacts and cache
clean:
	@echo "==> Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
