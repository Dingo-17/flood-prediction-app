#!/bin/bash

# iOS Production Build Script for Flood Prediction App
# This script prepares and builds the iOS app for App Store submission

echo "🚀 Building Flood Prediction App for Production..."

# Change to the iOS app directory
cd /Users/digantohaque/python/flood-ios-app

echo "📱 Step 1: Verify production configuration..."

# Check if API is set to production
if grep -q "ENV: 'production'" www/js/app.js; then
    echo "✅ API configured for production"
else
    echo "❌ API not configured for production"
    echo "Please update ENV to 'production' in www/js/app.js"
    exit 1
fi

echo "📱 Step 2: Installing/updating dependencies..."
npm install

echo "📱 Step 3: Building web assets..."
# Since this is a static app, we just need to ensure files are ready
echo "✅ Web assets ready"

echo "📱 Step 4: Syncing with Capacitor..."
npx cap sync ios

echo "📱 Step 5: Opening Xcode for final build..."
echo ""
echo "🎯 NEXT STEPS IN XCODE:"
echo "1. Select 'Any iOS Device (arm64)' as build target"
echo "2. Go to Product → Archive"
echo "3. Once archived, click 'Distribute App'"
echo "4. Choose 'App Store Connect'"
echo "5. Follow the upload process"
echo ""
echo "📋 BEFORE SUBMITTING TO APP STORE:"
echo "1. Add app icons (1024x1024 for App Store)"
echo "2. Create screenshots for different device sizes"
echo "3. Fill out App Store Connect metadata"
echo "4. Set up privacy policy URL"
echo "5. Configure app pricing and availability"
echo ""
echo "🔗 Backend URL: https://ai-flood-prediction-system.onrender.com"
echo ""

# Open Xcode
npx cap open ios

echo "✅ Production build process initiated!"
echo "📱 The iOS project is now open in Xcode"
