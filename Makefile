# Makefile for ESG Reporting Project

.PHONY: help install test lint format clean build deploy dev-setup

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies and package in development mode"
	@echo "  test        - Run the test suite"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black and isort"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build the package"
	@echo "  deploy      - Deploy to Azure using azd"
	@echo "  dev-setup   - Set up development environment"

# Install dependencies and package
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

# Run tests
test:
	pytest tests/ -v --cov=src/esg_reporting --cov-report=html --cov-report=term

# Run linting
lint:
	flake8 src/ tests/
	bandit -r src/
	safety check

# Format code
format:
	black src/ tests/
	isort src/ tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	python setup.py sdist bdist_wheel

# Deploy to Azure
deploy:
	azd deploy

# Set up development environment
dev-setup:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Linux/Mac: source venv/bin/activate"
	@echo "Then run: make install"

# Initialize Azure resources
azure-init:
	azd init
	azd up

# Run the application locally
run:
	esg-reporting --help

# Development dependencies
dev-deps:
	pip install black isort flake8 bandit safety pytest-cov
