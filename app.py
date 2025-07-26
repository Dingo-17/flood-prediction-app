from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import requests
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize models (will be trained on first run)
rf_model = None
scaler = None
feature_cols = None

def create_and_train_models():
    """Create and train flood prediction models"""
    global rf_model, scaler, feature_cols
    
    print("🔄 Creating synthetic training data...")
    
    # Generate synthetic flood data for training
    np.random.seed(42)
    n_samples = 1000
    
    # Generate features
    rainfall_1day = np.random.gamma(2, 2, n_samples)
    rainfall_3day = np.random.gamma(2, 3, n_samples) 
    rainfall_7day = np.random.gamma(2, 4, n_samples)
    water_level_lag1 = 3.5 + 0.1 * rainfall_1day + np.random.normal(0, 0.3, n_samples)
    water_level_trend = np.random.normal(0, 0.2, n_samples)
    is_monsoon = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    
    # Create feature matrix
    X = np.column_stack([
        rainfall_1day, rainfall_3day, rainfall_7day,
        water_level_lag1, water_level_trend, is_monsoon
    ])
    
    feature_cols = ['rainfall_1day', 'rainfall_3day', 'rainfall_7day', 
                   'water_level_lag1', 'water_level_trend', 'is_monsoon']
    
    # Create flood labels (flood if rainfall is high OR water level is high)
    flood_threshold = 5.5
    y = ((rainfall_3day > 8) | (water_level_lag1 > flood_threshold)).astype(int)
    
    print(f"📊 Training data: {X.shape[0]} samples, {y.sum()} flood events ({y.mean()*100:.1f}%)")
    
    # Split and scale
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    
    # Evaluate
    accuracy = rf_model.score(X_test_scaled, y_test)
    print(f"✅ Model trained! Accuracy: {accuracy:.3f}")
    
    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(rf_model, 'models/rf_flood_model.pkl')
    joblib.dump(scaler, 'models/feature_scaler.pkl')
    joblib.dump(feature_cols, 'models/feature_columns.pkl')
    
    return rf_model, scaler, feature_cols

# Load or create models
try:
    rf_model = joblib.load('models/rf_flood_model.pkl')
    scaler = joblib.load('models/feature_scaler.pkl')
    feature_cols = joblib.load('models/feature_columns.pkl')
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"📚 Training new models...")
    rf_model, scaler, feature_cols = create_and_train_models()

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

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/locations')
def get_locations():
    """Get all monitored locations"""
    locations_data = []
    for name, (lat, lon) in LOCATIONS.items():
        locations_data.append({
            'name': name,
            'lat': lat,
            'lon': lon,
            'threshold': FLOOD_THRESHOLDS.get(name, 5.5)
        })
    return jsonify(locations_data)

@app.route('/api/predict/<location>')
def predict_location(location):
    """Get flood prediction for a specific location"""
    if location not in LOCATIONS:
        return jsonify({'error': 'Location not found'}), 404
    
    try:
        # Simulate getting recent data (in production, this would fetch from APIs)
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        dates.reverse()
        
        # Generate realistic rainfall data
        np.random.seed(int(datetime.now().timestamp()) % 1000)
        rainfall = np.random.gamma(2, 3, 7)
        rainfall = np.maximum(rainfall, 0)
        
        # Create DataFrame
        live_data = pd.DataFrame({
            'date': dates,
            'rainfall': rainfall,
            'estimated_water_level': 4.2 + (rainfall * 0.1) + np.random.normal(0, 0.2, 7)
        })
        
        live_data['estimated_water_level'] = np.maximum(live_data['estimated_water_level'], 2.0)
        
        # Simple prediction logic (replace with actual model prediction)
        latest_rainfall = live_data['rainfall'].iloc[-1]
        latest_water_level = live_data['estimated_water_level'].iloc[-1]
        threshold = FLOOD_THRESHOLDS.get(location, 5.5)
        
        # Use Random Forest model for prediction
        if rf_model is not None and scaler is not None:
            try:
                # Create features for the model
                rainfall_3day = live_data['rainfall'].tail(3).sum()
                rainfall_7day = live_data['rainfall'].sum()
                water_level_trend = live_data['estimated_water_level'].diff().iloc[-1]
                current_month = datetime.now().month
                is_monsoon = 1 if 6 <= current_month <= 9 else 0
                
                # Create feature array
                features = np.array([[
                    latest_rainfall, rainfall_3day, rainfall_7day,
                    latest_water_level, water_level_trend, is_monsoon
                ]])
                
                # Scale features and predict
                features_scaled = scaler.transform(features)
                risk_score = rf_model.predict_proba(features_scaled)[0, 1]
                flood_prediction = rf_model.predict(features_scaled)[0]
                
            except Exception as e:
                print(f"Model prediction error: {e}")
                # Fallback to simple logic
                risk_factors = [
                    latest_water_level / threshold,
                    latest_rainfall / 20,
                    live_data['rainfall'].tail(3).sum() / 50
                ]
                risk_score = np.clip(np.mean(risk_factors), 0, 1)
                flood_prediction = int(risk_score > 0.6)
        else:
            # Fallback calculation if model not available
            risk_factors = [
                latest_water_level / threshold,
                latest_rainfall / 20,  # 20mm is moderate rainfall
                live_data['rainfall'].tail(3).sum() / 50  # 3-day accumulated
            ]
            risk_score = np.clip(np.mean(risk_factors), 0, 1)
            flood_prediction = int(risk_score > 0.6)
        
        return jsonify({
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'current_rainfall': float(latest_rainfall),
            'current_water_level': float(latest_water_level),
            'flood_threshold': float(threshold),
            'flood_risk': int(flood_prediction),
            'risk_probability': float(risk_score),
            'confidence': float(max(risk_score, 1-risk_score)),
            'status': 'HIGH RISK' if flood_prediction == 1 else 'LOW RISK',
            'recent_data': [{
                'date': row['date'],
                'rainfall': float(row['rainfall']),
                'estimated_water_level': float(row['estimated_water_level'])
            } for _, row in live_data.iterrows()]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<location>')
def get_history(location):
    """Get prediction history for a location"""
    log_file = 'logs/flood_predictions.csv'
    
    if not os.path.exists(log_file):
        return jsonify({'history': []})
    
    try:
        df = pd.read_csv(log_file)
        location_history = df[df['location'] == location].tail(30)
        
        history = []
        for _, row in location_history.iterrows():
            history.append({
                'date': row['date'],
                'rainfall': round(row['recent_rainfall'], 1),
                'water_level': round(row['estimated_water_level'], 2),
                'prediction': int(row.get('ensemble_prediction', 0)),
                'probability': round(row.get('ensemble_probability', 0), 3)
            })
        
        return jsonify({'history': history})
        
    except Exception as e:
        return jsonify({'error': str(e), 'history': []}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    alert_file = 'alerts/alert_history.csv'
    
    if not os.path.exists(alert_file):
        return jsonify({'alerts': []})
    
    try:
        df = pd.read_csv(alert_file)
        recent_alerts = df.tail(10)
        
        alerts = []
        for _, row in recent_alerts.iterrows():
            alerts.append({
                'timestamp': row['timestamp'],
                'location': row['location'],
                'alert_type': row['alert_type'],
                'risk_probability': round(row['risk_probability'], 3)
            })
        
        return jsonify({'alerts': alerts})
        
    except Exception as e:
        return jsonify({'error': str(e), 'alerts': []}), 500

@app.route('/api/status')
def system_status():
    """Get system status"""
    return jsonify({
        'status': 'operational',
        'models_loaded': rf_model is not None and scaler is not None,
        'last_update': datetime.now().isoformat(),
        'monitored_locations': len(LOCATIONS),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))  # Render uses port 10000 by default
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
