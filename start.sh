#!/bin/bash
# Start script for API deployment

echo "🚀 Starting API Anomaly Detection System..."

# Create necessary directories
mkdir -p models logs

# Set environment variables
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Start the application
python main.py
