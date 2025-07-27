#!/bin/bash

# Test Production Backend Deployment
echo "🔍 Testing Flood Prediction Backend Deployment"
echo "Backend URL: https://ai-flood-prediction-system.onrender.com"
echo ""

# Test root endpoint
echo "Testing root endpoint..."
ROOT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://ai-flood-prediction-system.onrender.com/)
echo "Root endpoint status: $ROOT_STATUS"

# Test API endpoint
echo "Testing API locations endpoint..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://ai-flood-prediction-system.onrender.com/api/locations)
echo "API endpoint status: $API_STATUS"

# Test with actual response
echo ""
echo "Testing API response..."
curl -s https://ai-flood-prediction-system.onrender.com/api/locations | head -n 5

echo ""
echo "🕐 If you see 404 errors, the deployment may still be in progress."
echo "🕐 Render deployments typically take 5-10 minutes."
echo "🕐 Check https://dashboard.render.com for deployment status."
echo ""
echo "✅ Once you see JSON response above, the backend is ready!"
echo "✅ Then you can run: ./build-production.sh"
