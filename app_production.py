from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import requests

# Initialize Flask app with minimal dependencies for production
app = Flask(__name__)
CORS(app)

# Simple in-memory data for locations
LOCATIONS = {
    'Dhaka': {
        'lat': 23.8103,
        'lon': 90.4125,
        'elevation': 8.0,
        'river_distance': 2.5,
        'drainage_quality': 0.6,
        'population': 9500000,
        'flood_threshold': 5.5
    },
    'Sylhet': {
        'lat': 24.8949,
        'lon': 91.8687,
        'elevation': 34.0,
        'river_distance': 1.2,
        'drainage_quality': 0.4,
        'population': 500000,
        'flood_threshold': 6.0
    },
    'Rangpur': {
        'lat': 25.7439,
        'lon': 89.2752,
        'elevation': 68.0,
        'river_distance': 5.8,
        'drainage_quality': 0.5,
        'population': 300000,
        'flood_threshold': 4.8
    },
    'Bahadurabad': {
        'lat': 25.1906,
        'lon': 89.7006,
        'elevation': 18.0,
        'river_distance': 0.5,
        'drainage_quality': 0.3,
        'population': 50000,
        'flood_threshold': 7.2
    },
    'Chittagong': {
        'lat': 22.3569,
        'lon': 91.7832,
        'elevation': 9.0,
        'river_distance': 4.2,
        'drainage_quality': 0.7,
        'population': 2500000,
        'flood_threshold': 3.5
    }
}

def simulate_current_conditions(location_name):
    """Simulate current weather and water conditions"""
    np.random.seed(hash(location_name + str(datetime.now().hour)) % 2**32)
    
    # Base conditions influenced by location characteristics
    location = LOCATIONS.get(location_name, LOCATIONS['Dhaka'])
    elevation = location['elevation']
    
    # Simulate realistic conditions
    current_rainfall = max(0, np.random.gamma(2, 3) * (50 - elevation) / 50)
    water_level = location['flood_threshold'] * (0.3 + np.random.random() * 0.8)
    
    # Add some seasonal variation (July is monsoon season)
    seasonal_factor = 1.8  # Higher in monsoon
    current_rainfall *= seasonal_factor
    
    return {
        'rainfall_1h': round(current_rainfall, 1),
        'rainfall_24h': round(current_rainfall * 8 + np.random.gamma(1.5, 4), 1),
        'water_level': round(water_level, 2),
        'temperature': round(28 + np.random.normal(0, 3), 1),
        'humidity': round(75 + np.random.normal(0, 10), 1),
        'timestamp': datetime.now().isoformat()
    }

def calculate_flood_risk(location_name, conditions):
    """Calculate flood risk using simplified model"""
    if location_name not in LOCATIONS:
        return {'risk_level': 'unknown', 'risk_percentage': 0}
    
    location = LOCATIONS[location_name]
    
    # Simple risk calculation based on multiple factors
    rainfall_factor = min(1.0, conditions['rainfall_24h'] / 50.0)
    water_level_factor = conditions['water_level'] / location['flood_threshold']
    drainage_factor = 1.0 - location['drainage_quality']
    elevation_factor = max(0, (20 - location['elevation']) / 20)
    
    # Weighted risk calculation
    risk_score = (
        rainfall_factor * 0.4 +
        water_level_factor * 0.3 +
        drainage_factor * 0.2 +
        elevation_factor * 0.1
    )
    
    risk_percentage = min(100, risk_score * 100)
    
    # Determine risk level
    if risk_percentage < 20:
        risk_level = 'Low'
        alert_color = 'green'
    elif risk_percentage < 50:
        risk_level = 'Moderate'
        alert_color = 'yellow'
    elif risk_percentage < 80:
        risk_level = 'High'
        alert_color = 'orange'
    else:
        risk_level = 'Critical'
        alert_color = 'red'
    
    return {
        'risk_level': risk_level,
        'risk_percentage': round(risk_percentage, 1),
        'alert_color': alert_color,
        'factors': {
            'rainfall_impact': round(rainfall_factor * 100, 1),
            'water_level_impact': round(water_level_factor * 100, 1),
            'drainage_impact': round(drainage_factor * 100, 1),
            'elevation_impact': round(elevation_factor * 100, 1)
        }
    }

@app.route('/')
def dashboard():
    """Main dashboard page - API status"""
    return jsonify({
        "message": "AI Flood Prediction System API",
        "status": "live",
        "version": "1.0.0",
        "deployment": "render-production",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/api/locations",
            "/api/predict/<location>",
            "/api/predict/coordinates/<lat>/<lon>",
            "/api/history/<location>",
            "/api/alerts",
            "/api/status"
        ]
    })

@app.route('/api/locations')
def get_locations():
    """Get all monitored locations"""
    locations_data = []
    for name, data in LOCATIONS.items():
        conditions = simulate_current_conditions(name)
        risk = calculate_flood_risk(name, conditions)
        
        locations_data.append({
            'location_name': name,
            'latitude': data['lat'],
            'longitude': data['lon'],
            'elevation': data['elevation'],
            'population': data['population'],
            'current_conditions': conditions,
            'flood_risk': risk,
            'last_updated': datetime.now().isoformat()
        })
    
    return jsonify({
        'locations': locations_data,
        'total_count': len(locations_data),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predict/<location>')
def predict_location(location):
    """Get flood prediction for specific location"""
    if location not in LOCATIONS:
        return jsonify({'error': 'Location not found'}), 404
    
    conditions = simulate_current_conditions(location)
    risk = calculate_flood_risk(location, conditions)
    location_data = LOCATIONS[location]
    
    # Generate 7-day forecast
    forecast = []
    for i in range(7):
        future_date = datetime.now() + timedelta(days=i)
        # Simulate future conditions with some variation
        np.random.seed(hash(location + str(future_date.day)) % 2**32)
        future_rainfall = max(0, np.random.gamma(1.8, 4))
        future_risk = calculate_flood_risk(location, {
            'rainfall_24h': future_rainfall,
            'water_level': location_data['flood_threshold'] * (0.4 + np.random.random() * 0.6),
            'temperature': 28,
            'humidity': 75
        })
        
        forecast.append({
            'date': future_date.strftime('%Y-%m-%d'),
            'predicted_rainfall': round(future_rainfall, 1),
            'flood_risk': future_risk['risk_level'],
            'risk_percentage': future_risk['risk_percentage']
        })
    
    return jsonify({
        'location': location,
        'coordinates': {'lat': location_data['lat'], 'lon': location_data['lon']},
        'current_conditions': conditions,
        'flood_risk': risk,
        '7_day_forecast': forecast,
        'recommendations': generate_recommendations(risk['risk_level']),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predict/coordinates/<float:lat>/<float:lon>')
def predict_coordinates(lat, lon):
    """Get flood prediction for specific coordinates"""
    # Find nearest location
    min_distance = float('inf')
    nearest_location = 'Dhaka'
    
    for name, data in LOCATIONS.items():
        distance = ((lat - data['lat'])**2 + (lon - data['lon'])**2)**0.5
        if distance < min_distance:
            min_distance = distance
            nearest_location = name
    
    # Get prediction for nearest location but return with provided coordinates
    conditions = simulate_current_conditions(nearest_location)
    risk = calculate_flood_risk(nearest_location, conditions)
    
    return jsonify({
        'coordinates': {'lat': lat, 'lon': lon},
        'nearest_monitoring_station': nearest_location,
        'distance_km': round(min_distance * 111.32, 2),  # Convert to km
        'current_conditions': conditions,
        'flood_risk': risk,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/history/<location>')
def get_history(location):
    """Get historical flood data for location"""
    if location not in LOCATIONS:
        return jsonify({'error': 'Location not found'}), 404
    
    # Generate 30 days of historical data
    history = []
    for i in range(30, 0, -1):
        past_date = datetime.now() - timedelta(days=i)
        np.random.seed(hash(location + str(past_date.day)) % 2**32)
        
        past_rainfall = max(0, np.random.gamma(1.5, 3))
        past_conditions = {
            'rainfall_24h': past_rainfall,
            'water_level': LOCATIONS[location]['flood_threshold'] * (0.3 + np.random.random() * 0.7),
            'temperature': 28,
            'humidity': 75
        }
        past_risk = calculate_flood_risk(location, past_conditions)
        
        history.append({
            'date': past_date.strftime('%Y-%m-%d'),
            'rainfall': past_rainfall,
            'water_level': past_conditions['water_level'],
            'flood_risk': past_risk['risk_level'],
            'risk_percentage': past_risk['risk_percentage']
        })
    
    return jsonify({
        'location': location,
        'history': history,
        'period': '30_days',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/alerts')
def get_alerts():
    """Get current flood alerts for all locations"""
    alerts = []
    
    for location_name in LOCATIONS.keys():
        conditions = simulate_current_conditions(location_name)
        risk = calculate_flood_risk(location_name, conditions)
        
        if risk['risk_percentage'] > 30:  # Only show alerts for moderate+ risk
            alert_level = 'WARNING' if risk['risk_percentage'] > 70 else 'WATCH'
            alerts.append({
                'location': location_name,
                'alert_level': alert_level,
                'risk_percentage': risk['risk_percentage'],
                'message': f"Flood {alert_level.lower()} issued for {location_name}. Current risk: {risk['risk_level']}",
                'issued_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=6)).isoformat()
            })
    
    return jsonify({
        'alerts': alerts,
        'total_active_alerts': len(alerts),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def system_status():
    """Get system status"""
    return jsonify({
        'system_status': 'operational',
        'api_version': '1.0.0',
        'monitored_locations': len(LOCATIONS),
        'data_sources': ['synthetic_weather_data', 'elevation_models'],
        'model_status': 'simplified_production_model',
        'last_updated': datetime.now().isoformat(),
        'uptime': 'live',
        'database_status': 'in_memory'
    })

def generate_recommendations(risk_level):
    """Generate safety recommendations based on risk level"""
    recommendations = {
        'Low': [
            "Monitor weather forecasts regularly",
            "Keep emergency supplies accessible",
            "Stay informed about local conditions"
        ],
        'Moderate': [
            "Avoid low-lying areas if possible",
            "Prepare emergency kit with essentials",
            "Monitor local authorities for updates",
            "Consider alternative travel routes"
        ],
        'High': [
            "Avoid unnecessary travel",
            "Move to higher ground if in flood-prone areas",
            "Keep emergency contacts readily available",
            "Monitor official warnings closely",
            "Prepare for possible evacuation"
        ],
        'Critical': [
            "Evacuate immediately if advised by authorities",
            "Move to highest available ground",
            "Call emergency services if in danger",
            "Do not attempt to drive through flooded roads",
            "Stay tuned to emergency broadcasts"
        ]
    }
    
    return recommendations.get(risk_level, recommendations['Low'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"🚀 Starting AI Flood Prediction System on port {port}")
    print(f"🌊 Monitoring {len(LOCATIONS)} locations in Bangladesh")
    app.run(debug=debug, host='0.0.0.0', port=port)
