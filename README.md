# 🌊 Bangladesh Flood Prediction System

A comprehensive AI-powered flood prediction system for Bangladesh using rainfall data, machine learning models, and real-time monitoring.

## 🎯 Features

- **🤖 AI Models**: XGBoost and LSTM models for accurate flood prediction
- **📡 Live Data Integration**: OpenWeatherMap and MeteoSource API support
- **🚨 Alert System**: Telegram bot and email notifications
- **📊 Web Dashboard**: Real-time monitoring interface
- **📝 Data Logging**: Historical prediction tracking
- **🗺️ Interactive Maps**: Visualize flood risk across Bangladesh

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Edit the configuration section in `flood_prediction_system.ipynb`:
```python
# Replace with your actual API keys
OPENWEATHER_API_KEY = "your_openweather_api_key"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

### 3. Run the Jupyter Notebook
```bash
jupyter notebook flood_prediction_system.ipynb
```

### 4. Start the Web Dashboard
```bash
python app.py
```
Visit `http://localhost:5000` to view the dashboard.

### 5. Set up Automated Predictions
```bash
# Run daily predictions
python automated_predictions.py

# Or set up cron job for daily execution
crontab -e
# Add: 0 6 * * * /path/to/python automated_predictions.py
```

## 📋 Project Structure

```
flood/
├── flood_prediction_system.ipynb  # Main notebook with models
├── app.py                        # Flask web dashboard
├── automated_predictions.py      # Daily prediction script
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── templates/
│   └── dashboard.html           # Web dashboard template
├── models/                      # Trained models (generated)
│   ├── xgboost_flood_model.pkl
│   ├── lstm_flood_model.h5
│   └── feature_scaler.pkl
├── data/                        # Data files (generated)
│   └── historical_flood_data.csv
├── logs/                        # Prediction logs (generated)
│   ├── flood_predictions.csv
│   └── automated_predictions.log
└── alerts/                      # Alert history (generated)
    └── alert_history.csv
```

## 🛠️ Configuration

### Monitored Locations
The system monitors these key locations in Bangladesh:
- **Dhaka** (23.8103°N, 90.4125°E) - Threshold: 5.5m
- **Sylhet** (24.8949°N, 91.8687°E) - Threshold: 6.0m
- **Rangpur** (25.7439°N, 89.2752°E) - Threshold: 4.8m
- **Bahadurabad** (25.1906°N, 89.7006°E) - Threshold: 7.2m
- **Chittagong** (22.3569°N, 91.7832°E) - Threshold: 3.5m

### API Setup

#### OpenWeatherMap API
1. Visit https://openweathermap.org/api
2. Sign up for a free account
3. Get your API key from the dashboard
4. Update `OPENWEATHER_API_KEY` in the configuration

#### Telegram Bot Setup
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Get your chat ID by messaging @userinfobot
5. Update `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

#### Email Setup (Gmail)
1. Enable 2-factor authentication on Gmail
2. Generate an App Password
3. Update `EMAIL_CONFIG` with your credentials

## 📊 Model Performance

The system uses two complementary models:

### XGBoost Classifier
- **Accuracy**: ~85-90% on test data
- **Strengths**: Fast inference, feature importance
- **Use case**: Tabular data with engineered features

### LSTM Neural Network
- **Accuracy**: ~80-85% on test data
- **Strengths**: Sequence modeling, temporal dependencies
- **Use case**: Time series patterns

### Ensemble Approach
Combines both models for improved accuracy and reliability.

## 🔧 Features

### Data Sources
- **Rainfall**: OpenWeatherMap, MeteoSource APIs
- **River Levels**: Simulated based on rainfall patterns
- **Historical Data**: Synthetic data with realistic patterns

### Feature Engineering
- **Lag Features**: 1-7 day rainfall and water level history
- **Rolling Statistics**: 3-day and 7-day averages
- **Seasonal Features**: Monsoon indicators, cyclical patterns
- **Interaction Features**: Rainfall-water level relationships

### Alert System
- **Smart Alerts**: Cooldown periods to prevent spam
- **Multi-channel**: Telegram + Email notifications
- **Rich Content**: Detailed risk assessments and recommendations

## 🌐 Web Dashboard

The dashboard provides:
- **Real-time Map**: Interactive Bangladesh map with risk indicators
- **Location Status**: Current conditions for all monitored areas
- **Risk Trends**: Historical risk probability charts
- **Alert History**: Recent warnings and notifications
- **System Status**: Model health and last update times

## 📈 Usage Examples

### Basic Prediction
```python
# Load models
models = load_models()

# Get live data
rainfall_data = fetch_live_rainfall('Dhaka')

# Make prediction
predictions, _ = predict_flood_risk(rainfall_data, models, scaler, feature_cols)

if predictions['ensemble']['prediction'] == 1:
    print("🚨 FLOOD WARNING!")
else:
    print("✅ No flood risk detected")
```

### Automated Monitoring
```python
# Set up daily monitoring
python automated_predictions.py

# Results logged to:
# - logs/flood_predictions.csv
# - logs/automated_predictions.log
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Install dependencies with `pip install -r requirements.txt`
2. **API Errors**: Check your API keys and internet connection
3. **Model Loading**: Ensure models are trained by running the notebook
4. **Permission Errors**: Check file permissions for logs and models directories

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the Jupyter notebook for examples
3. Examine the logs for error details

## 🔮 Future Enhancements

- **Real Bangladesh Data**: Integration with BWDB and BMD
- **Satellite Imagery**: Use satellite data for better predictions
- **Mobile App**: iOS/Android app for alerts
- **Advanced Models**: Transformer and attention-based models
- **Multi-language**: Bengali language support
- **IoT Integration**: Connect with water level sensors

---

**🌊 Built with ❤️ for Bangladesh flood safety**
