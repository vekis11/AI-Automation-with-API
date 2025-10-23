# API Anomaly Detection System - Makefile
# Provides convenient commands for development and deployment

.PHONY: help install test lint format clean build run deploy

# Default target
help:
	@echo "API Anomaly Detection System - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies"
	@echo "  test        Run all tests"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and isort"
	@echo "  clean       Clean up temporary files"
	@echo ""
	@echo "Service:"
	@echo "  run         Start the service"
	@echo "  stop        Stop the service"
	@echo "  logs        View service logs"
	@echo ""
	@echo "Docker:"
	@echo "  build       Build Docker image"
	@echo "  up          Start with Docker Compose"
	@echo "  down        Stop Docker Compose"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy      Deploy to production"
	@echo "  deploy-staging Deploy to staging"

# Development commands
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt 2>/dev/null || true

test:
	@echo "🧪 Running tests..."
	python scripts/run_tests.py

test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest test_main.py -v --cov=main --cov-report=term-missing

test-integration:
	@echo "🔗 Running integration tests..."
	python scripts/test_pipeline.py --url http://localhost:8000

lint:
	@echo "🔍 Running linting checks..."
	python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	python -m black --check --diff .
	python -m isort --check-only --diff .

format:
	@echo "🎨 Formatting code..."
	python -m black .
	python -m isort .

clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Service commands
run:
	@echo "🚀 Starting service..."
	python scripts/start_service.py

run-docker:
	@echo "🐳 Starting service with Docker..."
	docker-compose up -d

stop:
	@echo "🛑 Stopping service..."
	docker-compose down

logs:
	@echo "📋 Viewing service logs..."
	docker-compose logs -f

# Docker commands
build:
	@echo "🐳 Building Docker image..."
	docker build -t api-anomaly-detection:latest .

up:
	@echo "🚀 Starting with Docker Compose..."
	docker-compose up -d

down:
	@echo "🛑 Stopping Docker Compose..."
	docker-compose down

# Deployment commands
deploy:
	@echo "🚀 Deploying to production..."
	./scripts/deploy.sh latest production

deploy-staging:
	@echo "🧪 Deploying to staging..."
	./scripts/deploy.sh latest staging

# Health checks
health:
	@echo "🏥 Checking service health..."
	curl -f http://localhost:8000/health || echo "❌ Service is not healthy"

metrics:
	@echo "📊 Viewing metrics..."
	curl http://localhost:8000/metrics

# Development setup
setup:
	@echo "🛠️  Setting up development environment..."
	mkdir -p models logs data
	pip install -r requirements.txt
	python -m pytest test_main.py -v

# Full pipeline
pipeline:
	@echo "🔄 Running full CI/CD pipeline..."
	$(MAKE) clean
	$(MAKE) install
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) build
	$(MAKE) up
	$(MAKE) health
	@echo "✅ Pipeline completed successfully!"

# Quick start
quickstart:
	@echo "⚡ Quick start setup..."
	$(MAKE) setup
	$(MAKE) run
	@echo "✅ Service is ready at http://localhost:8000"
