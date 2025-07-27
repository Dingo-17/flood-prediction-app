#!/bin/bash

# Render.com Build Script for Flood Prediction System
echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python packages from requirements-production.txt..."
pip install -r requirements-production.txt

echo "✅ Build completed successfully!"

# List installed packages for verification
echo "📋 Installed packages:"
pip list | grep -E "(flask|numpy|pandas|scikit-learn|requests|joblib|gunicorn)"

echo "🎯 Ready for deployment!"
