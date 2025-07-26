#!/bin/bash

# 🚀 Quick Deploy Script for Flood Prediction System
# Usage: ./quick_deploy.sh [platform]
# Platforms: heroku, railway, render, docker, vercel

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}🌊 Bangladesh Flood Prediction System${NC}"
    echo -e "${BLUE}====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_dependencies() {
    local platform=$1
    case $platform in
        "heroku")
            if ! command -v heroku &> /dev/null; then
                print_error "Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli"
                exit 1
            fi
            ;;
        "railway")
            if ! command -v railway &> /dev/null; then
                print_error "Railway CLI not found. Install from: https://docs.railway.app/deploy/cli"
                exit 1
            fi
            ;;
        "docker")
            if ! command -v docker &> /dev/null; then
                print_error "Docker not found. Install from: https://docs.docker.com/get-docker/"
                exit 1
            fi
            ;;
        "vercel")
            if ! command -v vercel &> /dev/null; then
                print_error "Vercel CLI not found. Install with: npm i -g vercel"
                exit 1
            fi
            ;;
    esac
}

deploy_heroku() {
    print_info "Deploying to Heroku..."
    
    # Check if logged in
    if ! heroku auth:whoami &> /dev/null; then
        print_info "Please login to Heroku:"
        heroku login
    fi
    
    # Get app name
    read -p "Enter your Heroku app name (or press Enter for auto-generated): " app_name
    
    if [ -z "$app_name" ]; then
        app_name="flood-prediction-$(date +%s)"
    fi
    
    # Create app
    print_info "Creating Heroku app: $app_name"
    heroku create $app_name || print_warning "App might already exist"
    
    # Set environment variables
    print_info "Setting environment variables..."
    heroku config:set FLASK_ENV=production -a $app_name
    heroku config:set PORT=\$PORT -a $app_name
    
    # Optional API keys
    read -p "Enter OpenWeatherMap API key (optional): " weather_key
    if [ ! -z "$weather_key" ]; then
        heroku config:set OPENWEATHER_API_KEY=$weather_key -a $app_name
    fi
    
    # Git setup and deploy
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial deployment"
    fi
    
    heroku git:remote -a $app_name
    
    print_info "Deploying to Heroku..."
    git push heroku main || git push heroku master
    
    # Open app
    heroku open -a $app_name
    
    print_success "Deployed to Heroku! App URL: https://$app_name.herokuapp.com"
}

deploy_railway() {
    print_info "Deploying to Railway..."
    
    railway login
    railway init
    railway up
    
    print_success "Deployed to Railway! Check your Railway dashboard for the URL."
}

deploy_docker() {
    print_info "Building and running with Docker..."
    
    # Build image
    docker build -t flood-prediction-system .
    
    # Stop any existing container
    docker stop flood-prediction-container 2>/dev/null || true
    docker rm flood-prediction-container 2>/dev/null || true
    
    # Run container
    docker run -d --name flood-prediction-container -p 8080:8080 flood-prediction-system
    
    print_success "Docker container running at http://localhost:8080"
}

deploy_render() {
    print_info "Setting up Render deployment..."
    print_info "Please follow these steps:"
    echo "1. Go to https://render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new Web Service"
    echo "4. Use these settings:"
    echo "   - Build Command: pip install -r requirements-deploy.txt"
    echo "   - Start Command: python simple_app.py"
    echo "5. Set environment variables in Render dashboard"
    echo ""
    print_success "Render setup instructions provided!"
}

deploy_vercel() {
    print_info "Deploying to Vercel..."
    vercel
    print_success "Deployed to Vercel!"
}

main() {
    print_header
    
    PLATFORM=${1:-""}
    
    if [ -z "$PLATFORM" ]; then
        echo "Available platforms:"
        echo "1. heroku   - Heroku Platform"
        echo "2. railway  - Railway Platform" 
        echo "3. docker   - Docker Container"
        echo "4. render   - Render Platform"
        echo "5. vercel   - Vercel Platform"
        echo ""
        read -p "Choose platform (1-5): " choice
        
        case $choice in
            1) PLATFORM="heroku" ;;
            2) PLATFORM="railway" ;;
            3) PLATFORM="docker" ;;
            4) PLATFORM="render" ;;
            5) PLATFORM="vercel" ;;
            *) print_error "Invalid choice"; exit 1 ;;
        esac
    fi
    
    check_dependencies $PLATFORM
    
    case $PLATFORM in
        "heroku") deploy_heroku ;;
        "railway") deploy_railway ;;
        "docker") deploy_docker ;;
        "render") deploy_render ;;
        "vercel") deploy_vercel ;;
        *) print_error "Unknown platform: $PLATFORM" ;;
    esac
}

main "$@"
