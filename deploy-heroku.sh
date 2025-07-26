#!/bin/bash

# 🚀 Heroku Deployment Script for AI Flood Prediction System
# Run this script to deploy your flood prediction system to Heroku

set -e  # Exit on any error

echo "🌊 Starting Heroku deployment for AI Flood Prediction System..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please login to Heroku:"
    heroku login
fi

# Get app name from user
read -p "Enter your Heroku app name (e.g., my-flood-prediction): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ App name cannot be empty"
    exit 1
fi

echo "📱 Creating Heroku app: $APP_NAME"

# Create Heroku app
heroku create $APP_NAME || echo "App might already exist, continuing..."

# Set environment variables
echo "⚙️ Setting environment variables..."
heroku config:set FLASK_ENV=production --app $APP_NAME
heroku config:set PORT=8080 --app $APP_NAME

# Optional: Set API keys (user can do this later)
read -p "Enter OpenWeatherMap API key (or press Enter to skip): " WEATHER_API
if [ ! -z "$WEATHER_API" ]; then
    heroku config:set OPENWEATHER_API_KEY=$WEATHER_API --app $APP_NAME
fi

read -p "Enter Telegram Bot Token (or press Enter to skip): " TELEGRAM_TOKEN
if [ ! -z "$TELEGRAM_TOKEN" ]; then
    heroku config:set TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN --app $APP_NAME
fi

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: AI Flood Prediction System"
fi

# Add Heroku remote
echo "🔗 Adding Heroku remote..."
heroku git:remote -a $APP_NAME

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git push heroku main || git push heroku master

# Scale app
echo "📈 Scaling app..."
heroku ps:scale web=1 --app $APP_NAME

# Open app
echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📊 Dashboard: https://$APP_NAME.herokuapp.com"
echo "🔍 API Status: https://$APP_NAME.herokuapp.com/api/status"

# Show logs
read -p "View logs? (y/n): " view_logs
if [[ $view_logs =~ ^[Yy]$ ]]; then
    heroku logs --tail --app $APP_NAME
fi

echo "🎉 Deployment successful! Your AI Flood Prediction System is live!"
