#!/bin/bash

# Test ML-Enhanced Backend
echo "🧠 Testing ML-Enhanced Flood Prediction Backend..."
echo ""

BASE_URL="https://flood-prediction-app-lkmp.onrender.com"

echo "🔍 Testing API Status..."
echo "curl -s '$BASE_URL/'"
echo "Response:"
curl -s "$BASE_URL/" | python3 -m json.tool 2>/dev/null || curl -s "$BASE_URL/"
echo ""
echo "---"

echo ""
echo "🌊 Testing Enhanced Prediction (Dhaka)..."
echo "curl -s '$BASE_URL/api/predict/Dhaka'"
echo "Response:"
curl -s "$BASE_URL/api/predict/Dhaka" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('✅ Location:', data.get('location'))
    print('✅ Risk Level:', data.get('risk_assessment', {}).get('risk_level'))
    print('✅ Risk Probability:', data.get('risk_assessment', {}).get('risk_probability'))
    print('✅ Prediction Method:', data.get('predictions', {}).get('method'))
    print('✅ ML Enabled:', data.get('predictions', {}).get('ml_enabled'))
    print('✅ Features Analyzed:', data.get('predictions', {}).get('features_analyzed'))
    print('✅ Rainfall Today:', data.get('weather_forecast', {}).get('rainfall_today'))
    print('✅ Water Level:', data.get('current_conditions', {}).get('water_level_m'))
except:
    print('❌ Error parsing JSON response')
"
echo ""
echo "---"

echo ""
echo "🗺️ Testing Enhanced Locations..."
echo "curl -s '$BASE_URL/api/locations'"
echo "Response:"
curl -s "$BASE_URL/api/locations" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'✅ Total Locations: {len(data)}')
    for loc in data:
        print(f'  📍 {loc[\"name\"]}: Elevation {loc.get(\"elevation\", \"N/A\")}m, Drainage: {loc.get(\"drainage_quality\", \"Unknown\")}')
except:
    print('❌ Error parsing JSON response')
"
echo ""
echo "---"

echo ""
echo "📊 Testing System Status..."
echo "curl -s '$BASE_URL/api/status'"
echo "Response:"
curl -s "$BASE_URL/api/status" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    ml_info = data.get('ml_model', {})
    print('✅ System:', data.get('system'))
    print('✅ Version:', data.get('version'))
    print('✅ ML Available:', ml_info.get('available'))
    print('✅ ML Type:', ml_info.get('type'))
    print('✅ ML Features:', ml_info.get('features'))
    print('✅ Training Samples:', ml_info.get('training_samples'))
    print('✅ Locations Monitored:', data.get('locations_monitored'))
except:
    print('❌ Error parsing JSON response')
"
echo ""
echo "---"

echo ""
echo "🚨 Testing Alerts System..."
echo "curl -s '$BASE_URL/api/alerts'"
echo "Response:"
curl -s "$BASE_URL/api/alerts" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    alerts = data.get('alerts', [])
    print(f'✅ Total Alerts: {data.get(\"total_alerts\", 0)}')
    for alert in alerts:
        print(f'  🚨 {alert[\"location\"]}: {alert[\"alert_level\"]} (Risk: {alert[\"risk_probability\"]})')
except:
    print('❌ Error parsing JSON response')
"

echo ""
echo "🎯 EXPECTED RESULTS:"
echo "✅ Version should be '2.0.0'"
echo "✅ ml_enabled should be true"
echo "✅ method should be 'random_forest_ml'"
echo "✅ features_analyzed should be 9"
echo "✅ Enhanced geographic data should be visible"
echo ""
echo "📱 If all tests pass, your iOS app now uses the same advanced ML as the website!"
