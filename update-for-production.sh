#!/bin/bash

# Update iOS app for production deployment
echo "🔧 Updating iOS app for production..."

# Get the production URL from user
read -p "Enter your Render URL (e.g., https://flood-prediction-bangladesh.onrender.com): " RENDER_URL

# Remove trailing slash if present
RENDER_URL=${RENDER_URL%/}

echo "📱 Updating API URLs in app.js..."

# Update the app.js file to use production URL
sed -i '' "s|http://192.168.1.164:10000|${RENDER_URL}|g" www/js/app.js

echo "✅ Updated app.js with production URL: ${RENDER_URL}"

# Sync changes to iOS
echo "🔄 Syncing changes to iOS..."
npx cap sync ios

echo "🎉 iOS app is now configured for production!"
echo ""
echo "Next steps:"
echo "1. Open Xcode: npx cap open ios"
echo "2. Archive for App Store: Product → Archive"
echo "3. Upload to App Store Connect"
echo ""
echo "Production URL: ${RENDER_URL}"
