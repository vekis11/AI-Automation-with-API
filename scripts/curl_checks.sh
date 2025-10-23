#!/bin/bash
# Simple curl-based deployment checks
# Usage: ./scripts/curl_checks.sh [BASE_URL] [TOKEN]

BASE_URL=${1:-"http://localhost:8000"}
TOKEN=${2:-"your-token-here"}

echo "🚀 Deployment Health Check with curl"
echo "Base URL: $BASE_URL"
echo "=================================="

# Function to check endpoint
check_endpoint() {
    local endpoint=$1
    local method=${2:-"GET"}
    local data=${3:-""}
    local expected_status=${4:-200}
    
    echo -n "Checking $method $endpoint... "
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "$data" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method \
            -H "Authorization: Bearer $TOKEN" \
            "$BASE_URL$endpoint")
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo "✅ PASSED ($status_code)"
        if [ -n "$body" ]; then
            echo "   Response: $body"
        fi
    else
        echo "❌ FAILED ($status_code)"
        if [ -n "$body" ]; then
            echo "   Error: $body"
        fi
    fi
}

# Basic health checks
echo ""
echo "📋 BASIC HEALTH CHECKS"
echo "----------------------"
check_endpoint "/health"
check_endpoint "/metrics"
check_endpoint "/status"

# Documentation checks
echo ""
echo "📚 DOCUMENTATION CHECKS"
echo "----------------------"
check_endpoint "/docs"
check_endpoint "/redoc"
check_endpoint "/openapi.json"

# API functionality checks
echo ""
echo "🔧 API FUNCTIONALITY CHECKS"
echo "---------------------------"

# Training endpoint
training_data='{
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
check_endpoint "/train" "POST" "$training_data"

# Detection endpoint
detection_data='{
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
check_endpoint "/detect" "POST" "$detection_data"

echo ""
echo "🎯 Deployment check completed!"
