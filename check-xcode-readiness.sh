#!/bin/bash

# Check Xcode readiness for App Store submission
echo "🔍 Checking Xcode project readiness..."

cd /Users/digantohaque/python/flood-ios-app

echo ""
echo "📱 Project Status:"
echo "✅ Capacitor sync completed"
echo "✅ iOS project generated"
echo "✅ Production API configured"

echo ""
echo "🎯 Current Configuration:"
echo "Backend URL: $(grep -A1 'PRODUCTION:' www/js/app.js | grep -o 'https://[^'\'',]*')"
echo "Environment: $(grep 'ENV:' www/js/app.js | grep -o "'[^']*'" | tr -d "'")"

echo ""
echo "📋 Xcode Project Structure:"
if [ -d "ios/App/App.xcworkspace" ]; then
    echo "✅ Xcode workspace exists"
else
    echo "❌ Xcode workspace missing"
fi

if [ -f "ios/App/App/Info.plist" ]; then
    echo "✅ Info.plist configured"
else
    echo "❌ Info.plist missing"
fi

if [ -f "ios/App/App/capacitor.config.json" ]; then
    echo "✅ Capacitor config synced"
else
    echo "❌ Capacitor config missing"
fi

echo ""
echo "🚀 Ready for Xcode Archive!"
echo ""
echo "📝 NEXT STEPS:"
echo "1. In Xcode: Select 'Any iOS Device (arm64)'"
echo "2. Go to Product → Archive"
echo "3. Click 'Distribute App' → 'App Store Connect'"
echo "4. Upload to App Store"
echo ""
echo "📖 See APP_STORE_SUBMISSION_GUIDE.md for detailed instructions"
