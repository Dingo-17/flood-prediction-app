from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
LOCATIONS = {
    'Dhaka': (23.8103, 90.4125),
    'Sylhet': (24.8949, 91.8687),
    'Rangpur': (25.7439, 89.2752),
    'Bahadurabad': (25.1906, 89.7006),
    'Chittagong': (22.3569, 91.7832)
}

FLOOD_THRESHOLDS = {
    'Dhaka': 5.5,
    'Sylhet': 6.0,
    'Rangpur': 4.8,
    'Bahadurabad': 7.2,
    'Chittagong': 3.5
}

def simulate_rainfall_data(location, days=7):
    """Simulate rainfall data for demonstration"""
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    dates.reverse()
    
    # Simulate realistic rainfall patterns
    np.random.seed(hash(location) % 1000)
    rainfall = np.random.gamma(2, 3, days)
    rainfall = np.maximum(rainfall, 0)
    
    return [{
        'date': dates[i],
        'rainfall': float(rainfall[i]),
        'water_level': float(4.0 + rainfall[i] * 0.1 + np.random.normal(0, 0.3))
    } for i in range(days)]

def predict_flood_risk(location):
    """Simple flood prediction based on rainfall and water level"""
    data = simulate_rainfall_data(location)
    latest = data[-1]
    
    # Simple rule-based prediction
    water_level = latest['water_level']
    rainfall = latest['rainfall']
    threshold = FLOOD_THRESHOLDS[location]
    
    # Risk calculation
    risk_score = (water_level / threshold) * 0.7 + (rainfall / 20.0) * 0.3
    flood_probability = min(max(risk_score, 0.0), 1.0)
    
    return {
        'location': location,
        'current_water_level': water_level,
        'flood_threshold': threshold,
        'recent_rainfall': rainfall,
        'flood_probability': flood_probability,
        'flood_risk': 'HIGH' if flood_probability > 0.6 else 'MEDIUM' if flood_probability > 0.3 else 'LOW',
        'prediction': flood_probability > 0.6,
        'last_updated': datetime.now().isoformat()
    }

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/locations')
def get_locations():
    """Get all monitored locations"""
    return jsonify(list(LOCATIONS.keys()))

@app.route('/api/predict/<location>')
def predict_location(location):
    """Get flood prediction for specific location"""
    if location not in LOCATIONS:
        return jsonify({'error': 'Location not found'}), 404
    
    try:
        prediction = predict_flood_risk(location)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-all')
def predict_all_locations():
    """Get flood predictions for all locations"""
    predictions = []
    for location in LOCATIONS:
        try:
            prediction = predict_flood_risk(location)
            predictions.append(prediction)
        except Exception as e:
            predictions.append({
                'location': location,
                'error': str(e)
            })
    
    return jsonify(predictions)

@app.route('/api/rainfall/<location>')
def get_rainfall_data(location):
    """Get rainfall history for location"""
    if location not in LOCATIONS:
        return jsonify({'error': 'Location not found'}), 404
    
    try:
        data = simulate_rainfall_data(location, days=30)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def system_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'locations_monitored': len(LOCATIONS),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
