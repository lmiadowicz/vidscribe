.PHONY: help install install-dev test test-cov lint format clean build upload docs run

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PROJECT_NAME := vidscribe
SRC_DIR := src/$(PROJECT_NAME)
TEST_DIR := tests

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      Install the package in production mode"
	@echo "  make install-dev  Install the package in development mode with dev dependencies"
	@echo "  make test         Run unit tests"
	@echo "  make test-cov     Run tests with coverage report"
	@echo "  make lint         Run code linters (flake8, mypy)"
	@echo "  make format       Format code with black and isort"
	@echo "  make clean        Remove build artifacts and cache files"
	@echo "  make build        Build distribution packages"
	@echo "  make upload       Upload package to PyPI"
	@echo "  make docs         Generate documentation"
	@echo "  make run          Run the CLI tool"

# Installation targets
install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"
	pre-commit install

# Testing targets
test:
	pytest $(TEST_DIR) -v

test-cov:
	pytest $(TEST_DIR) --cov=$(PROJECT_NAME) --cov-report=term-missing --cov-report=html

test-unit:
	pytest $(TEST_DIR)/unit -v

test-integration:
	pytest $(TEST_DIR)/integration -v

# Code quality targets
lint:
	flake8 $(SRC_DIR) $(TEST_DIR)
	mypy $(SRC_DIR)

format:
	black $(SRC_DIR) $(TEST_DIR)
	isort $(SRC_DIR) $(TEST_DIR)

check-format:
	black --check $(SRC_DIR) $(TEST_DIR)
	isort --check-only $(SRC_DIR) $(TEST_DIR)

# Cleaning targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Build and distribution targets
build: clean
	$(PYTHON) -m build

upload: build
	$(PYTHON) -m twine upload dist/*

upload-test: build
	$(PYTHON) -m twine upload --repository testpypi dist/*

# Documentation targets
docs:
	cd docs && $(MAKE) html

docs-serve:
	cd docs && $(PYTHON) -m http.server --directory _build/html

# Development targets
run:
	$(PYTHON) -m $(PROJECT_NAME).cli

dev-server:
	$(PYTHON) -m $(PROJECT_NAME).cli --debug

# Docker targets (if using Docker)
docker-build:
	docker build -t $(PROJECT_NAME):latest .

docker-run:
	docker run -it --rm $(PROJECT_NAME):latest

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Version management
version:
	@echo "Current version: $$($(PYTHON) -c 'import $(PROJECT_NAME); print($(PROJECT_NAME).__version__)')"

bump-patch:
	bump2version patch

bump-minor:
	bump2version minor

bump-major:
	bump2version major