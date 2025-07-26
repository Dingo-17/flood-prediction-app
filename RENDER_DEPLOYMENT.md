# 🎨 Deploy to Render - Complete Guide

## Why Render?

✅ **Free Tier Available** - Great for testing and small projects  
✅ **GitHub Integration** - Auto-deploy on code changes  
✅ **SSL Certificates** - Automatic HTTPS  
✅ **Custom Domains** - Easy domain setup  
✅ **Environment Variables** - Secure config management  
✅ **Auto-scaling** - Handles traffic spikes  
✅ **Great Support** - Excellent documentation and community  

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Prepare Your Code

Run the preparation script:
```bash
./deploy-render.sh
```

This will:
- ✅ Initialize git repository
- ✅ Configure app for Render
- ✅ Create production requirements
- ✅ Generate render.yaml config

### Step 2: Push to GitHub

1. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Name it `ai-flood-prediction` (or your preferred name)
   - Don't initialize with README
   - Click "Create repository"

2. **Push Your Code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ai-flood-prediction.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Deploy on Render

1. **Create Render Account**:
   - Go to https://render.com
   - Sign up with GitHub (recommended)

2. **Create Web Service**:
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select your `ai-flood-prediction` repository

3. **Configure Service**:
   ```
   Name: ai-flood-prediction-system
   Environment: Python 3
   Build Command: pip install -r requirements-production.txt
   Start Command: python app.py
   Instance Type: Free (or paid for better performance)
   ```

4. **Set Environment Variables**:
   ```
   FLASK_ENV = production
   PORT = 10000
   ```

5. **Optional API Keys** (for full functionality):
   ```
   OPENWEATHER_API_KEY = your_api_key_here
   TELEGRAM_BOT_TOKEN = your_bot_token_here
   TELEGRAM_CHAT_ID = your_chat_id_here
   ```

6. **Deploy**:
   - Click **"Create Web Service"**
   - Wait 2-3 minutes for deployment

### Step 4: Test Your Live App

Once deployed, test these endpoints:
```bash
# Your app will be at: https://your-app-name.onrender.com

# Test the dashboard
curl https://your-app-name.onrender.com

# Test API status
curl https://your-app-name.onrender.com/api/status

# Test flood prediction
curl https://your-app-name.onrender.com/api/predict/Dhaka
```

## 🔧 Advanced Configuration

### Auto-Deploy on Git Push

Render automatically deploys when you push to your main branch:
```bash
# Make changes to your code
git add .
git commit -m "Update flood prediction models"
git push origin main
# Render automatically deploys!
```

### Custom Domain

1. Go to your service dashboard on Render
2. Click **"Settings"** → **"Custom Domains"**
3. Add your domain (e.g., `floodprediction.yourdomain.com`)
4. Update your DNS settings as instructed

### Environment Variables Management

Add environment variables in Render dashboard:
1. Go to your service → **"Environment"**
2. Click **"Add Environment Variable"**
3. Add key-value pairs

### Scaling and Performance

- **Free Tier**: 512MB RAM, goes to sleep after 15 min of inactivity
- **Starter ($7/month)**: 512MB RAM, no sleep, faster builds
- **Standard ($25/month)**: 2GB RAM, priority support

## 📊 Monitoring Your App

### View Logs
1. Go to your service dashboard
2. Click **"Logs"** tab
3. Monitor real-time application logs

### Health Checks
Render automatically monitors your app via:
- HTTP health checks to your app
- Built-in uptime monitoring
- Email alerts on failures

### Metrics
View app performance:
- Response times
- Memory usage
- CPU usage
- Request counts

## 🚨 Setting Up Alerts

### Get API Keys

1. **OpenWeatherMap**:
   - Go to https://openweathermap.org/api
   - Sign up and get free API key
   - Add to Render environment variables

2. **Telegram Bot**:
   - Message @BotFather on Telegram
   - Create new bot with `/newbot`
   - Get bot token and chat ID
   - Add to Render environment variables

3. **Email (Gmail)**:
   - Enable 2-factor authentication
   - Generate app password
   - Add credentials to environment variables

## 🔄 Updates and Maintenance

### Update Your Models
1. Modify your code locally
2. Test changes: `python app.py`
3. Commit and push: `git push origin main`
4. Render auto-deploys your changes

### Database Integration
For production scale, consider adding:
- PostgreSQL (Render offers managed databases)
- Redis (for caching predictions)
- External storage (AWS S3, etc.)

## 💰 Cost Estimation

### Free Tier (Perfect for testing)
- ✅ 750 hours/month
- ✅ Sleeps after 15 min inactivity
- ✅ 100GB bandwidth
- ✅ Free SSL certificates

### Paid Plans (For production)
- **Starter ($7/month)**: No sleep, faster builds
- **Standard ($25/month)**: 2GB RAM, priority support
- **Pro ($85/month)**: 8GB RAM, advanced features

## 🎯 Production Checklist

- [ ] GitHub repository created and code pushed
- [ ] Render service deployed successfully
- [ ] Environment variables configured
- [ ] API endpoints tested
- [ ] Health checks passing
- [ ] Custom domain configured (optional)
- [ ] Monitoring and alerts set up
- [ ] API keys added for weather data
- [ ] Telegram/email alerts configured

## 🆘 Troubleshooting

### Common Issues

**Build Fails**:
- Check `requirements-production.txt` exists
- Verify Python version compatibility
- Check build logs in Render dashboard

**App Won't Start**:
- Verify `python app.py` works locally
- Check PORT environment variable
- Review application logs

**API Errors**:
- Test endpoints locally first
- Check environment variables
- Verify model files exist

### Support Resources

- **Render Docs**: https://render.com/docs
- **Community Forum**: https://community.render.com
- **Status Page**: https://status.render.com
- **Support**: Available in dashboard for paid plans

## 🎉 Success!

Your AI Flood Prediction System is now live on Render with:

- 🤖 **Machine Learning Models** automatically trained
- 🌐 **Professional Web Interface** with interactive dashboard
- 📡 **REST API** for integration with other systems
- 🚨 **Alert System** ready for notifications
- 📊 **Real-time Predictions** for Bangladesh locations
- 🔄 **Auto-deployment** on code changes
- 🔒 **HTTPS Security** with SSL certificates

**Your app is helping predict floods and potentially saving lives! 🌊💙**

---

*Need help? Check the troubleshooting section or contact Render support.*
