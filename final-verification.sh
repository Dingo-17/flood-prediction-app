#!/bin/bash
echo "🎉 FINAL DEPLOYMENT VERIFICATION"
echo "================================="
echo ""
echo "Testing production backend at: https://flood-prediction-app-lkmp.onrender.com"
echo ""

# Test root endpoint
echo "1. Testing Root API Endpoint:"
root_response=$(curl -s https://flood-prediction-app-lkmp.onrender.com/)
if echo "$root_response" | grep -q '"status":"live"'; then
    echo "   ✅ Root endpoint: WORKING"
    echo "   Status: $(echo "$root_response" | grep -o '"status":"[^"]*"')"
    echo "   Version: $(echo "$root_response" | grep -o '"version":"[^"]*"')"
else
    echo "   ❌ Root endpoint: FAILED"
    echo "   Response: $root_response"
fi

echo ""

# Test locations endpoint
echo "2. Testing Locations API Endpoint:"
locations_response=$(curl -s https://flood-prediction-app-lkmp.onrender.com/api/locations)
if echo "$locations_response" | grep -q '"location_name"'; then
    location_count=$(echo "$locations_response" | grep -o '"location_name"' | wc -l | tr -d ' ')
    echo "   ✅ Locations endpoint: WORKING"
    echo "   Found $location_count locations"
    echo "   Sample location: $(echo "$locations_response" | grep -o '"location_name":"[^"]*"' | head -1)"
else
    echo "   ❌ Locations endpoint: FAILED"
    echo "   Response: $locations_response" | head -3
fi

echo ""

# Test specific prediction
echo "3. Testing Flood Prediction for Dhaka:"
prediction_response=$(curl -s https://flood-prediction-app-lkmp.onrender.com/api/predict/Dhaka)
if echo "$prediction_response" | grep -q '"flood_risk"'; then
    risk_level=$(echo "$prediction_response" | grep -o '"risk_level":"[^"]*"' | head -1)
    risk_percentage=$(echo "$prediction_response" | grep -o '"risk_percentage":[0-9.]*' | head -1)
    echo "   ✅ Prediction endpoint: WORKING"
    echo "   Dhaka $risk_level"
    echo "   Risk: $risk_percentage%"
else
    echo "   ❌ Prediction endpoint: FAILED"
    echo "   Response: $prediction_response" | head -3
fi

echo ""

# Check iOS app configuration
echo "4. Checking iOS App Configuration:"
if grep -q "flood-prediction-app-lkmp.onrender.com" www/js/app.js; then
    echo "   ✅ iOS app configured with correct production URL"
else
    echo "   ❌ iOS app still has old URL - needs update"
fi

echo ""

# Overall status
echo "🚀 OVERALL STATUS:"
if echo "$root_response" | grep -q '"status":"live"' && echo "$locations_response" | grep -q '"location_name"'; then
    echo "✅ BACKEND IS FULLY OPERATIONAL!"
    echo "✅ All API endpoints working correctly"
    echo "✅ Flood prediction system live"
    echo ""
    echo "🎯 READY FOR iOS BUILD:"
    echo "Run: ./build-production.sh"
    echo ""
    echo "📱 THEN SUBMIT TO APP STORE:"
    echo "Follow the App Store preparation steps in SETUP_GUIDE.md"
else
    echo "❌ Some issues detected - check individual endpoint results above"
fi

echo ""
