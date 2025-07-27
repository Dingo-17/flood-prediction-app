#!/bin/bash

# Render.com Startup Script for Flask Application
echo "🚀 Starting Flood Prediction System..."

# Set environment variables
export FLASK_ENV=production
export PYTHONPATH=/opt/render/project/src

# Start the Flask application
echo "📱 Starting Flask app on port ${PORT:-10000}..."
python app.py
