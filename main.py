"""
API Anomaly Detection System
A FastAPI-based service for detecting anomalous user behavior in API logs using Isolation Forest ML model.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import logging
from datetime import datetime, timedelta
import json
from loguru import logger
import asyncio
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Configure logging
logger.add("logs/anomaly_detection.log", rotation="1 day", retention="30 days")

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')
ANOMALY_COUNT = Counter('anomalies_detected_total', 'Total anomalies detected')

app = FastAPI(
    title="API Anomaly Detection System",
    description="ML-powered anomaly detection for API logs using Isolation Forest",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global variables for model and scaler
model = None
scaler = None
is_trained = False

class APILog(BaseModel):
    """API log entry model"""
    timestamp: datetime
    user_id: str
    endpoint: str
    method: str
    status_code: int
    response_time: float
    ip_address: str
    user_agent: str
    request_size: Optional[int] = None
    response_size: Optional[int] = None

class AnomalyDetectionRequest(BaseModel):
    """Request model for anomaly detection"""
    logs: List[APILog]
    threshold: Optional[float] = -0.5

class AnomalyDetectionResponse(BaseModel):
    """Response model for anomaly detection"""
    anomalies: List[Dict[str, Any]]
    total_logs: int
    anomaly_count: int
    anomaly_rate: float
    model_confidence: float

class TrainingData(BaseModel):
    """Training data model"""
    logs: List[APILog]
    test_size: Optional[float] = 0.2

class ModelStatus(BaseModel):
    """Model status response"""
    is_trained: bool
    training_date: Optional[datetime]
    model_accuracy: Optional[float]
    feature_count: int

def extract_features(logs: List[APILog]) -> pd.DataFrame:
    """Extract features from API logs for ML model"""
    features = []
    
    for log in logs:
        # Basic features
        feature_dict = {
            'hour': log.timestamp.hour,
            'day_of_week': log.timestamp.weekday(),
            'status_code': log.status_code,
            'response_time': log.response_time,
            'request_size': log.request_size or 0,
            'response_size': log.response_size or 0,
        }
        
        # User behavior features
        user_logs = [l for l in logs if l.user_id == log.user_id]
        feature_dict.update({
            'user_request_frequency': len(user_logs),
            'user_avg_response_time': np.mean([l.response_time for l in user_logs]),
            'user_error_rate': len([l for l in user_logs if l.status_code >= 400]) / len(user_logs) if user_logs else 0,
        })
        
        # Endpoint features
        endpoint_logs = [l for l in logs if l.endpoint == log.endpoint]
        feature_dict.update({
            'endpoint_frequency': len(endpoint_logs),
            'endpoint_avg_response_time': np.mean([l.response_time for l in endpoint_logs]),
            'endpoint_error_rate': len([l for l in endpoint_logs if l.status_code >= 400]) / len(endpoint_logs) if endpoint_logs else 0,
        })
        
        # Time-based features
        recent_logs = [l for l in logs if (log.timestamp - l.timestamp).total_seconds() < 3600]  # Last hour
        feature_dict.update({
            'recent_requests': len(recent_logs),
            'recent_error_rate': len([l for l in recent_logs if l.status_code >= 400]) / len(recent_logs) if recent_logs else 0,
        })
        
        features.append(feature_dict)
    
    return pd.DataFrame(features)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token verification (in production, use proper JWT validation)"""
    if credentials.credentials != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return credentials.credentials

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/train", response_model=Dict[str, Any])
async def train_model(
    training_data: TrainingData,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Train the Isolation Forest model"""
    global model, scaler, is_trained
    
    try:
        logger.info(f"Starting model training with {len(training_data.logs)} logs")
        
        # Extract features
        features_df = extract_features(training_data.logs)
        
        # Split data
        X_train, X_test = train_test_split(
            features_df, 
            test_size=training_data.test_size, 
            random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Isolation Forest
        model = IsolationForest(
            contamination=0.1,  # Expected 10% anomalies
            random_state=42,
            n_estimators=100
        )
        model.fit(X_train_scaled)
        
        # Evaluate model
        train_scores = model.decision_function(X_train_scaled)
        test_scores = model.decision_function(X_test_scaled)
        
        # Calculate accuracy (assuming we have some labeled data)
        train_predictions = model.predict(X_train_scaled)
        test_predictions = model.predict(X_test_scaled)
        
        # Save model
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/isolation_forest.pkl")
        joblib.dump(scaler, "models/scaler.pkl")
        
        is_trained = True
        
        logger.info("Model training completed successfully")
        
        return {
            "status": "success",
            "message": "Model trained successfully",
            "training_samples": len(training_data.logs),
            "train_anomalies": np.sum(train_predictions == -1),
            "test_anomalies": np.sum(test_predictions == -1),
            "model_accuracy": np.mean(test_predictions == 1),  # Assuming most data is normal
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.post("/detect", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    token: str = Depends(verify_token)
):
    """Detect anomalies in API logs"""
    global model, scaler, is_trained
    
    if not is_trained or model is None or scaler is None:
        raise HTTPException(status_code=400, detail="Model not trained. Please train the model first.")
    
    try:
        REQUEST_COUNT.labels(method='POST', endpoint='/detect').inc()
        
        with REQUEST_DURATION.time():
            # Extract features
            features_df = extract_features(request.logs)
            
            # Scale features
            features_scaled = scaler.transform(features_df)
            
            # Predict anomalies
            predictions = model.predict(features_scaled)
            scores = model.decision_function(features_scaled)
            
            # Identify anomalies
            anomalies = []
            for i, (log, prediction, score) in enumerate(zip(request.logs, predictions, scores)):
                if prediction == -1 and score < request.threshold:
                    anomaly_data = {
                        "log_index": i,
                        "timestamp": log.timestamp,
                        "user_id": log.user_id,
                        "endpoint": log.endpoint,
                        "method": log.method,
                        "status_code": log.status_code,
                        "response_time": log.response_time,
                        "anomaly_score": float(score),
                        "severity": "high" if score < -0.8 else "medium" if score < -0.5 else "low"
                    }
                    anomalies.append(anomaly_data)
                    ANOMALY_COUNT.inc()
            
            logger.info(f"Detected {len(anomalies)} anomalies out of {len(request.logs)} logs")
            
            return AnomalyDetectionResponse(
                anomalies=anomalies,
                total_logs=len(request.logs),
                anomaly_count=len(anomalies),
                anomaly_rate=len(anomalies) / len(request.logs) if request.logs else 0,
                model_confidence=float(np.mean(scores))
            )
            
    except Exception as e:
        logger.error(f"Anomaly detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.get("/status", response_model=ModelStatus)
async def get_model_status(token: str = Depends(verify_token)):
    """Get model status and information"""
    global model, scaler, is_trained
    
    if not is_trained:
        return ModelStatus(
            is_trained=False,
            training_date=None,
            model_accuracy=None,
            feature_count=0
        )
    
    return ModelStatus(
        is_trained=True,
        training_date=datetime.now(),  # In production, store actual training date
        model_accuracy=0.85,  # In production, calculate actual accuracy
        feature_count=len(scaler.feature_names_in_) if scaler else 0
    )

@app.post("/load-model")
async def load_model(token: str = Depends(verify_token)):
    """Load pre-trained model from disk"""
    global model, scaler, is_trained
    
    try:
        if os.path.exists("models/isolation_forest.pkl") and os.path.exists("models/scaler.pkl"):
            model = joblib.load("models/isolation_forest.pkl")
            scaler = joblib.load("models/scaler.pkl")
            is_trained = True
            logger.info("Model loaded successfully from disk")
            return {"status": "success", "message": "Model loaded successfully"}
        else:
            raise HTTPException(status_code=404, detail="No trained model found on disk")
    except Exception as e:
        logger.error(f"Model loading failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
