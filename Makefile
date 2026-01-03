.PHONY: help install test format lint clean build publish dev-setup

help:  ## Show this help message
@echo "Available commands:"
@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in editable mode
pip install -e .

dev-setup:  ## Set up development environment
pip install -e ".[dev]"
pre-commit install

test:  ## Run tests
pytest

test-cov:  ## Run tests with coverage report
pytest --cov=sage_github --cov-report=html --cov-report=term

format:  ## Format code with ruff
ruff format .

lint:  ## Lint code with ruff
ruff check --fix .

check:  ## Run all quality checks (format + lint + type check)
ruff format --check .
ruff check .
mypy src/sage_github

pre-commit:  ## Run pre-commit hooks on all files
pre-commit run --all-files

clean:  ## Clean build artifacts and cache
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf .pytest_cache/
rm -rf .mypy_cache/
rm -rf .ruff_cache/
rm -rf htmlcov/
rm -rf .coverage
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build:  ## Build distribution packages
python -m build

publish-test:  ## Publish to TestPyPI
python -m twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
python -m twine upload dist/*

run:  ## Run the CLI (usage: make run ARGS="download")
github-manager $(ARGS)
