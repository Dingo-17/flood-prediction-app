#!/bin/bash

# Render Deployment Test Script
# Run this after your Render deployment is complete

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Your Render URL (update this after deployment)
RENDER_URL="https://ai-flood-prediction-system.onrender.com"

echo -e "${YELLOW}🚀 Testing Render Deployment...${NC}"
echo -e "URL: $RENDER_URL"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
response=$(curl -s -w "%{http_code}" "$RENDER_URL/health" -o /tmp/health_response.txt)
if [ $response -eq 200 ]; then
    echo -e "${GREEN}✅ Health check passed (200)${NC}"
    cat /tmp/health_response.txt
else
    echo -e "${RED}❌ Health check failed ($response)${NC}"
fi
echo ""

# Test 2: Main Dashboard
echo -e "${YELLOW}Test 2: Main Dashboard${NC}"
response=$(curl -s -w "%{http_code}" "$RENDER_URL/" -o /tmp/dashboard_response.txt)
if [ $response -eq 200 ]; then
    echo -e "${GREEN}✅ Dashboard loaded (200)${NC}"
    echo "Content preview:"
    head -c 200 /tmp/dashboard_response.txt
    echo "..."
else
    echo -e "${RED}❌ Dashboard failed ($response)${NC}"
fi
echo ""

# Test 3: API Prediction
echo -e "${YELLOW}Test 3: API Prediction${NC}"
prediction_data='{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "water_level": 5.2,
    "rainfall": 25.5,
    "temperature": 22.3
}'

response=$(curl -s -w "%{http_code}" \
    -X POST "$RENDER_URL/api/predict" \
    -H "Content-Type: application/json" \
    -d "$prediction_data" \
    -o /tmp/prediction_response.txt)

if [ $response -eq 200 ]; then
    echo -e "${GREEN}✅ API prediction successful (200)${NC}"
    echo "Response:"
    cat /tmp/prediction_response.txt | python3 -m json.tool 2>/dev/null || cat /tmp/prediction_response.txt
else
    echo -e "${RED}❌ API prediction failed ($response)${NC}"
    echo "Response:"
    cat /tmp/prediction_response.txt
fi
echo ""

# Test 4: Static Files
echo -e "${YELLOW}Test 4: Static CSS/JS Files${NC}"
css_response=$(curl -s -w "%{http_code}" "$RENDER_URL/static/css/style.css" -o /dev/null)
js_response=$(curl -s -w "%{http_code}" "$RENDER_URL/static/js/main.js" -o /dev/null)

if [ $css_response -eq 200 ]; then
    echo -e "${GREEN}✅ CSS files loading (200)${NC}"
else
    echo -e "${RED}❌ CSS files failed ($css_response)${NC}"
fi

if [ $js_response -eq 200 ]; then
    echo -e "${GREEN}✅ JS files loading (200)${NC}"
else
    echo -e "${RED}❌ JS files failed ($js_response)${NC}"
fi
echo ""

# Summary
echo -e "${YELLOW}📊 Test Summary${NC}"
echo "- Health Check: $([ $response -eq 200 ] && echo "✅" || echo "❌")"
echo "- Dashboard: $([ $response -eq 200 ] && echo "✅" || echo "❌")"
echo "- API Prediction: $([ $response -eq 200 ] && echo "✅" || echo "❌")"
echo "- Static Files: $([ $css_response -eq 200 ] && [ $js_response -eq 200 ] && echo "✅" || echo "❌")"
echo ""

if [ $response -eq 200 ]; then
    echo -e "${GREEN}🎉 Deployment appears to be working correctly!${NC}"
    echo -e "${YELLOW}Next step: Update iOS app API URLs to use $RENDER_URL${NC}"
else
    echo -e "${RED}⚠️  Some issues detected. Check Render logs for details.${NC}"
fi

# Cleanup
rm -f /tmp/health_response.txt /tmp/dashboard_response.txt /tmp/prediction_response.txt
