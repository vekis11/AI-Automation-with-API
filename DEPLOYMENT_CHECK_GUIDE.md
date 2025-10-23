# 🚀 Deployment Check Guide

## Quick URL Checks

### 1. **Basic Health Check**
```bash
# Check if service is running
curl http://localhost:8000/health

# With verbose output
curl -v http://localhost:8000/health
```

### 2. **All Available Endpoints**
| Endpoint | Method | Description | Check Command |
|----------|--------|-------------|---------------|
| `/health` | GET | Health check | `curl http://localhost:8000/health` |
| `/metrics` | GET | Prometheus metrics | `curl http://localhost:8000/metrics` |
| `/status` | GET | Model status | `curl http://localhost:8000/status` |
| `/docs` | GET | API documentation | `curl http://localhost:8000/docs` |
| `/redoc` | GET | Alternative docs | `curl http://localhost:8000/redoc` |
| `/train` | POST | Train model | See training example below |
| `/detect` | POST | Detect anomalies | See detection example below |

### 3. **Comprehensive Checks**

#### Option A: Python Script (Recommended)
```bash
# Run comprehensive check
python scripts/check_deployment.py

# With custom URL
python scripts/check_deployment.py --url http://your-server:8000

# With authentication token
python scripts/check_deployment.py --url http://your-server:8000 --token your-actual-token
```

#### Option B: Bash Script
```bash
# Make executable
chmod +x scripts/curl_checks.sh

# Run checks
./scripts/curl_checks.sh

# With custom URL and token
./scripts/curl_checks.sh http://your-server:8000 your-actual-token
```

### 4. **Manual API Testing**

#### Test Training Endpoint
```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
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
  }'
```

#### Test Detection Endpoint
```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
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
  }'
```

### 5. **Docker Deployment Checks**

#### Check if container is running
```bash
# List running containers
docker ps

# Check container logs
docker logs api-anomaly-detection

# Check container health
docker inspect api-anomaly-detection --format='{{.State.Health.Status}}'
```

#### Test Docker deployment
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test from inside container
docker exec api-anomaly-detection curl http://localhost:8000/health
```

### 6. **Production Deployment Checks**

#### For Cloud Deployments
```bash
# Replace with your actual domain
BASE_URL="https://your-api.example.com"

# Health check
curl $BASE_URL/health

# Full check
python scripts/check_deployment.py --url $BASE_URL --token your-production-token
```

#### For Kubernetes Deployments
```bash
# Port forward to access service
kubectl port-forward service/api-anomaly-detection 8000:8000

# Then run checks
curl http://localhost:8000/health
```

### 7. **Expected Responses**

#### Health Endpoint (`/health`)
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "version": "1.0.0"
}
```

#### Status Endpoint (`/status`)
```json
{
  "is_trained": true,
  "training_date": "2024-01-01T10:00:00Z",
  "model_accuracy": 0.95,
  "feature_count": 6
}
```

#### Training Response
```json
{
  "message": "Model trained successfully",
  "accuracy": 0.95,
  "training_samples": 100,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Detection Response
```json
{
  "anomaly_count": 2,
  "anomalies": [
    {
      "log_index": 0,
      "anomaly_score": 0.85,
      "is_anomaly": true
    }
  ],
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 8. **Troubleshooting**

#### Common Issues
- **Connection refused**: Service not running
- **401 Unauthorized**: Invalid or missing token
- **404 Not Found**: Wrong endpoint URL
- **500 Internal Server Error**: Server-side error, check logs

#### Debug Commands
```bash
# Check if port is open
netstat -tulpn | grep :8000

# Check service status
systemctl status api-anomaly-detection

# Check logs
journalctl -u api-anomaly-detection -f
```

### 9. **Automated Monitoring**

#### Set up monitoring with cron
```bash
# Add to crontab for regular checks
*/5 * * * * curl -f http://localhost:8000/health || echo "Service down" | mail -s "API Alert" admin@example.com
```

#### Health check script for CI/CD
```bash
#!/bin/bash
# Add to your deployment pipeline
if curl -f http://localhost:8000/health; then
    echo "✅ Deployment successful"
    exit 0
else
    echo "❌ Deployment failed"
    exit 1
fi
```

## 🎯 Quick Start

1. **Start your service**
2. **Run basic check**: `curl http://localhost:8000/health`
3. **Run comprehensive check**: `python scripts/check_deployment.py`
4. **Check documentation**: Open `http://localhost:8000/docs` in browser

That's it! Your deployment is verified! 🚀
