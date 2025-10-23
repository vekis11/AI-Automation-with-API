"""
Comprehensive test suite for API Anomaly Detection System
Ensures 100% pipeline success with thorough testing
"""

import asyncio
import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import AnomalyDetectionRequest, APILog, TrainingData, app, extract_features

# Test client
client = TestClient(app)


# Test data generators
def generate_test_logs(count: int = 100, anomaly_ratio: float = 0.1) -> list:
    """Generate test API logs with some anomalies"""
    logs = []
    base_time = datetime.now()

    for i in range(count):
        # Create normal or anomalous log
        is_anomaly = i < int(count * anomaly_ratio)

        if is_anomaly:
            # Anomalous patterns
            log = APILog(
                timestamp=base_time + timedelta(minutes=i),
                user_id=f"user_{i % 10}",
                endpoint=f"/api/anomalous/{i}",
                method="POST" if i % 3 == 0 else "GET",
                status_code=500 if i % 2 == 0 else 200,
                response_time=5.0 + np.random.normal(0, 2),  # High response time
                ip_address=f"192.168.1.{i % 255}",
                user_agent="SuspiciousBot/1.0",
                request_size=10000 + np.random.randint(0, 5000),
                response_size=50000 + np.random.randint(0, 10000),
            )
        else:
            # Normal patterns
            log = APILog(
                timestamp=base_time + timedelta(minutes=i),
                user_id=f"user_{i % 10}",
                endpoint=f"/api/normal/{i % 5}",
                method="GET" if i % 2 == 0 else "POST",
                status_code=200 if i % 10 != 0 else 404,
                response_time=0.1 + np.random.normal(0, 0.05),
                ip_address=f"192.168.1.{i % 10}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                request_size=100 + np.random.randint(0, 500),
                response_size=1000 + np.random.randint(0, 2000),
            )
        logs.append(log)

    return logs


class TestHealthEndpoints:
    """Test health and status endpoints"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestAuthentication:
    """Test authentication and security"""

    def test_protected_endpoints_require_auth(self):
        """Test that protected endpoints require authentication"""
        # Test train endpoint without auth
        response = client.post("/train", json={"logs": []})
        assert response.status_code == 401

        # Test detect endpoint without auth
        response = client.post("/detect", json={"logs": []})
        assert response.status_code == 401

        # Test status endpoint without auth
        response = client.get("/status")
        assert response.status_code == 401

    def test_invalid_token(self):
        """Test with invalid token"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/train", json={"logs": []}, headers=headers)
        assert response.status_code == 401

    def test_valid_token(self):
        """Test with valid token"""
        headers = {"Authorization": "Bearer your-secret-token"}
        response = client.get("/status", headers=headers)
        assert response.status_code == 200


class TestModelTraining:
    """Test model training functionality"""

    @pytest.fixture
    def training_data(self):
        """Generate training data"""
        logs = generate_test_logs(1000, 0.1)
        return TrainingData(logs=logs, test_size=0.2)

    def test_train_model_success(self, training_data):
        """Test successful model training"""
        headers = {"Authorization": "Bearer your-secret-token"}

        with patch('main.joblib.dump') as mock_dump:
            response = client.post("/train", json=training_data.dict(), headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "training_samples" in data
            assert data["training_samples"] == 1000
            assert "model_accuracy" in data

    def test_train_model_validation_error(self):
        """Test training with invalid data"""
        headers = {"Authorization": "Bearer your-secret-token"}

        # Test with empty logs
        response = client.post("/train", json={"logs": []}, headers=headers)
        assert response.status_code == 200  # Should handle empty data gracefully

    def test_train_model_exception_handling(self, training_data):
        """Test training exception handling"""
        headers = {"Authorization": "Bearer your-secret-token"}

        with patch('main.extract_features', side_effect=Exception("Feature extraction failed")):
            response = client.post("/train", json=training_data.dict(), headers=headers)
            assert response.status_code == 500
            assert "Training failed" in response.json()["detail"]


class TestAnomalyDetection:
    """Test anomaly detection functionality"""

    @pytest.fixture
    def trained_model(self):
        """Mock a trained model"""
        with patch('main.model') as mock_model, patch('main.scaler') as mock_scaler, patch('main.is_trained', True):

            # Mock model predictions
            mock_model.predict.return_value = np.array([1, -1, 1, -1, 1])
            mock_model.decision_function.return_value = np.array([0.1, -0.8, 0.2, -0.9, 0.1])

            # Mock scaler
            mock_scaler.transform.return_value = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]])

            yield mock_model, mock_scaler

    def test_detect_anomalies_success(self, trained_model):
        """Test successful anomaly detection"""
        headers = {"Authorization": "Bearer your-secret-token"}
        logs = generate_test_logs(5, 0.4)

        request_data = AnomalyDetectionRequest(logs=logs, threshold=-0.5)

        with patch('main.extract_features') as mock_extract:
            mock_extract.return_value = pd.DataFrame(
                {'hour': [1, 2, 3, 4, 5], 'status_code': [200, 500, 200, 500, 200], 'response_time': [0.1, 5.0, 0.2, 4.0, 0.1]}
            )

            response = client.post("/detect", json=request_data.dict(), headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert "anomalies" in data
            assert "total_logs" in data
            assert "anomaly_count" in data
            assert "anomaly_rate" in data
            assert "model_confidence" in data
            assert data["total_logs"] == 5

    def test_detect_anomalies_model_not_trained(self):
        """Test detection when model is not trained"""
        headers = {"Authorization": "Bearer your-secret-token"}
        logs = generate_test_logs(5)
        request_data = AnomalyDetectionRequest(logs=logs)

        with patch('main.is_trained', False):
            response = client.post("/detect", json=request_data.dict(), headers=headers)
            assert response.status_code == 400
            assert "Model not trained" in response.json()["detail"]

    def test_detect_anomalies_exception_handling(self, trained_model):
        """Test detection exception handling"""
        headers = {"Authorization": "Bearer your-secret-token"}
        logs = generate_test_logs(5)
        request_data = AnomalyDetectionRequest(logs=logs)

        with patch('main.extract_features', side_effect=Exception("Feature extraction failed")):
            response = client.post("/detect", json=request_data.dict(), headers=headers)
            assert response.status_code == 500
            assert "Detection failed" in response.json()["detail"]


class TestModelStatus:
    """Test model status functionality"""

    def test_model_status_not_trained(self):
        """Test model status when not trained"""
        headers = {"Authorization": "Bearer your-secret-token"}

        with patch('main.is_trained', False):
            response = client.get("/status", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["is_trained"] == False
            assert data["training_date"] is None

    def test_model_status_trained(self):
        """Test model status when trained"""
        headers = {"Authorization": "Bearer your-secret-token"}

        with patch('main.is_trained', True), patch('main.scaler') as mock_scaler:
            mock_scaler.feature_names_in_ = ['feature1', 'feature2', 'feature3']

            response = client.get("/status", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["is_trained"] == True
            assert data["feature_count"] == 3


class TestModelLoading:
    """Test model loading functionality"""

    def test_load_model_success(self):
        """Test successful model loading"""
        headers = {"Authorization": "Bearer your-secret-token"}

        with (
            patch('main.joblib.load') as mock_load,
            patch('main.os.path.exists', return_value=True),
            patch('main.is_trained', True),
        ):

            mock_model = MagicMock()
            mock_scaler = MagicMock()
            mock_load.side_effect = [mock_model, mock_scaler]

            response = client.post("/load-model", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    def test_load_model_not_found(self):
        """Test model loading when no model exists"""
        headers = {"Authorization": "Bearer your-secret-token"}

        with patch('main.os.path.exists', return_value=False):
            response = client.post("/load-model", headers=headers)
            assert response.status_code == 404
            assert "No trained model found" in response.json()["detail"]

    def test_load_model_exception(self):
        """Test model loading exception handling"""
        headers = {"Authorization": "Bearer your-secret-token"}

        with patch('main.os.path.exists', return_value=True), patch('main.joblib.load', side_effect=Exception("Load failed")):

            response = client.post("/load-model", headers=headers)
            assert response.status_code == 500
            assert "Model loading failed" in response.json()["detail"]


class TestFeatureExtraction:
    """Test feature extraction functionality"""

    def test_extract_features_basic(self):
        """Test basic feature extraction"""
        logs = generate_test_logs(10)
        features_df = extract_features(logs)

        assert isinstance(features_df, pd.DataFrame)
        assert len(features_df) == 10
        assert 'hour' in features_df.columns
        assert 'status_code' in features_df.columns
        assert 'response_time' in features_df.columns
        assert 'user_request_frequency' in features_df.columns

    def test_extract_features_empty_logs(self):
        """Test feature extraction with empty logs"""
        features_df = extract_features([])
        assert isinstance(features_df, pd.DataFrame)
        assert len(features_df) == 0

    def test_extract_features_single_log(self):
        """Test feature extraction with single log"""
        logs = generate_test_logs(1)
        features_df = extract_features(logs)

        assert len(features_df) == 1
        assert not features_df.empty


class TestDataValidation:
    """Test data validation and edge cases"""

    def test_apilog_validation(self):
        """Test APILog model validation"""
        # Valid log
        valid_log = APILog(
            timestamp=datetime.now(),
            user_id="user123",
            endpoint="/api/test",
            method="GET",
            status_code=200,
            response_time=0.5,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        assert valid_log.user_id == "user123"

    def test_anomaly_detection_request_validation(self):
        """Test AnomalyDetectionRequest validation"""
        logs = generate_test_logs(5)
        request = AnomalyDetectionRequest(logs=logs, threshold=-0.5)
        assert request.threshold == -0.5
        assert len(request.logs) == 5

    def test_training_data_validation(self):
        """Test TrainingData validation"""
        logs = generate_test_logs(100)
        training_data = TrainingData(logs=logs, test_size=0.2)
        assert training_data.test_size == 0.2
        assert len(training_data.logs) == 100


class TestPerformance:
    """Test performance and scalability"""

    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        headers = {"Authorization": "Bearer your-secret-token"}
        logs = generate_test_logs(10000)  # Large dataset

        with patch('main.joblib.dump'), patch('main.extract_features') as mock_extract:

            # Mock feature extraction to return reasonable data
            mock_extract.return_value = pd.DataFrame(
                {
                    'hour': np.random.randint(0, 24, 10000),
                    'status_code': np.random.choice([200, 404, 500], 10000),
                    'response_time': np.random.exponential(0.5, 10000),
                }
            )

            response = client.post("/train", json={"logs": [log.dict() for log in logs]}, headers=headers)
            assert response.status_code == 200

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        headers = {"Authorization": "Bearer your-secret-token"}
        logs = generate_test_logs(10)

        # This would need async testing in a real scenario
        # For now, just test that the endpoint can handle multiple calls
        for _ in range(5):
            response = client.get("/status", headers=headers)
            assert response.status_code == 200


class TestErrorHandling:
    """Test comprehensive error handling"""

    def test_malformed_json(self):
        """Test handling of malformed JSON"""
        headers = {"Authorization": "Bearer your-secret-token"}
        response = client.post("/train", data="invalid json", headers=headers)
        assert response.status_code == 422  # Validation error

    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        headers = {"Authorization": "Bearer your-secret-token"}
        response = client.post("/train", json={}, headers=headers)
        assert response.status_code == 422

    def test_invalid_data_types(self):
        """Test handling of invalid data types"""
        headers = {"Authorization": "Bearer your-secret-token"}
        invalid_data = {
            "logs": [
                {
                    "timestamp": "invalid-date",
                    "user_id": 123,  # Should be string
                    "endpoint": "/test",
                    "method": "GET",
                    "status_code": "200",  # Should be int
                    "response_time": "0.5",  # Should be float
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0",
                }
            ]
        }
        response = client.post("/train", json=invalid_data, headers=headers)
        assert response.status_code == 422


# Integration tests
class TestIntegration:
    """Test end-to-end integration scenarios"""

    def test_full_workflow(self):
        """Test complete workflow: train -> detect -> status"""
        headers = {"Authorization": "Bearer your-secret-token"}

        # Step 1: Train model
        training_logs = generate_test_logs(500, 0.1)
        with patch('main.joblib.dump'):
            train_response = client.post("/train", json={"logs": [log.dict() for log in training_logs]}, headers=headers)
            assert train_response.status_code == 200

        # Step 2: Check status
        status_response = client.get("/status", headers=headers)
        assert status_response.status_code == 200

        # Step 3: Detect anomalies
        test_logs = generate_test_logs(50, 0.2)
        with patch('main.is_trained', True), patch('main.model') as mock_model, patch('main.scaler') as mock_scaler:

            mock_model.predict.return_value = np.array([1] * 40 + [-1] * 10)
            mock_model.decision_function.return_value = np.array([0.1] * 40 + [-0.8] * 10)
            mock_scaler.transform.return_value = np.random.rand(50, 10)

            detect_response = client.post("/detect", json={"logs": [log.dict() for log in test_logs]}, headers=headers)
            assert detect_response.status_code == 200
            data = detect_response.json()
            assert data["anomaly_count"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
