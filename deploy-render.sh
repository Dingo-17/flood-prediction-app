#!/bin/bash

# 🎨 Render Deployment Script for AI Flood Prediction System
# Run this script to prepare your flood prediction system for Render deployment

set -e  # Exit on any error

echo "🌊 Preparing Render deployment for AI Flood Prediction System..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: AI Flood Prediction System for Render"
fi

# Check if we have a GitHub remote
if ! git remote | grep -q origin; then
    echo "🔗 Setting up GitHub repository..."
    echo ""
    echo "📋 RENDER DEPLOYMENT INSTRUCTIONS:"
    echo "=================================="
    echo ""
    echo "1. 📱 Create a GitHub repository:"
    echo "   - Go to https://github.com/new"
    echo "   - Create a new repository (e.g., 'ai-flood-prediction')"
    echo "   - Don't initialize with README (we already have files)"
    echo ""
    echo "2. 🔗 Connect your local repository:"
    read -p "   Enter your GitHub repository URL (e.g., https://github.com/username/ai-flood-prediction.git): " GITHUB_URL
    
    if [ ! -z "$GITHUB_URL" ]; then
        git remote add origin $GITHUB_URL
        echo "   ✅ GitHub remote added!"
        
        # Push to GitHub
        echo "📤 Pushing code to GitHub..."
        git branch -M main
        git push -u origin main
        echo "   ✅ Code pushed to GitHub!"
    else
        echo "   ⏭️ Skipping GitHub setup - you can do this manually later"
    fi
fi

echo ""
echo "3. 🎨 Deploy on Render:"
echo "   ========================"
echo "   - Go to https://render.com"
echo "   - Click 'New +' → 'Web Service'"
echo "   - Connect your GitHub repository"
echo "   - Use these settings:"
echo ""
echo "   📋 BUILD SETTINGS:"
echo "   ------------------"
echo "   • Name: ai-flood-prediction-system"
echo "   • Environment: Python 3"
echo "   • Build Command: pip install -r requirements-production.txt"
echo "   • Start Command: python app.py"
echo "   • Instance Type: Free (or upgrade as needed)"
echo ""
echo "   ⚙️ ENVIRONMENT VARIABLES:"
echo "   -------------------------"
echo "   Add these in the Render dashboard:"
echo "   • FLASK_ENV = production"
echo "   • PORT = 10000 (Render's default)"
echo ""
echo "   🔑 OPTIONAL API KEYS (add these for full functionality):"
echo "   --------------------------------------------------------"
echo "   • OPENWEATHER_API_KEY = your_openweather_api_key"
echo "   • TELEGRAM_BOT_TOKEN = your_telegram_bot_token"
echo "   • TELEGRAM_CHAT_ID = your_telegram_chat_id"
echo "   • EMAIL_USERNAME = your_email@gmail.com"
echo "   • EMAIL_PASSWORD = your_app_password"
echo ""

# Update app.py for Render's port handling
echo "🔧 Configuring app for Render deployment..."
if ! grep -q "int(os.environ.get('PORT', 10000))" app.py; then
    # Update the port configuration for Render
    python3 -c "
import re
with open('app.py', 'r') as f:
    content = f.read()

# Update the port line to use Render's default port 10000
content = re.sub(
    r'port = int\(os\.environ\.get\([^)]+\)\)',
    'port = int(os.environ.get(\"PORT\", 10000))',
    content
)

with open('app.py', 'w') as f:
    f.write(content)
"
    echo "   ✅ App configured for Render (port 10000)"
fi

# Ensure we have the production requirements file
if [ ! -f "requirements-production.txt" ]; then
    echo "📦 Creating production requirements file..."
    cat > requirements-production.txt << EOF
flask==3.1.1
flask-cors==6.0.1
scikit-learn==1.7.1
pandas==2.3.1
numpy==2.2.6
requests==2.32.4
joblib==1.5.1
gunicorn==23.0.0
python-dotenv==1.0.1
EOF
    echo "   ✅ Production requirements created"
fi

# Create a render.yaml file for easy deployment
echo "📄 Creating render.yaml deployment configuration..."
cat > render.yaml << EOF
services:
  - type: web
    name: ai-flood-prediction-system
    env: python
    buildCommand: pip install -r requirements-production.txt
    startCommand: python app.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 10000
EOF
echo "   ✅ render.yaml created"

echo ""
echo "4. 🚀 Final Steps:"
echo "   ==============="
echo "   - Click 'Create Web Service' on Render"
echo "   - Wait for deployment (usually 2-3 minutes)"
echo "   - Test your live app!"
echo ""
echo "5. 📊 Your App Endpoints:"
echo "   ====================="
echo "   Once deployed, your app will be available at:"
echo "   • Dashboard: https://your-app-name.onrender.com"
echo "   • API Status: https://your-app-name.onrender.com/api/status"
echo "   • Predictions: https://your-app-name.onrender.com/api/predict/Dhaka"
echo "   • Locations: https://your-app-name.onrender.com/api/locations"
echo ""
echo "✅ Render deployment preparation complete!"
echo ""
echo "💡 NEXT STEPS:"
echo "   1. Complete the GitHub setup if not done"
echo "   2. Go to https://render.com and create your web service"
echo "   3. Connect your GitHub repository"
echo "   4. Use the settings provided above"
echo "   5. Add environment variables in Render dashboard"
echo "   6. Deploy and test!"
echo ""
echo "🎉 Your AI Flood Prediction System will be live in minutes!"
