# Render Deployment Configuration for AI Flood Prediction System

## Service Configuration
- **Type**: Web Service
- **Environment**: Python 3.13.4
- **Build Command**: `./build.sh` (or `pip install -r requirements-production.txt`)
- **Start Command**: `python app.py`
- **Port**: 10000

## Environment Variables
- FLASK_ENV=production
- PORT=10000

## Manual Configuration Steps (if automatic deployment fails):

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select your service**: ai-flood-prediction-system
3. **Go to Settings**
4. **Update Build Command**: `pip install -r requirements-production.txt`
5. **Update Start Command**: `python app.py`
6. **Set Environment Variables**:
   - FLASK_ENV: production
   - PORT: 10000
7. **Manual Deploy**: Click "Manual Deploy" -> "Deploy latest commit"

## Build Commands to Try (in order of preference):
1. `./build.sh`
2. `pip install -r requirements-production.txt`
3. `pip install -r requirements.txt`
4. `python -m pip install -r requirements-production.txt`

## Files Required for Deployment:
- ✅ app.py (Flask application)
- ✅ requirements-production.txt (dependencies)
- ✅ render.yaml (service configuration)
- ✅ build.sh (build script)
- ✅ All model files and templates

## Production URL:
https://ai-flood-prediction-system.onrender.com

## Troubleshooting:
- If build fails, check that requirements-production.txt exists
- Verify all dependencies are compatible with Python 3.13.4
- Check Render logs for specific error messages
- Try manual deployment with explicit build command
