#!/bin/bash

# 🚄 Railway Deployment Script for AI Flood Prediction System
# Run this script to deploy your flood prediction system to Railway

set -e  # Exit on any error

echo "🌊 Starting Railway deployment for AI Flood Prediction System..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

# Initialize Railway project
echo "🚀 Initializing Railway project..."
railway init

# Set environment variables
echo "⚙️ Setting environment variables..."
railway variables set FLASK_ENV=production
railway variables set PORT=8080

# Optional: Set API keys
read -p "Enter OpenWeatherMap API key (or press Enter to skip): " WEATHER_API
if [ ! -z "$WEATHER_API" ]; then
    railway variables set OPENWEATHER_API_KEY=$WEATHER_API
fi

read -p "Enter Telegram Bot Token (or press Enter to skip): " TELEGRAM_TOKEN
if [ ! -z "$TELEGRAM_TOKEN" ]; then
    railway variables set TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN
fi

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Get deployment URL
DEPLOYMENT_URL=$(railway domain)

echo "✅ Deployment complete!"
echo "🌐 Your app is available at: $DEPLOYMENT_URL"
echo "📊 Dashboard: $DEPLOYMENT_URL"
echo "🔍 API Status: $DEPLOYMENT_URL/api/status"

echo "🎉 Railway deployment successful! Your AI Flood Prediction System is live!"
