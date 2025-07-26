#!/bin/bash

# 🐳 Docker Deployment Script for AI Flood Prediction System
# Run this script to build and deploy using Docker

set -e  # Exit on any error

echo "🌊 Starting Docker deployment for AI Flood Prediction System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t flood-prediction-system .

# Get image ID
IMAGE_ID=$(docker images flood-prediction-system:latest -q)
echo "✅ Built image: $IMAGE_ID"

# Stop any existing container
echo "🛑 Stopping existing containers..."
docker stop flood-prediction-app 2>/dev/null || true
docker rm flood-prediction-app 2>/dev/null || true

# Run container
echo "🚀 Starting new container..."
docker run -d \
    --name flood-prediction-app \
    -p 8080:8080 \
    -e FLASK_ENV=production \
    -e PORT=8080 \
    flood-prediction-system

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 5

# Check if container is running
if docker ps | grep -q flood-prediction-app; then
    echo "✅ Container is running successfully!"
    echo "🌐 Your app is available at: http://localhost:8080"
    echo "📊 Dashboard: http://localhost:8080"
    echo "🔍 API Status: http://localhost:8080/api/status"
    
    # Show container logs
    echo "📄 Container logs:"
    docker logs flood-prediction-app
    
    echo ""
    echo "🎉 Docker deployment successful!"
    echo "💡 To view logs: docker logs -f flood-prediction-app"
    echo "💡 To stop: docker stop flood-prediction-app"
    echo "💡 To restart: docker start flood-prediction-app"
else
    echo "❌ Container failed to start. Checking logs..."
    docker logs flood-prediction-app
    exit 1
fi
