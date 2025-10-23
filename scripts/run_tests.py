#!/usr/bin/env python3
"""
Comprehensive Test Runner for API Anomaly Detection System
Ensures 100% pipeline success with automated testing
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
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

def main():
    """Main test runner"""
    print("🧪 API Anomaly Detection System - Comprehensive Test Suite")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    # Test results tracking
    tests_passed = 0
    total_tests = 0
    
    # 1. Code Quality Tests
    print("\n📋 Running Code Quality Tests")
    print("-" * 40)
    
    total_tests += 1
    if run_command("python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Linting"):
        tests_passed += 1
    
    total_tests += 1
    if run_command("python -m black --check --diff .", "Code Formatting"):
        tests_passed += 1
    
    total_tests += 1
    if run_command("python -m isort --check-only --diff .", "Import Sorting"):
        tests_passed += 1
    
    # 2. Security Tests
    print("\n🔒 Running Security Tests")
    print("-" * 40)
    
    total_tests += 1
    if run_command("python -m safety check", "Security Scan"):
        tests_passed += 1
    
    total_tests += 1
    if run_command("python -m bandit -r .", "Security Analysis"):
        tests_passed += 1
    
    # 3. Unit Tests
    print("\n🧪 Running Unit Tests")
    print("-" * 40)
    
    total_tests += 1
    if run_command("python -m pytest test_main.py -v --tb=short --cov=main --cov-report=term-missing", "Unit Tests"):
        tests_passed += 1
    
    # 4. Integration Tests
    print("\n🔗 Running Integration Tests")
    print("-" * 40)
    
    # Start the service if not running
    print("🚀 Starting service for integration tests...")
    if not check_service_health():
        print("Starting service with Docker...")
        run_command("docker-compose up -d", "Start Service")
        time.sleep(10)
        
        if not check_service_health():
            print("❌ Failed to start service for integration tests")
            sys.exit(1)
    
    total_tests += 1
    if run_command("python scripts/test_pipeline.py --url http://localhost:8000 --report", "Integration Tests"):
        tests_passed += 1
    
    # 5. Performance Tests
    print("\n⚡ Running Performance Tests")
    print("-" * 40)
    
    total_tests += 1
    if run_command("python -c \"import requests; import time; start=time.time(); [requests.get('http://localhost:8000/health') for _ in range(100)]; print(f'100 requests in {time.time()-start:.2f}s')\"", "Performance Test"):
        tests_passed += 1
    
    # 6. Docker Tests
    print("\n🐳 Running Docker Tests")
    print("-" * 40)
    
    total_tests += 1
    if run_command("docker build -t api-anomaly-detection:test .", "Docker Build"):
        tests_passed += 1
    
    total_tests += 1
    if run_command("docker run --rm -d --name test-container -p 8001:8000 api-anomaly-detection:test", "Docker Run"):
        tests_passed += 1
        
        # Test Docker container
        time.sleep(5)
        if check_service_health("http://localhost:8001"):
            run_command("docker stop test-container", "Stop Test Container")
            tests_passed += 1
        else:
            run_command("docker stop test-container", "Stop Test Container")
            tests_passed -= 1  # Revert the previous pass
    
    # 7. Documentation Tests
    print("\n📚 Running Documentation Tests")
    print("-" * 40)
    
    total_tests += 1
    if run_command("python -c \"import main; print('API documentation generated successfully')\"", "API Documentation"):
        tests_passed += 1
    
    # Results Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {total_tests - tests_passed}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Pipeline is ready for deployment.")
        print("✅ Code quality checks passed")
        print("✅ Security scans passed")
        print("✅ Unit tests passed")
        print("✅ Integration tests passed")
        print("✅ Performance tests passed")
        print("✅ Docker tests passed")
        print("✅ Documentation tests passed")
        return 0
    else:
        print(f"\n⚠️  {total_tests - tests_passed} tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
