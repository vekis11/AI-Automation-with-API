#!/usr/bin/env python3
"""
Deployment Health Check Script
Comprehensive URL-based testing for the API Anomaly Detection System
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class DeploymentChecker:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer your-token-here'  # Replace with actual token
        })
    
    def check_health(self) -> bool:
        """Check basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Health check: PASSED")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Health check: FAILED (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Health check: ERROR - {e}")
            return False
    
    def check_metrics(self) -> bool:
        """Check Prometheus metrics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/metrics", timeout=10)
            if response.status_code == 200:
                print("✅ Metrics endpoint: PASSED")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                return True
            else:
                print(f"❌ Metrics endpoint: FAILED (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Metrics endpoint: ERROR - {e}")
            return False
    
    def check_status(self) -> bool:
        """Check model status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/status", timeout=10)
            if response.status_code == 200:
                print("✅ Status endpoint: PASSED")
                status_data = response.json()
                print(f"   Model trained: {status_data.get('is_trained', False)}")
                print(f"   Feature count: {status_data.get('feature_count', 0)}")
                return True
            else:
                print(f"❌ Status endpoint: FAILED (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Status endpoint: ERROR - {e}")
            return False
    
    def check_docs(self) -> bool:
        """Check API documentation endpoints"""
        endpoints = [
            "/docs",
            "/redoc", 
            "/openapi.json"
        ]
        
        all_passed = True
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {endpoint}: PASSED")
                else:
                    print(f"❌ {endpoint}: FAILED (Status: {response.status_code})")
                    all_passed = False
            except Exception as e:
                print(f"❌ {endpoint}: ERROR - {e}")
                all_passed = False
        
        return all_passed
    
    def test_training_endpoint(self) -> bool:
        """Test the training endpoint with sample data"""
        try:
            # Sample training data
            training_data = {
                "logs": [
                    {
                        "timestamp": "2024-01-01T10:00:00Z",
                        "user_id": "user1",
                        "endpoint": "/api/users",
                        "method": "GET",
                        "response_time": 150,
                        "status_code": 200,
                        "ip_address": "192.168.1.1"
                    },
                    {
                        "timestamp": "2024-01-01T10:01:00Z",
                        "user_id": "user2", 
                        "endpoint": "/api/orders",
                        "method": "POST",
                        "response_time": 300,
                        "status_code": 201,
                        "ip_address": "192.168.1.2"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/train",
                json=training_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Training endpoint: PASSED")
                result = response.json()
                print(f"   Training accuracy: {result.get('accuracy', 'N/A')}")
                return True
            else:
                print(f"❌ Training endpoint: FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Training endpoint: ERROR - {e}")
            return False
    
    def test_detection_endpoint(self) -> bool:
        """Test the anomaly detection endpoint"""
        try:
            # Sample detection data
            detection_data = {
                "logs": [
                    {
                        "timestamp": "2024-01-01T10:00:00Z",
                        "user_id": "user1",
                        "endpoint": "/api/users",
                        "method": "GET", 
                        "response_time": 150,
                        "status_code": 200,
                        "ip_address": "192.168.1.1"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/detect",
                json=detection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Detection endpoint: PASSED")
                result = response.json()
                print(f"   Anomalies detected: {result.get('anomaly_count', 0)}")
                return True
            else:
                print(f"❌ Detection endpoint: FAILED (Status: {response.status_code})")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Detection endpoint: ERROR - {e}")
            return False
    
    def run_comprehensive_check(self) -> Dict[str, bool]:
        """Run all checks and return results"""
        print("🚀 Starting Comprehensive Deployment Check")
        print("=" * 60)
        
        results = {}
        
        # Basic health checks
        print("\n📋 BASIC HEALTH CHECKS")
        print("-" * 30)
        results['health'] = self.check_health()
        results['metrics'] = self.check_metrics()
        results['status'] = self.check_status()
        
        # Documentation checks
        print("\n📚 DOCUMENTATION CHECKS")
        print("-" * 30)
        results['docs'] = self.check_docs()
        
        # API functionality checks
        print("\n🔧 API FUNCTIONALITY CHECKS")
        print("-" * 30)
        results['training'] = self.test_training_endpoint()
        results['detection'] = self.test_detection_endpoint()
        
        # Summary
        print("\n📊 SUMMARY")
        print("=" * 60)
        passed = sum(results.values())
        total = len(results)
        
        for check, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {check.upper()}: {'PASSED' if status else 'FAILED'}")
        
        print(f"\n🎯 Overall: {passed}/{total} checks passed")
        
        if passed == total:
            print("🎉 All checks passed! Deployment is healthy!")
        else:
            print("⚠️  Some checks failed. Review the output above.")
        
        return results

def main():
    """Main function to run deployment checks"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check deployment health")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the deployed service")
    parser.add_argument("--token", default="your-token-here",
                       help="Authorization token for API calls")
    
    args = parser.parse_args()
    
    checker = DeploymentChecker(args.url)
    if args.token != "your-token-here":
        checker.session.headers.update({'Authorization': f'Bearer {args.token}'})
    
    results = checker.run_comprehensive_check()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All checks passed
    else:
        sys.exit(1)  # Some checks failed

if __name__ == "__main__":
    main()
