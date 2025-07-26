#!/usr/bin/env python3
"""
Daily Automated Flood Prediction Script
Runs predictions for all locations and sends alerts if necessary
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from datetime import datetime, timedelta
import requests
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_predictions.log'),
        logging.StreamHandler()
    ]
)

# Configuration (load from environment variables in production)
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

def load_models():
    """Load trained models"""
    try:
        xgb_model = joblib.load('models/xgboost_flood_model.pkl')
        scaler = joblib.load('models/feature_scaler.pkl')
        lstm_model = tf.keras.models.load_model('models/lstm_flood_model.h5')
        logging.info("✅ Models loaded successfully")
        return xgb_model, lstm_model, scaler
    except Exception as e:
        logging.error(f"❌ Error loading models: {e}")
        return None, None, None

def get_simulated_live_data(location, days=7):
    """Simulate live rainfall data"""
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    dates.reverse()
    
    # Simulate realistic rainfall patterns
    np.random.seed(int(datetime.now().timestamp()) % 1000)
    rainfall = np.random.gamma(2, 3, days)
    rainfall = np.maximum(rainfall, 0)
    
    return pd.DataFrame({
        'date': dates,
        'rainfall': rainfall,
        'estimated_water_level': 4.2 + (rainfall * 0.1) + np.random.normal(0, 0.2, days)
    })

def create_flood_features(df, flood_threshold=5.5, lag_days=7):
    """Create features for flood prediction"""
    df = df.sort_values('date').reset_index(drop=True)
    df_features = df.copy()
    
    # Rename column for consistency
    if 'estimated_water_level' in df_features.columns:
        df_features['water_level'] = df_features['estimated_water_level']
    
    # Add temporal features
    df_features['date'] = pd.to_datetime(df_features['date'])
    df_features['month'] = df_features['date'].dt.month
    df_features['season'] = df_features['month'].apply(lambda x: 'monsoon' if 6 <= x <= 9 else 'dry')
    
    # Create flood label
    df_features['flood'] = (df_features['water_level'] > flood_threshold).astype(int)
    
    # Create lag features
    for i in range(1, lag_days + 1):
        df_features[f'rainfall_lag{i}'] = df_features['rainfall'].shift(i)
        df_features[f'water_level_lag{i}'] = df_features['water_level'].shift(i)
    
    # Rolling statistics
    df_features['rainfall_3day_avg'] = df_features['rainfall'].rolling(window=3).mean()
    df_features['rainfall_7day_avg'] = df_features['rainfall'].rolling(window=7).mean()
    df_features['rainfall_3day_sum'] = df_features['rainfall'].rolling(window=3).sum()
    df_features['rainfall_7day_sum'] = df_features['rainfall'].rolling(window=7).sum()
    
    # Water level statistics
    df_features['water_level_3day_avg'] = df_features['water_level'].rolling(window=3).mean()
    df_features['water_level_7day_max'] = df_features['water_level'].rolling(window=7).max()
    df_features['water_level_trend'] = df_features['water_level'] - df_features['water_level_lag1']
    
    # Seasonal features
    df_features['is_monsoon'] = df_features['season'].apply(lambda x: 1 if x == 'monsoon' else 0)
    df_features['month_sin'] = np.sin(2 * np.pi * df_features['month'] / 12)
    df_features['month_cos'] = np.cos(2 * np.pi * df_features['month'] / 12)
    
    # Interaction features
    df_features['rain_water_interaction'] = df_features['rainfall'] * df_features['water_level_lag1']
    
    # Drop rows with NaN values
    df_features = df_features.dropna().reset_index(drop=True)
    
    return df_features

def predict_flood_risk(rainfall_data, xgb_model, lstm_model, scaler, flood_threshold=5.5):
    """Predict flood risk using trained models"""
    try:
        # Create features
        df_features = create_flood_features(rainfall_data, flood_threshold, lag_days=7)
        
        if len(df_features) == 0:
            return None, "Not enough data for prediction"
        
        # Feature columns (same as training)
        feature_cols = [col for col in df_features.columns 
                       if col not in ['date', 'rainfall', 'water_level', 'month', 'year', 'season', 'flood', 'estimated_water_level']]
        
        # Get latest features
        latest_features = df_features[feature_cols].iloc[-1:].values
        latest_features_scaled = scaler.transform(latest_features)
        
        predictions = {}
        
        # XGBoost prediction
        if xgb_model is not None:
            xgb_prob = xgb_model.predict_proba(latest_features)[0, 1]
            xgb_pred = xgb_model.predict(latest_features)[0]
            predictions['xgboost'] = {
                'probability': xgb_prob,
                'prediction': xgb_pred,
                'confidence': max(xgb_prob, 1-xgb_prob)
            }
        
        # LSTM prediction (if enough data)
        if lstm_model is not None and len(df_features) >= 7:
            sequence_data = df_features[feature_cols].iloc[-7:].values
            sequence_scaled = scaler.transform(sequence_data)
            sequence_input = sequence_scaled.reshape(1, 7, len(feature_cols))
            
            lstm_prob = lstm_model.predict(sequence_input, verbose=0)[0, 0]
            lstm_pred = int(lstm_prob > 0.5)
            predictions['lstm'] = {
                'probability': lstm_prob,
                'prediction': lstm_pred,
                'confidence': max(lstm_prob, 1-lstm_prob)
            }
        
        # Ensemble prediction
        if predictions:
            avg_prob = np.mean([p['probability'] for p in predictions.values()])
            ensemble_pred = int(avg_prob > 0.5)
            ensemble_confidence = max(avg_prob, 1-avg_prob)
            
            predictions['ensemble'] = {
                'probability': avg_prob,
                'prediction': ensemble_pred,
                'confidence': ensemble_confidence
            }
        
        return predictions, df_features.iloc[-1]
        
    except Exception as e:
        return None, f"Error in prediction: {str(e)}"

def log_prediction(location, rainfall_data, predictions, log_file='logs/flood_predictions.csv'):
    """Log prediction results to CSV"""
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'location': location,
        'date': rainfall_data['date'].iloc[-1],
        'recent_rainfall': rainfall_data['rainfall'].iloc[-1],
        'estimated_water_level': rainfall_data['estimated_water_level'].iloc[-1],
        'flood_threshold': FLOOD_THRESHOLDS.get(location, 5.5)
    }
    
    # Add model predictions
    if predictions:
        for model_name, pred in predictions.items():
            log_entry[f'{model_name}_probability'] = pred['probability']
            log_entry[f'{model_name}_prediction'] = pred['prediction']
            log_entry[f'{model_name}_confidence'] = pred['confidence']
    
    # Create DataFrame
    log_df = pd.DataFrame([log_entry])
    
    # Append to file
    if os.path.exists(log_file):
        log_df.to_csv(log_file, mode='a', header=False, index=False)
    else:
        log_df.to_csv(log_file, mode='w', header=True, index=False)
    
    logging.info(f"📝 Prediction logged for {location}")

def send_alert_if_needed(location, predictions, rainfall_data):
    """Send alert if flood risk is high"""
    if not predictions:
        return False
    
    ensemble_pred = predictions.get('ensemble', predictions[list(predictions.keys())[0]])
    
    if ensemble_pred['prediction'] == 1:
        logging.warning(f"🚨 FLOOD WARNING for {location}!")
        logging.warning(f"   Risk probability: {ensemble_pred['probability']:.1%}")
        logging.warning(f"   Current rainfall: {rainfall_data['rainfall'].iloc[-1]:.1f}mm")
        logging.warning(f"   Water level: {rainfall_data['estimated_water_level'].iloc[-1]:.2f}m")
        
        # Here you would implement actual alert sending
        # For now, just log the alert
        return True
    
    return False

def main():
    """Main function to run daily predictions"""
    logging.info("🚀 Starting automated flood prediction system...")
    
    # Load models
    xgb_model, lstm_model, scaler = load_models()
    
    if xgb_model is None:
        logging.error("❌ Cannot proceed without models")
        return
    
    # Run predictions for all locations
    alerts_sent = 0
    total_locations = len(LOCATIONS)
    
    for location, (lat, lon) in LOCATIONS.items():
        try:
            logging.info(f"🔄 Processing {location}...")
            
            # Get live data (in production, this would fetch from APIs)
            live_data = get_simulated_live_data(location, days=7)
            
            # Make prediction
            threshold = FLOOD_THRESHOLDS.get(location, 5.5)
            predictions, latest_data = predict_flood_risk(
                live_data, xgb_model, lstm_model, scaler, threshold
            )
            
            if predictions:
                # Log prediction
                log_prediction(location, live_data, predictions)
                
                # Send alert if needed
                if send_alert_if_needed(location, predictions, live_data):
                    alerts_sent += 1
                
                ensemble_pred = predictions.get('ensemble', predictions[list(predictions.keys())[0]])
                logging.info(f"✅ {location}: {ensemble_pred['prediction']} (risk: {ensemble_pred['probability']:.1%})")
            else:
                logging.error(f"❌ Failed to predict for {location}: {latest_data}")
                
        except Exception as e:
            logging.error(f"❌ Error processing {location}: {str(e)}")
    
    logging.info(f"✅ Automated predictions completed!")
    logging.info(f"   Locations processed: {total_locations}")
    logging.info(f"   Alerts sent: {alerts_sent}")

if __name__ == "__main__":
    main()
