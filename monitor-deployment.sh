#!/bin/bash
echo "🕐 MONITORING DEPLOYMENT PROGRESS"
echo "================================="
echo ""
echo "Checking deployment status every 30 seconds..."
echo "Press Ctrl+C to stop monitoring"
echo ""

count=1
while true; do
    echo "[$count] $(date '+%H:%M:%S') - Testing deployment..."
    
    response=$(curl -s -w "%{http_code}" https://ai-flood-prediction-system.onrender.com/)
    status_code="${response: -3}"
    content="${response%???}"
    
    if [ "$status_code" = "200" ]; then
        echo "🎉 SUCCESS! Deployment is now LIVE!"
        echo "✅ Status Code: $status_code"
        echo "📄 Response: $content" | head -3
        echo ""
        echo "🚀 NEXT STEPS:"
        echo "1. Run: ./build-production.sh (to build iOS app)"
        echo "2. Submit to App Store"
        echo ""
        break
    else
        echo "   ⏳ Still deploying... Status: $status_code"
    fi
    
    echo ""
    sleep 30
    count=$((count + 1))
    
    # Stop after 20 minutes (40 checks)
    if [ $count -gt 40 ]; then
        echo "⚠️ Deployment taking longer than expected."
        echo "🔧 Check Render dashboard logs for issues."
        break
    fi
done
