#!/bin/bash
echo "🚀 DEPLOYMENT STATUS CHECK"
echo "=========================="
echo ""

# Quick test
echo "Testing backend..."
status=$(curl -s -o /dev/null -w "%{http_code}" https://ai-flood-prediction-system.onrender.com/)

if [ "$status" = "200" ]; then
    echo "✅ BACKEND IS LIVE!"
    echo "✅ Status: $status"
    echo "✅ Ready to build iOS app: ./build-production.sh"
elif [ "$status" = "404" ]; then
    echo "❌ BACKEND NOT READY"
    echo "❌ Status: 404 (Not Found)"
    echo "🔧 Fix needed: Follow manual setup in ../flood/deploy-fix-final.sh"
else
    echo "⚠️  BACKEND STATUS: $status"
    echo "🔧 Check Render dashboard for deployment status"
fi

echo ""
echo "🔍 For detailed testing: ./test-backend.sh"
echo "🔧 For deployment fix: ../flood/deploy-fix-final.sh"
