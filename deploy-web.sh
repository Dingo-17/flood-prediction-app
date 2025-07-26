#!/bin/bash

# 🚀 Deployment Script for Bangladesh Flood Prediction System

echo "🚀 Deploying Bangladesh Flood Prediction System..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Function to deploy to Heroku
deploy_heroku() {
    echo "📡 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI not found. Install from https://devcenter.heroku.com/articles/heroku-cli"
        return 1
    fi
    
    # Create Heroku app if it doesn't exist
    read -p "Enter Heroku app name (or press Enter for auto-generated): " app_name
    
    if [ -z "$app_name" ]; then
        heroku create
    else
        heroku create $app_name
    fi
    
    # Set environment variables
    echo "Setting environment variables..."
    read -p "Enter OpenWeatherMap API key: " api_key
    heroku config:set OPENWEATHER_API_KEY="$api_key"
    
    read -p "Enter Telegram Bot Token (optional): " bot_token
    if [ ! -z "$bot_token" ]; then
        heroku config:set TELEGRAM_BOT_TOKEN="$bot_token"
    fi
    
    # Deploy
    git add .
    git commit -m "Deploy flood prediction system"
    git push heroku main
    
    print_status "Heroku deployment complete!"
    heroku open
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found. Install from https://railway.app/cli"
        return 1
    fi
    
    railway login
    railway init
    railway up
    
    print_status "Railway deployment complete!"
}

# Function to deploy to Render
deploy_render() {
    echo "🎨 Deploying to Render..."
    print_warning "Please follow these steps:"
    echo "1. Go to https://render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new Web Service"
    echo "4. Use these settings:"
    echo "   - Build Command: pip install -r requirements-deploy.txt"
    echo "   - Start Command: gunicorn app:app --bind 0.0.0.0:\$PORT"
    echo "   - Environment: Python 3"
    echo "5. Add environment variables from .env.example"
}

# Function to build Docker image
deploy_docker() {
    echo "🐳 Building Docker image..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Install from https://docker.com"
        return 1
    fi
    
    # Build image
    docker build -t bangladesh-flood-prediction .
    
    # Run container
    echo "Starting container on port 8080..."
    docker run -d -p 8080:8080 --name flood-prediction bangladesh-flood-prediction
    
    print_status "Docker deployment complete!"
    echo "🌐 Access your app at: http://localhost:8080"
}

# Function to deploy locally with production server
deploy_local() {
    echo "🏠 Setting up local production deployment..."
    
    # Install production dependencies
    pip3 install -r requirements-deploy.txt
    
    # Create systemd service (Linux only)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        create_systemd_service
    fi
    
    # Start with gunicorn
    echo "Starting production server..."
    gunicorn app:app --bind 0.0.0.0:8080 --workers 2 --daemon
    
    print_status "Local production deployment complete!"
    echo "🌐 Access your app at: http://localhost:8080"
}

# Create systemd service for Linux
create_systemd_service() {
    SERVICE_FILE="/etc/systemd/system/flood-prediction.service"
    CURRENT_DIR=$(pwd)
    
    sudo tee $SERVICE_FILE > /dev/null <<EOL
[Unit]
Description=Bangladesh Flood Prediction System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 -m gunicorn app:app --bind 0.0.0.0:8080 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

    sudo systemctl daemon-reload
    sudo systemctl enable flood-prediction
    sudo systemctl start flood-prediction
    
    print_status "Systemd service created and started"
}

# Main menu
echo "Choose deployment option:"
echo "1) Heroku (Free tier available)"
echo "2) Railway (Free tier available)" 
echo "3) Render (Free tier available)"
echo "4) Docker (Local/VPS)"
echo "5) Local Production Server"
echo "6) Show deployment guide"

read -p "Enter your choice (1-6): " choice

case $choice in
    1) deploy_heroku ;;
    2) deploy_railway ;;
    3) deploy_render ;;
    4) deploy_docker ;;
    5) deploy_local ;;
    6) cat << 'EOF'
📖 Deployment Guide:

🌐 Cloud Platforms (Recommended):
• Heroku: Easy deployment, free tier available
• Railway: Modern platform, generous free tier  
• Render: Good free tier, automatic deployments
• Vercel: Good for frontend, limited backend support

🐳 Docker:
• Build: docker build -t flood-prediction .
• Run: docker run -p 8080:8080 flood-prediction

🏠 Local/VPS:
• Use gunicorn: gunicorn app:app --bind 0.0.0.0:8080
• Use waitress: waitress-serve --host=0.0.0.0 --port=8080 app:app

📋 Before Deployment:
1. Update API keys in environment variables
2. Test locally first
3. Check requirements-deploy.txt
4. Set up monitoring and logging

EOF
        ;;
    *) print_error "Invalid choice" ;;
esac
