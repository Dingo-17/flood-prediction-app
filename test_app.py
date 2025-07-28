from flask import Flask, jsonify
from flask_cors import CORS
import os

# Simple Flask app for testing deployment
app = Flask(__name__)
CORS(app)

@app.route('/')
def test_root():
    """Test root endpoint"""
    return jsonify({
        "message": "AI Flood Prediction System - Test Mode",
        "status": "live",
        "version": "1.0.0-test",
        "deployment": "render",
        "timestamp": "2025-07-28"
    })

@app.route('/api/locations')
def test_locations():
    """Test locations endpoint"""
    return jsonify({
        "locations": [
            {"name": "Dhaka", "lat": 23.8103, "lon": 90.4125, "status": "monitored"},
            {"name": "Sylhet", "lat": 24.8949, "lon": 91.8687, "status": "monitored"},
            {"name": "Rangpur", "lat": 25.7439, "lon": 89.2752, "status": "monitored"}
        ]
    })

@app.route('/api/status')
def test_status():
    """Test status endpoint"""
    return jsonify({
        "system": "operational",
        "models": "test_mode",
        "database": "connected",
        "api": "working"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"🚀 Starting test Flask app on port {port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
