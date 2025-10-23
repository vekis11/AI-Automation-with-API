#!/bin/bash

# API Anomaly Detection System Deployment Script
# Ensures 100% success deployment with comprehensive checks

set -e  # Exit on any error

echo "🚀 Starting API Anomaly Detection System Deployment"

# Configuration
APP_NAME="api-anomaly-detection"
VERSION=${1:-"latest"}
ENVIRONMENT=${2:-"production"}
PORT=${3:-8000}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Pre-deployment checks
log "Running pre-deployment checks..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed. Please install Docker Compose first."
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed. Please install Python 3 first."
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
fi

log "Pre-deployment checks passed ✅"

# Create necessary directories
log "Creating necessary directories..."
mkdir -p models logs data

# Install Python dependencies
log "Installing Python dependencies..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Run tests
log "Running test suite..."
python3 -m pytest test_main.py -v --tb=short --cov=main --cov-report=term-missing

if [ $? -ne 0 ]; then
    error "Tests failed. Deployment aborted."
fi

log "All tests passed ✅"

# Code quality checks
log "Running code quality checks..."

# Linting
if command -v flake8 &> /dev/null; then
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    if [ $? -ne 0 ]; then
        error "Linting failed. Please fix the issues."
    fi
fi

# Format checking
if command -v black &> /dev/null; then
    black --check --diff .
    if [ $? -ne 0 ]; then
        warn "Code formatting issues found. Consider running 'black .' to fix them."
    fi
fi

log "Code quality checks passed ✅"

# Build Docker image
log "Building Docker image..."
docker build -t $APP_NAME:$VERSION .

if [ $? -ne 0 ]; then
    error "Docker build failed."
fi

log "Docker image built successfully ✅"

# Test Docker container
log "Testing Docker container..."
docker run -d --name ${APP_NAME}-test -p $PORT:8000 $APP_NAME:$VERSION

# Wait for container to start
sleep 10

# Health check
log "Performing health check..."
for i in {1..30}; do
    if curl -f http://localhost:$PORT/health &> /dev/null; then
        log "Health check passed ✅"
        break
    fi
    if [ $i -eq 30 ]; then
        error "Health check failed after 30 attempts"
    fi
    sleep 2
done

# Stop test container
docker stop ${APP_NAME}-test
docker rm ${APP_NAME}-test

log "Container test passed ✅"

# Deploy based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    log "Deploying to production environment..."
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Start new containers
    docker-compose up -d
    
    # Wait for services to be ready
    sleep 15
    
    # Final health check
    log "Performing final health check..."
    for i in {1..30}; do
        if curl -f http://localhost:$PORT/health &> /dev/null; then
            log "Production deployment successful ✅"
            break
        fi
        if [ $i -eq 30 ]; then
            error "Production health check failed"
        fi
        sleep 2
    done
    
    # Check all services
    log "Checking all services..."
    docker-compose ps
    
    log "🎉 Deployment completed successfully!"
    log "API available at: http://localhost:$PORT"
    log "Health check: http://localhost:$PORT/health"
    log "Metrics: http://localhost:$PORT/metrics"
    log "Prometheus: http://localhost:9090"
    log "Grafana: http://localhost:3000 (admin/admin)"
    
elif [ "$ENVIRONMENT" = "staging" ]; then
    log "Deploying to staging environment..."
    
    # Use different port for staging
    STAGING_PORT=8001
    docker run -d --name ${APP_NAME}-staging -p $STAGING_PORT:8000 $APP_NAME:$VERSION
    
    # Wait and check
    sleep 10
    if curl -f http://localhost:$STAGING_PORT/health &> /dev/null; then
        log "Staging deployment successful ✅"
        log "Staging API available at: http://localhost:$STAGING_PORT"
    else
        error "Staging deployment failed"
    fi
    
else
    error "Unknown environment: $ENVIRONMENT. Use 'production' or 'staging'"
fi

# Cleanup
log "Cleaning up..."
docker image prune -f

log "🚀 Deployment script completed successfully!"
