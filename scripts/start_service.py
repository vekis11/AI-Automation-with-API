#!/usr/bin/env python3
"""
Service Startup Script for API Anomaly Detection System
Ensures proper service initialization and health checks
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import requests


def create_directories():
    """Create necessary directories"""
    directories = ["models", "logs", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def start_service(method="python"):
    """Start the service using specified method"""
    print(f"🚀 Starting service using {method}...")

    if method == "python":
        try:
            # Start the service in background
            process = subprocess.Popen([sys.executable, "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ Service started with PID: {process.pid}")
            return process
        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            return None

    elif method == "docker":
        try:
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            print("✅ Service started with Docker Compose")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start service with Docker: {e}")
            return False

    else:
        print(f"❌ Unknown method: {method}")
        return False


def check_service_health(url="http://localhost:8000", max_attempts=30):
    """Check if the service is healthy"""
    print(f"🏥 Checking service health at {url}...")

    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Service is healthy and ready")
                return True
        except:
            pass

        if attempt < max_attempts - 1:
            print(f"⏳ Waiting for service... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)

    print("❌ Service health check failed")
    return False


def run_initial_tests():
    """Run initial tests to verify service functionality"""
    print("🧪 Running initial tests...")

    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code != 200:
            print("❌ Health endpoint test failed")
            return False
        print("✅ Health endpoint test passed")
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

    # Test metrics endpoint
    try:
        response = requests.get("http://localhost:8000/metrics", timeout=10)
        if response.status_code != 200:
            print("❌ Metrics endpoint test failed")
            return False
        print("✅ Metrics endpoint test passed")
    except Exception as e:
        print(f"❌ Metrics endpoint test failed: {e}")
        return False

    # Test authentication
    try:
        response = requests.get("http://localhost:8000/status", timeout=10)
        if response.status_code != 401:
            print("❌ Authentication test failed")
            return False
        print("✅ Authentication test passed")
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

    return True


def main():
    """Main startup function"""
    print("🚀 API Anomaly Detection System - Service Startup")
    print("=" * 50)

    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)

    # Parse command line arguments
    method = "python"
    if len(sys.argv) > 1:
        method = sys.argv[1]

    # Step 1: Create directories
    create_directories()

    # Step 2: Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Step 3: Start service
    if method == "python":
        process = start_service(method)
        if process is None:
            sys.exit(1)
    else:
        if not start_service(method):
            sys.exit(1)

    # Step 4: Wait for service to be ready
    print("⏳ Waiting for service to be ready...")
    time.sleep(5)

    # Step 5: Health check
    if not check_service_health():
        print("❌ Service failed to start properly")
        if method == "python" and 'process' in locals():
            process.terminate()
        sys.exit(1)

    # Step 6: Run initial tests
    if not run_initial_tests():
        print("❌ Initial tests failed")
        if method == "python" and 'process' in locals():
            process.terminate()
        sys.exit(1)

    # Step 7: Success message
    print("\n🎉 Service started successfully!")
    print("=" * 50)
    print("📊 Service Information:")
    print(f"   URL: http://localhost:8000")
    print(f"   Health: http://localhost:8000/health")
    print(f"   Metrics: http://localhost:8000/metrics")
    print(f"   Documentation: http://localhost:8000/docs")
    print("\n🔧 Available Commands:")
    print("   python scripts/test_pipeline.py  # Run full test suite")
    print("   python scripts/run_tests.py      # Run all tests")
    print("   docker-compose logs -f           # View logs")
    print("\n🛑 To stop the service:")
    if method == "python":
        print("   Press Ctrl+C or kill the process")
    else:
        print("   docker-compose down")

    # Keep the service running
    if method == "python" and 'process' in locals():
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping service...")
            process.terminate()
            process.wait()
            print("✅ Service stopped")


if __name__ == "__main__":
    main()
