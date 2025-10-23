#!/usr/bin/env python3
"""
Comprehensive Pipeline Test Suite
Ensures 100% success rate for the API Anomaly Detection System
"""

import asyncio
import json
import time
import requests
import subprocess
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class PipelineTester:
    """Comprehensive pipeline testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.auth_token = "your-secret-token"
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def generate_test_data(self, count: int = 100, anomaly_ratio: float = 0.1) -> List[Dict]:
        """Generate test API logs"""
        logs = []
        base_time = datetime.now()
        
        for i in range(count):
            is_anomaly = i < int(count * anomaly_ratio)
            
            if is_anomaly:
                # Anomalous patterns
                log = {
                    "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
                    "user_id": f"user_{i % 10}",
                    "endpoint": f"/api/anomalous/{i}",
                    "method": "POST" if i % 3 == 0 else "GET",
                    "status_code": 500 if i % 2 == 0 else 200,
                    "response_time": 5.0 + np.random.normal(0, 2),
                    "ip_address": f"192.168.1.{i % 255}",
                    "user_agent": "SuspiciousBot/1.0",
                    "request_size": 10000 + np.random.randint(0, 5000),
                    "response_size": 50000 + np.random.randint(0, 10000)
                }
            else:
                # Normal patterns
                log = {
                    "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
                    "user_id": f"user_{i % 10}",
                    "endpoint": f"/api/normal/{i % 5}",
                    "method": "GET" if i % 2 == 0 else "POST",
                    "status_code": 200 if i % 10 != 0 else 404,
                    "response_time": 0.1 + np.random.normal(0, 0.05),
                    "ip_address": f"192.168.1.{i % 10}",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "request_size": 100 + np.random.randint(0, 500),
                    "response_size": 1000 + np.random.randint(0, 2000)
                }
            logs.append(log)
        
        return logs
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            self.log_test("Health Endpoint", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Health Endpoint", False, str(e))
            return False
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            success = response.status_code == 200 and "text/plain" in response.headers.get("content-type", "")
            self.log_test("Metrics Endpoint", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Metrics Endpoint", False, str(e))
            return False
    
    def test_authentication(self):
        """Test authentication"""
        try:
            # Test without auth
            response = requests.get(f"{self.base_url}/status", timeout=10)
            success = response.status_code == 401
            self.log_test("Authentication (No Token)", success, f"Status: {response.status_code}")
            
            # Test with invalid token
            headers = {"Authorization": "Bearer invalid-token"}
            response = requests.get(f"{self.base_url}/status", headers=headers, timeout=10)
            success = response.status_code == 401
            self.log_test("Authentication (Invalid Token)", success, f"Status: {response.status_code}")
            
            # Test with valid token
            response = requests.get(f"{self.base_url}/status", headers=self.headers, timeout=10)
            success = response.status_code == 200
            self.log_test("Authentication (Valid Token)", success, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test("Authentication", False, str(e))
            return False
    
    def test_model_training(self):
        """Test model training"""
        try:
            training_data = {
                "logs": self.generate_test_data(1000, 0.1),
                "test_size": 0.2
            }
            
            response = requests.post(
                f"{self.base_url}/train",
                json=training_data,
                headers=self.headers,
                timeout=60
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("status") == "success"
                self.log_test("Model Training", success, f"Training samples: {data.get('training_samples', 0)}")
            else:
                self.log_test("Model Training", False, f"Status: {response.status_code}, Response: {response.text}")
            
            return success
        except Exception as e:
            self.log_test("Model Training", False, str(e))
            return False
    
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        try:
            test_logs = self.generate_test_data(50, 0.2)
            detection_data = {
                "logs": test_logs,
                "threshold": -0.5
            }
            
            response = requests.post(
                f"{self.base_url}/detect",
                json=detection_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "anomalies" in data and "total_logs" in data
                self.log_test("Anomaly Detection", success, f"Anomalies: {data.get('anomaly_count', 0)}/{data.get('total_logs', 0)}")
            else:
                self.log_test("Anomaly Detection", False, f"Status: {response.status_code}, Response: {response.text}")
            
            return success
        except Exception as e:
            self.log_test("Anomaly Detection", False, str(e))
            return False
    
    def test_model_status(self):
        """Test model status"""
        try:
            response = requests.get(f"{self.base_url}/status", headers=self.headers, timeout=10)
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "is_trained" in data
                self.log_test("Model Status", success, f"Trained: {data.get('is_trained', False)}")
            else:
                self.log_test("Model Status", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test("Model Status", False, str(e))
            return False
    
    def test_performance(self):
        """Test performance under load"""
        try:
            def make_request():
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    return response.status_code == 200
                except:
                    return False
            
            # Test with concurrent requests
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(100)]
                results = [f.result() for f in as_completed(futures)]
            
            end_time = time.time()
            duration = end_time - start_time
            success_rate = sum(results) / len(results)
            
            success = success_rate >= 0.95 and duration < 30
            self.log_test("Performance Test", success, f"Success rate: {success_rate:.2%}, Duration: {duration:.2f}s")
            
            return success
        except Exception as e:
            self.log_test("Performance Test", False, str(e))
            return False
    
    def test_error_handling(self):
        """Test error handling"""
        try:
            # Test malformed JSON
            response = requests.post(
                f"{self.base_url}/train",
                data="invalid json",
                headers=self.headers,
                timeout=10
            )
            success = response.status_code == 422
            self.log_test("Error Handling (Malformed JSON)", success, f"Status: {response.status_code}")
            
            # Test missing required fields
            response = requests.post(
                f"{self.base_url}/train",
                json={},
                headers=self.headers,
                timeout=10
            )
            success = response.status_code == 422
            self.log_test("Error Handling (Missing Fields)", success, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test("Error Handling", False, str(e))
            return False
    
    def test_data_validation(self):
        """Test data validation"""
        try:
            # Test with invalid data types
            invalid_data = {
                "logs": [{
                    "timestamp": "invalid-date",
                    "user_id": 123,  # Should be string
                    "endpoint": "/test",
                    "method": "GET",
                    "status_code": "200",  # Should be int
                    "response_time": "0.5",  # Should be float
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0"
                }]
            }
            
            response = requests.post(
                f"{self.base_url}/train",
                json=invalid_data,
                headers=self.headers,
                timeout=10
            )
            
            success = response.status_code == 422
            self.log_test("Data Validation", success, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test("Data Validation", False, str(e))
            return False
    
    def test_integration_workflow(self):
        """Test complete integration workflow"""
        try:
            # Step 1: Train model
            training_data = {
                "logs": self.generate_test_data(500, 0.1),
                "test_size": 0.2
            }
            
            response = requests.post(
                f"{self.base_url}/train",
                json=training_data,
                headers=self.headers,
                timeout=60
            )
            
            if response.status_code != 200:
                self.log_test("Integration Workflow", False, "Training failed")
                return False
            
            # Step 2: Check status
            response = requests.get(f"{self.base_url}/status", headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Integration Workflow", False, "Status check failed")
                return False
            
            # Step 3: Detect anomalies
            test_logs = self.generate_test_data(50, 0.2)
            detection_data = {
                "logs": test_logs,
                "threshold": -0.5
            }
            
            response = requests.post(
                f"{self.base_url}/detect",
                json=detection_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "anomalies" in data and "total_logs" in data
                self.log_test("Integration Workflow", success, f"Complete workflow successful")
            else:
                self.log_test("Integration Workflow", False, f"Detection failed: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test("Integration Workflow", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all pipeline tests"""
        print("🧪 Starting Comprehensive Pipeline Tests")
        print("=" * 50)
        
        tests = [
            self.test_health_endpoint,
            self.test_metrics_endpoint,
            self.test_authentication,
            self.test_model_training,
            self.test_anomaly_detection,
            self.test_model_status,
            self.test_performance,
            self.test_error_handling,
            self.test_data_validation,
            self.test_integration_workflow
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Pipeline is ready for deployment.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Please fix issues before deployment.")
            return False
    
    def generate_report(self):
        """Generate test report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["success"]),
            "failed_tests": sum(1 for r in self.test_results if not r["success"]),
            "success_rate": sum(1 for r in self.test_results if r["success"]) / len(self.test_results) if self.test_results else 0,
            "results": self.test_results
        }
        
        with open("pipeline_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Test report saved to pipeline_test_report.json")
        return report

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API Anomaly Detection Pipeline Tester")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for the API")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    
    args = parser.parse_args()
    
    tester = PipelineTester(args.url)
    
    # Wait for service to be ready
    print("⏳ Waiting for service to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{args.url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Service is ready!")
                break
        except:
            if i == 29:
                print("❌ Service is not responding. Please start the service first.")
                sys.exit(1)
            time.sleep(2)
    
    # Run tests
    success = tester.run_all_tests()
    
    if args.report:
        tester.generate_report()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
