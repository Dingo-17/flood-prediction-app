# Flood Prediction iOS App

A Capacitor-based iOS app for the Bangladesh Flood Prediction System.

## Features

- 🌊 Real-time flood risk prediction
- 📍 GPS location integration
- 🗺️ Interactive maps with Leaflet
- 📱 Native iOS performance
- 🔔 Local notifications for high-risk alerts
- 📊 Mobile-optimized interface

## Prerequisites

Before you begin, ensure you have:

1. **Node.js** (v16 or later)
2. **Xcode** (latest version) - for iOS development
3. **iOS Simulator** or physical iOS device
4. **Capacitor CLI** installed globally

## Setup Instructions

### 1. Install Dependencies

```bash
cd flood-ios-app
npm install
```

### 2. Install Capacitor CLI globally

```bash
npm install -g @capacitor/cli
```

### 3. Initialize iOS Platform

```bash
npx cap add ios
```

### 4. Update API Configuration

Edit `www/index.html` and update the `API_BASE_URL` constant to point to your deployed Flask API:

```javascript
const API_BASE_URL = 'https://your-flood-api.herokuapp.com';
```

### 5. Sync Web Assets

```bash
npx cap sync
```

### 6. Open in Xcode

```bash
npx cap open ios
```

This will open Xcode with your iOS project.

### 7. Configure iOS Settings

In Xcode:

1. **Set your Team**: Select your Apple Developer account in Project Settings > Signing & Capabilities
2. **Update Bundle Identifier**: Change `com.floodprediction.app` to your unique identifier
3. **Configure Permissions**: The app requests location permissions for GPS functionality

### 8. Run the App

- **iOS Simulator**: Click the "Run" button in Xcode
- **Physical Device**: Connect your iOS device and select it as a target, then click "Run"

## Project Structure

```
flood-ios-app/
├── capacitor.config.json    # Capacitor configuration
├── package.json            # Node.js dependencies
├── www/                    # Web assets
│   └── index.html         # Main app interface
└── ios/                   # Generated iOS project (after cap add ios)
```

## Key Features

### 📍 GPS Integration
- Uses Capacitor Geolocation plugin
- Automatically fills latitude/longitude fields
- Falls back to manual entry if location is unavailable

### 🗺️ Interactive Maps
- Leaflet.js integration for map display
- Shows prediction location with markers
- Responsive design for mobile devices

### 📱 Mobile-First Design
- Optimized for iOS devices
- Touch-friendly interface
- Safe area support for iPhone X and later

### 🔔 Notifications
- Local notifications for high flood risk alerts
- Can be extended for push notifications

## API Integration

The app expects your Flask API to have a `/predict` endpoint that accepts:

```json
{
  "latitude": 23.8103,
  "longitude": 90.4125,
  "rainfall_24h": 50.0,
  "water_level": 2.5,
  "river_discharge": 1500.0,
  "temperature": 28.0,
  "humidity": 75.0
}
```

And returns:

```json
{
  "flood_probability": 0.75,
  "risk_level": "high",
  "location": "Dhaka, Bangladesh"
}
```

## Deployment Options

### TestFlight (Recommended for Testing)
1. Archive your app in Xcode
2. Upload to App Store Connect
3. Distribute via TestFlight

### App Store
1. Complete app review requirements
2. Submit for App Store review
3. Publish when approved

## Troubleshooting

### Common Issues

1. **Location Permission Denied**
   - Ensure Info.plist includes location usage descriptions
   - Grant location permissions in iOS Settings

2. **API Connection Failed**
   - Verify your Flask API is deployed and accessible
   - Update API_BASE_URL in index.html
   - Check CORS settings on your Flask API

3. **Build Errors**
   - Clean and rebuild: Product > Clean Build Folder
   - Update Capacitor: `npm update @capacitor/core @capacitor/cli @capacitor/ios`

### Development Commands

```bash
# Sync changes after modifying web assets
npx cap sync

# Run on iOS simulator
npx cap run ios

# Open in Xcode
npx cap open ios

# Update Capacitor
npm update @capacitor/core @capacitor/cli @capacitor/ios
```

## Next Steps

1. **Deploy your Flask API** to a cloud service (Heroku, Railway, etc.)
2. **Update API_BASE_URL** in the HTML file
3. **Test on real devices** with actual GPS data
4. **Add push notifications** for real-time alerts
5. **Implement offline capabilities** for areas with poor connectivity
6. **Add more visualization features** like charts and historical data

## Support

For issues related to:
- **Capacitor**: [Capacitor Documentation](https://capacitorjs.com/docs)
- **iOS Development**: [Apple Developer Documentation](https://developer.apple.com/documentation/)
- **Xcode**: [Xcode Help](https://help.apple.com/xcode/)
