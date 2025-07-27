# Render Deployment Guide - Complete

## Pre-Deployment Checklist ✅

- [x] Code pushed to GitHub: `https://github.com/Dingo-17/flood-prediction-app`
- [x] `render.yaml` configured
- [x] `requirements-production.txt` ready
- [x] Flask app configured for production

## Deployment Steps

### 1. Create Render Web Service

1. Go to [Render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Connect repository: `Dingo-17/flood-prediction-app`

### 2. Service Configuration

**Basic Settings:**
- **Name**: `ai-flood-prediction-system`
- **Region**: `Oregon (US West)` or closest to users
- **Branch**: `main`
- **Root Directory**: (leave blank)
- **Runtime**: `Python 3`

**Build & Start:**
- **Build Command**: `pip install -r requirements-production.txt`
- **Start Command**: `python app.py`

**Environment Variables:**
- `FLASK_ENV`: `production`
- `PORT`: `10000`

**Advanced:**
- **Auto-Deploy**: `Yes`
- **Instance Type**: `Starter` (recommended for production)

### 3. Post-Deployment Verification

Once deployed, your app will be available at: `https://ai-flood-prediction-system.onrender.com`

#### Test These Endpoints:

```bash
# Health check
curl https://ai-flood-prediction-system.onrender.com/health

# Main dashboard
curl https://ai-flood-prediction-system.onrender.com/

# API prediction test
curl -X POST https://ai-flood-prediction-system.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060, "water_level": 5.2, "rainfall": 25.5, "temperature": 22.3}'
```

## Next Steps After Deployment

### 4. Update iOS App API URLs

Once you have your Render URL (e.g., `https://ai-flood-prediction-system.onrender.com`), update the iOS app:

**File**: `/Users/digantohaque/python/flood-ios-app/www/js/app.js`

Change:
```javascript
const API_BASE_URL = 'http://192.168.1.XXX:5000';
```

To:
```javascript
const API_BASE_URL = 'https://ai-flood-prediction-system.onrender.com';
```

### 5. iOS App Store Preparation

After updating API URLs:

1. **Update Bundle ID** in `capacitor.config.json`
2. **Add App Icons** to `ios/App/App/Assets.xcassets/AppIcon.appiconset/`
3. **Update Info.plist** with privacy descriptions
4. **Build in Xcode**:
   ```bash
   cd /Users/digantohaque/python/flood-ios-app
   npx cap sync ios
   npx cap open ios
   ```
5. **Archive and Upload** to App Store Connect

## Troubleshooting

### Common Issues:

1. **Build Fails**: Check `requirements-production.txt` has all dependencies
2. **App Won't Start**: Verify `PORT` environment variable is set to `10000`
3. **API Errors**: Check logs in Render dashboard
4. **CORS Issues**: Flask app includes CORS headers for production

### Render Dashboard Features:

- **Logs**: Real-time application logs
- **Metrics**: Performance monitoring
- **Settings**: Update environment variables
- **Deploys**: View deployment history

## Production Features Enabled

✅ **Production Flask Configuration**
✅ **CORS Headers for Cross-Origin Requests**
✅ **Error Handling and Logging**
✅ **Health Check Endpoint**
✅ **Static File Serving**
✅ **API Rate Limiting Ready**
✅ **Security Headers**

## Cost Information

- **Free Tier**: 750 hours/month, sleeps after 15 min inactivity
- **Starter Plan**: $7/month, always on, custom domains
- **Pro Plan**: $25/month, more resources, autoscaling

## Support & Monitoring

- **Render Status**: https://status.render.com/
- **Documentation**: https://render.com/docs
- **Support**: Available through Render dashboard

---

**Next Action**: Deploy to Render following the steps above, then update iOS app API URLs and proceed with App Store submission.
