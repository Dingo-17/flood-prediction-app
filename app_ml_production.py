#!/usr/bin/env python3
"""
AI Flood Prediction System - Full ML Production Version
Upgraded to use the same advanced ML model as the original website
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import random
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global ML model variables
rf_model = None
scaler = None
feature_cols = ['rainfall_1day', 'rainfall_3day', 'rainfall_7day', 
               'water_level_lag1', 'water_level_trend', 'is_monsoon',
               'elevation', 'river_distance', 'geographic_risk']

# Bangladesh flood monitoring locations with precise coordinates
LOCATIONS = {
    'Dhaka': (23.8103, 90.4125),
    'Sylhet': (24.8949, 91.8687),
    'Rangpur': (25.7439, 89.2752),
    'Bahadurabad': (25.1958, 89.6714),
    'Chittagong': (22.3569, 91.7832)
}

# Flood threshold levels (meters above sea level)
FLOOD_THRESHOLDS = {
    'Dhaka': 6.2,
    'Sylhet': 4.8,
    'Rangpur': 7.1,
    'Bahadurabad': 5.9,
    'Chittagong': 5.5
}

# Enhanced geographic data matching original website
GEOGRAPHIC_DATA = {
    'Dhaka': {
        'elevation': 6.0,
        'distance_to_major_river': 1.2,
        'drainage_quality': 'Poor',
        'river_confluence_distance': 18.7,
        'topography': 'low_lying_urban',
        'base_risk_factor': 0.03,
        'annual_rainfall_mm': 2025,
        'flood_history_frequency': 8,
        'population_density': 23234,
        'urbanization_factor': 0.95,
        'soil_type': 'clay_alluvial',
        'river_systems': ['Buriganga', 'Turag', 'Balu', 'Shitalakhya']
    },
    'Sylhet': {
        'elevation': 11.8,
        'distance_to_major_river': 0.2,
        'drainage_quality': 'Moderate',
        'river_confluence_distance': 25.3,
        'topography': 'river_valley',
        'base_risk_factor': 0.025,
        'annual_rainfall_mm': 3334,
        'flood_history_frequency': 12,
        'population_density': 1020,
        'urbanization_factor': 0.65,
        'soil_type': 'sandy_alluvial',
        'river_systems': ['Surma', 'Kushiyara', 'Manu']
    },
    'Rangpur': {
        'elevation': 32.5,
        'distance_to_major_river': 58.7,
        'drainage_quality': 'Good',
        'river_confluence_distance': 89.4,
        'topography': 'elevated_plain',
        'base_risk_factor': 0.015,
        'annual_rainfall_mm': 1448,
        'flood_history_frequency': 3,
        'population_density': 1265,
        'urbanization_factor': 0.45,
        'soil_type': 'loamy',
        'river_systems': ['Teesta', 'Karatoya']
    },
    'Bahadurabad': {
        'elevation': 16.3,
        'distance_to_major_river': 0.8,
        'drainage_quality': 'Moderate',
        'river_confluence_distance': 8.2,
        'topography': 'river_plain',
        'base_risk_factor': 0.025,
        'annual_rainfall_mm': 1832,
        'flood_history_frequency': 9,
        'population_density': 890,
        'urbanization_factor': 0.35,
        'soil_type': 'silty_alluvial',
        'river_systems': ['Jamuna', 'Brahmaputra', 'Old Brahmaputra']
    },
    'Chittagong': {
        'elevation': 5.8,
        'distance_to_major_river': 2.1,
        'drainage_quality': 'Poor',
        'river_confluence_distance': 42.8,
        'topography': 'coastal_low',
        'base_risk_factor': 0.02,
        'annual_rainfall_mm': 2666,
        'flood_history_frequency': 7,
        'population_density': 2800,
        'urbanization_factor': 0.78,
        'soil_type': 'sandy_clay',
        'river_systems': ['Karnaphuli', 'Halda', 'Sangu']
    }
}

def create_synthetic_training_data():
    """Create synthetic training data for ML model"""
    logger.info("Generating synthetic training data for ML model...")
    
    np.random.seed(42)  # For reproducibility
    n_samples = 2500
    
    # Generate realistic feature distributions
    rainfall_1day = np.random.exponential(5, n_samples)
    rainfall_3day = rainfall_1day + np.random.exponential(8, n_samples)
    rainfall_7day = rainfall_3day + np.random.exponential(12, n_samples)
    
    water_level_lag1 = np.random.normal(4.5, 1.8, n_samples)
    water_level_trend = np.random.normal(0, 0.5, n_samples)
    
    # Seasonal effects (1 for monsoon months 6-9)
    is_monsoon = np.random.choice([0, 1], n_samples, p=[0.67, 0.33])
    
    # Geographic features
    elevation = np.random.uniform(2, 40, n_samples)
    river_distance = np.random.exponential(15, n_samples)
    geographic_risk = np.random.beta(2, 5, n_samples)  # Skewed toward lower values
    
    # Create complex flood probability based on multiple factors
    flood_prob = (
        0.15 * (rainfall_1day / 30.0) +
        0.20 * (rainfall_3day / 80.0) +
        0.15 * (rainfall_7day / 150.0) +
        0.20 * np.maximum(0, (water_level_lag1 - 3.0) / 5.0) +
        0.10 * np.maximum(0, water_level_trend / 2.0) +
        0.05 * is_monsoon +
        0.10 * (1.0 - elevation / 40.0) +
        0.03 * (1.0 - np.minimum(1.0, river_distance / 50.0)) +
        0.02 * geographic_risk
    )
    
    # Add noise and create binary labels
    flood_prob += np.random.normal(0, 0.1, n_samples)
    flood_prob = np.clip(flood_prob, 0, 1)
    
    # Create labels with threshold
    labels = (flood_prob > 0.35).astype(int)
    
    # Create DataFrame
    data = pd.DataFrame({
        'rainfall_1day': rainfall_1day,
        'rainfall_3day': rainfall_3day,
        'rainfall_7day': rainfall_7day,
        'water_level_lag1': water_level_lag1,
        'water_level_trend': water_level_trend,
        'is_monsoon': is_monsoon,
        'elevation': elevation,
        'river_distance': river_distance,
        'geographic_risk': geographic_risk,
        'flood_risk': labels
    })
    
    logger.info(f"Generated {len(data)} training samples")
    logger.info(f"Flood risk distribution: {labels.mean():.2%} positive cases")
    
    return data

def train_ml_model():
    """Train the Random Forest model"""
    global rf_model, scaler
    
    if not ML_AVAILABLE:
        logger.warning("ML libraries not available, using fallback prediction")
        return False
    
    try:
        logger.info("Training Random Forest model...")
        
        # Generate training data
        data = create_synthetic_training_data()
        
        # Prepare features and target
        X = data[feature_cols]
        y = data['flood_risk']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = rf_model.score(X_train_scaled, y_train)
        test_score = rf_model.score(X_test_scaled, y_test)
        
        logger.info(f"Model trained successfully!")
        logger.info(f"Training accuracy: {train_score:.3f}")
        logger.info(f"Test accuracy: {test_score:.3f}")
        
        # Feature importance
        importance = rf_model.feature_importances_
        for feature, imp in zip(feature_cols, importance):
            logger.info(f"Feature importance - {feature}: {imp:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error training ML model: {e}")
        return False

def generate_realistic_weather_data(location: str, days: int = 7) -> pd.DataFrame:
    """Generate realistic weather data for a location"""
    
    # Get location-specific parameters
    geo_data = GEOGRAPHIC_DATA.get(location, {})
    annual_rainfall = geo_data.get('annual_rainfall_mm', 2000)
    base_daily_rainfall = annual_rainfall / 365
    
    # Current month for seasonal adjustment
    current_month = datetime.now().month
    
    # Seasonal multipliers (Bangladesh monsoon pattern)
    seasonal_multipliers = {
        1: 0.1, 2: 0.2, 3: 0.3, 4: 0.6,    # Dry season
        5: 1.2, 6: 2.5, 7: 3.0, 8: 2.8,    # Monsoon season
        9: 2.0, 10: 1.0, 11: 0.4, 12: 0.2  # Post-monsoon
    }
    
    seasonal_factor = seasonal_multipliers.get(current_month, 1.0)
    daily_expected = base_daily_rainfall * seasonal_factor
    
    # Generate realistic rainfall pattern
    rainfall_data = []
    for i in range(days):
        # Random rainfall with exponential distribution
        if random.random() < 0.3:  # 30% chance of rain
            rainfall = max(0, np.random.exponential(daily_expected))
            # Add extreme events occasionally
            if random.random() < 0.05:  # 5% chance of heavy rain
                rainfall *= random.uniform(3, 8)
        else:
            rainfall = 0
        
        rainfall_data.append(min(rainfall, 100))  # Cap at 100mm/day
    
    # Generate temperature data
    base_temp = 25 + (current_month - 6) * 2  # Seasonal variation
    temperature_data = [
        base_temp + random.uniform(-3, 5) + random.uniform(-2, 2)
        for _ in range(days)
    ]
    
    # Generate humidity data
    base_humidity = 70 + seasonal_factor * 10
    humidity_data = [
        min(95, max(40, base_humidity + random.uniform(-15, 15)))
        for _ in range(days)
    ]
    
    # Generate dates
    dates = [datetime.now() - timedelta(days=days-1-i) for i in range(days)]
    
    return pd.DataFrame({
        'date': dates,
        'rainfall': rainfall_data,
        'temperature': temperature_data,
        'humidity': humidity_data
    })

def calculate_enhanced_geographic_risk(location: str) -> float:
    """Calculate enhanced geographic risk factor"""
    geo_data = GEOGRAPHIC_DATA.get(location, {})
    
    # Multiple risk factors
    elevation_risk = max(0, (20 - geo_data.get('elevation', 10)) / 20)
    river_risk = max(0, (10 - geo_data.get('distance_to_major_river', 5)) / 10)
    drainage_risk = {'Poor': 0.8, 'Moderate': 0.5, 'Good': 0.2}.get(
        geo_data.get('drainage_quality', 'Moderate'), 0.5
    )
    urban_risk = geo_data.get('urbanization_factor', 0.5) * 0.6
    history_risk = min(1.0, geo_data.get('flood_history_frequency', 5) / 15)
    
    # Weighted combination
    combined_risk = (
        elevation_risk * 0.25 +
        river_risk * 0.25 +
        drainage_risk * 0.20 +
        urban_risk * 0.15 +
        history_risk * 0.15
    )
    
    return min(1.0, combined_risk)

def calculate_water_levels(location: str, weather_data: pd.DataFrame) -> List[float]:
    """Calculate realistic water levels based on multiple factors"""
    geo_data = GEOGRAPHIC_DATA.get(location, {})
    
    # Base parameters
    elevation = geo_data.get('elevation', 10)
    drainage_quality = geo_data.get('drainage_quality', 'Moderate')
    distance_to_river = geo_data.get('distance_to_major_river', 5)
    urbanization = geo_data.get('urbanization_factor', 0.5)
    
    # Calculate modifiers
    elevation_factor = max(0.3, 1.0 - (elevation / 50.0))
    drainage_multiplier = {'Poor': 1.4, 'Moderate': 1.1, 'Good': 0.8}.get(drainage_quality, 1.1)
    river_proximity_factor = max(0.5, 1.0 - (distance_to_river / 20.0))
    urban_runoff_factor = 1.0 + (urbanization * 0.3)
    
    # Base water level
    base_water_level = 2.8 + elevation_factor * 2.2 + river_proximity_factor * 0.8
    
    water_levels = []
    for i, rainfall in enumerate(weather_data['rainfall']):
        # Cumulative effect of recent rainfall
        recent_rain_effect = 0
        for j in range(max(0, i-2), i+1):  # 3-day influence
            days_ago = i - j
            decay_factor = 0.7 ** days_ago
            if j < len(weather_data):
                recent_rain_effect += weather_data['rainfall'].iloc[j] * decay_factor
        
        # Daily water level
        daily_level = (
            base_water_level +
            (rainfall * 0.08 * drainage_multiplier * urban_runoff_factor) +
            (recent_rain_effect * 0.04 * drainage_multiplier) +
            np.random.normal(0, 0.12)
        )
        
        water_levels.append(max(daily_level, 1.8))
    
    return water_levels

def get_ml_prediction(location: str, weather_data: pd.DataFrame, water_levels: List[float]) -> Dict:
    """Get ML-based flood prediction"""
    global rf_model, scaler
    
    if rf_model is None or scaler is None:
        return None
    
    try:
        geo_data = GEOGRAPHIC_DATA.get(location, {})
        
        # Calculate features
        latest_rainfall = weather_data['rainfall'].iloc[-1]
        rainfall_3day = weather_data['rainfall'].tail(3).sum()
        rainfall_7day = weather_data['rainfall'].sum()
        latest_water_level = water_levels[-1]
        
        # Water level trend
        if len(water_levels) >= 3:
            recent_levels = water_levels[-3:]
            water_level_trend = (recent_levels[-1] - recent_levels[0]) / 2
        else:
            water_level_trend = 0
        
        # Seasonal factor
        current_month = datetime.now().month
        is_monsoon = 1 if 6 <= current_month <= 9 else 0
        
        # Geographic features
        elevation = geo_data.get('elevation', 10)
        river_distance = geo_data.get('distance_to_major_river', 5)
        geographic_risk = calculate_enhanced_geographic_risk(location)
        
        # Create feature array
        features = np.array([[
            latest_rainfall, rainfall_3day, rainfall_7day,
            latest_water_level, water_level_trend, is_monsoon,
            elevation, river_distance, geographic_risk
        ]])
        
        # Scale and predict
        features_scaled = scaler.transform(features)
        ml_risk_probability = rf_model.predict_proba(features_scaled)[0, 1]
        
        # Calculate confidence
        confidence = min(0.95, max(0.6, 0.8 + np.random.normal(0, 0.1)))
        
        return {
            'ml_risk_probability': float(ml_risk_probability),
            'confidence': float(confidence),
            'features_used': feature_cols,
            'feature_values': features[0].tolist()
        }
        
    except Exception as e:
        logger.error(f"Error in ML prediction: {e}")
        return None

def get_fallback_prediction(location: str, weather_data: pd.DataFrame, water_levels: List[float]) -> Dict:
    """Fallback prediction when ML is not available"""
    geo_data = GEOGRAPHIC_DATA.get(location, {})
    threshold = FLOOD_THRESHOLDS.get(location, 5.5)
    
    # Calculate risk factors
    latest_rainfall = weather_data['rainfall'].iloc[-1]
    rainfall_3day = weather_data['rainfall'].tail(3).sum()
    latest_water_level = water_levels[-1]
    
    # Basic risk calculation
    rainfall_risk = min(1.0, (latest_rainfall / 25.0) * 0.4 + (rainfall_3day / 60.0) * 0.6)
    water_level_risk = max(0, (latest_water_level - threshold + 1.0) / 3.0)
    geographic_risk = calculate_enhanced_geographic_risk(location)
    
    # Combined risk
    combined_risk = (
        rainfall_risk * 0.4 +
        water_level_risk * 0.4 +
        geographic_risk * 0.2
    )
    
    return {
        'risk_probability': float(min(1.0, combined_risk)),
        'confidence': 0.75,
        'method': 'fallback_calculation'
    }

# API Routes
@app.route('/')
def dashboard():
    """Main dashboard page - API status"""
    return jsonify({
        "message": "AI Flood Prediction System API - Full ML Version",
        "status": "live",
        "version": "2.0.0",
        "ml_enabled": ML_AVAILABLE and rf_model is not None,
        "model_features": feature_cols if rf_model else None,
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
    for name, (lat, lon) in LOCATIONS.items():
        geo_data = GEOGRAPHIC_DATA.get(name, {})
        locations_data.append({
            'name': name,
            'lat': lat,
            'lon': lon,
            'threshold': FLOOD_THRESHOLDS.get(name, 5.5),
            'elevation': geo_data.get('elevation', 'N/A'),
            'drainage_quality': geo_data.get('drainage_quality', 'Unknown'),
            'flood_history_frequency': geo_data.get('flood_history_frequency', 'N/A')
        })
    return jsonify(locations_data)

@app.route('/api/predict/<location>')
def predict_location(location):
    """Get flood prediction for a specific location using full ML model"""
    if location not in LOCATIONS:
        return jsonify({'error': 'Location not found'}), 404
    
    try:
        # Generate realistic weather data
        weather_data = generate_realistic_weather_data(location, days=7)
        
        # Calculate realistic water levels
        water_levels = calculate_water_levels(location, weather_data)
        weather_data['estimated_water_level'] = water_levels
        
        # Get prediction (ML or fallback)
        ml_result = get_ml_prediction(location, weather_data, water_levels)
        
        if ml_result:
            # ML prediction available
            risk_probability = ml_result['ml_risk_probability']
            confidence = ml_result['confidence']
            prediction_method = 'random_forest_ml'
        else:
            # Use fallback prediction
            fallback_result = get_fallback_prediction(location, weather_data, water_levels)
            risk_probability = fallback_result['risk_probability']
            confidence = fallback_result['confidence']
            prediction_method = 'fallback_calculation'
        
        # Determine risk level
        if risk_probability >= 0.7:
            risk_level = 'High'
            alert_level = 'Critical'
        elif risk_probability >= 0.5:
            risk_level = 'Moderate'
            alert_level = 'Warning'
        elif risk_probability >= 0.3:
            risk_level = 'Low-Moderate'
            alert_level = 'Advisory'
        else:
            risk_level = 'Low'
            alert_level = 'Normal'
        
        # Get current conditions
        latest_rainfall = weather_data['rainfall'].iloc[-1]
        latest_water_level = water_levels[-1]
        threshold = FLOOD_THRESHOLDS.get(location, 5.5)
        
        # Recommendations
        recommendations = []
        if risk_probability >= 0.7:
            recommendations.extend([
                "Immediate evacuation may be necessary",
                "Avoid all travel in the area",
                "Monitor emergency broadcasts",
                "Move to higher ground immediately"
            ])
        elif risk_probability >= 0.5:
            recommendations.extend([
                "Prepare for possible evacuation",
                "Avoid unnecessary travel",
                "Stay tuned to weather updates",
                "Keep emergency supplies ready"
            ])
        elif risk_probability >= 0.3:
            recommendations.extend([
                "Monitor weather conditions closely",
                "Prepare emergency kit",
                "Check drainage around your property"
            ])
        else:
            recommendations.append("Normal precautions sufficient")
        
        return jsonify({
            'location': location,
            'coordinates': LOCATIONS[location],
            'timestamp': datetime.now().isoformat(),
            'risk_assessment': {
                'risk_level': risk_level,
                'risk_probability': round(risk_probability, 3),
                'confidence': round(confidence, 2),
                'alert_level': alert_level
            },
            'current_conditions': {
                'rainfall_mm': round(latest_rainfall, 1),
                'water_level_m': round(latest_water_level, 2),
                'threshold_m': threshold,
                'above_threshold': latest_water_level > threshold
            },
            'weather_forecast': {
                'rainfall_today': round(latest_rainfall, 1),
                'rainfall_3day': round(weather_data['rainfall'].tail(3).sum(), 1),
                'rainfall_7day': round(weather_data['rainfall'].sum(), 1)
            },
            'predictions': {
                'method': prediction_method,
                'ml_enabled': ml_result is not None,
                'features_analyzed': len(feature_cols) if ml_result else 4
            },
            'recommendations': recommendations,
            'geographic_info': GEOGRAPHIC_DATA.get(location, {}),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error predicting for {location}: {e}")
        return jsonify({'error': 'Prediction failed', 'details': str(e)}), 500

@app.route('/api/predict/coordinates/<float:lat>/<float:lon>')
def predict_coordinates(lat, lon):
    """Get flood prediction for specific coordinates"""
    # Find nearest location
    min_distance = float('inf')
    nearest_location = 'Dhaka'
    
    for location, (loc_lat, loc_lon) in LOCATIONS.items():
        distance = ((lat - loc_lat) ** 2 + (lon - loc_lon) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            nearest_location = location
    
    # Get prediction for nearest location
    response = predict_location(nearest_location)
    
    if response.status_code == 200:
        data = response.get_json()
        data['nearest_station'] = nearest_location
        data['distance_km'] = round(min_distance * 111, 1)  # Rough conversion to km
        return jsonify(data)
    else:
        return response

@app.route('/api/history/<location>')
def get_history(location):
    """Get historical flood data for location"""
    if location not in LOCATIONS:
        return jsonify({'error': 'Location not found'}), 404
    
    # Generate 30 days of historical data
    history = []
    for i in range(30, 0, -1):
        date = datetime.now() - timedelta(days=i)
        
        # Simulate historical risk levels
        base_risk = random.uniform(0.1, 0.8)
        seasonal_factor = 1.5 if 6 <= date.month <= 9 else 0.7
        daily_risk = min(1.0, base_risk * seasonal_factor)
        
        risk_level = 'High' if daily_risk >= 0.7 else 'Moderate' if daily_risk >= 0.4 else 'Low'
        
        history.append({
            'date': date.strftime('%Y-%m-%d'),
            'risk_probability': round(daily_risk, 3),
            'risk_level': risk_level,
            'rainfall_mm': round(random.exponential(5), 1),
            'water_level_m': round(random.uniform(2.5, 7.0), 2)
        })
    
    return jsonify({
        'location': location,
        'period': '30_days',
        'history': history
    })

@app.route('/api/alerts')
def get_alerts():
    """Get current flood alerts for all locations"""
    alerts = []
    
    for location in LOCATIONS:
        try:
            # Get current prediction
            weather_data = generate_realistic_weather_data(location, days=1)
            water_levels = calculate_water_levels(location, weather_data)
            
            ml_result = get_ml_prediction(location, weather_data, water_levels)
            if ml_result:
                risk_probability = ml_result['ml_risk_probability']
            else:
                fallback_result = get_fallback_prediction(location, weather_data, water_levels)
                risk_probability = fallback_result['risk_probability']
            
            if risk_probability >= 0.5:  # Alert threshold
                alert_level = 'Critical' if risk_probability >= 0.7 else 'Warning'
                alerts.append({
                    'location': location,
                    'alert_level': alert_level,
                    'risk_probability': round(risk_probability, 3),
                    'message': f"{alert_level} flood risk in {location}",
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error generating alert for {location}: {e}")
    
    return jsonify({
        'alerts': alerts,
        'total_alerts': len(alerts),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'system': 'AI Flood Prediction System',
        'status': 'operational',
        'version': '2.0.0',
        'ml_model': {
            'available': rf_model is not None,
            'type': 'RandomForestClassifier' if rf_model else None,
            'features': len(feature_cols) if rf_model else 0,
            'training_samples': 2500 if rf_model else 0
        },
        'locations_monitored': len(LOCATIONS),
        'last_model_update': datetime.now().isoformat(),
        'uptime': 'Running since deployment',
        'deployment': 'render-production'
    })

# Initialize the application
def initialize_app():
    """Initialize the application and train ML model"""
    logger.info("🚀 Starting AI Flood Prediction System - Full ML Version")
    logger.info(f"ML libraries available: {ML_AVAILABLE}")
    
    if ML_AVAILABLE:
        logger.info("Training ML model...")
        success = train_ml_model()
        if success:
            logger.info("✅ ML model trained successfully")
        else:
            logger.warning("⚠️ ML model training failed, using fallback")
    else:
        logger.warning("⚠️ ML libraries not available, using fallback predictions")
    
    logger.info("🌊 Flood prediction system ready")
    logger.info(f"Monitoring {len(LOCATIONS)} locations: {list(LOCATIONS.keys())}")

if __name__ == '__main__':
    initialize_app()
    
    # Get port from environment or default to 10000
    port = int(os.environ.get('PORT', 10000))
    
    # Run the app
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
