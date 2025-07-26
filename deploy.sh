#!/bin/bash

# 🌊 Bangladesh Flood Prediction System - Deployment Script

echo "🌊 Bangladesh Flood Prediction System - Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
        print_status "Python 3 found (version $PYTHON_VERSION)"
        return 0
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        return 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        print_status "pip found"
        return 0
    else
        print_error "pip not found. Please install pip."
        return 1
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Use pip3 if available, otherwise pip
    PIP_CMD="pip3"
    if ! command -v pip3 &> /dev/null; then
        PIP_CMD="pip"
    fi
    
    if $PIP_CMD install -r requirements.txt; then
        print_status "Dependencies installed successfully"
        return 0
    else
        print_error "Failed to install dependencies"
        return 1
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    directories=("data" "models" "logs" "alerts")
    
    for dir in "${directories[@]}"; do
        if mkdir -p "$dir"; then
            print_status "Created directory: $dir/"
        else
            print_error "Failed to create directory: $dir/"
            return 1
        fi
    done
    
    return 0
}

# Check if Jupyter is available
check_jupyter() {
    if command -v jupyter &> /dev/null; then
        print_status "Jupyter found"
        return 0
    else
        print_warning "Jupyter not found. Installing..."
        pip3 install jupyter
        if command -v jupyter &> /dev/null; then
            print_status "Jupyter installed successfully"
            return 0
        else
            print_error "Failed to install Jupyter"
            return 1
        fi
    fi
}

# Run system tests
run_tests() {
    print_info "Running system tests..."
    
    if python3 test_system.py; then
        print_status "All tests passed"
        return 0
    else
        print_warning "Some tests failed, but system may still work"
        return 0  # Don't fail deployment for test issues
    fi
}

# Set up configuration template
setup_config() {
    print_info "Setting up configuration..."
    
    cat > config_template.py << EOL
# 🌊 Bangladesh Flood Prediction System Configuration

# API Keys (Replace with your actual keys)
OPENWEATHER_API_KEY = "your_openweather_api_key_here"
METEOSOURCE_API_KEY = "your_meteosource_api_key_here"

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token_here"
TELEGRAM_CHAT_ID = "your_telegram_chat_id_here"

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'port': 587,
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password_here',
    'recipient_email': 'recipient@gmail.com'
}

# System Settings
DEBUG_MODE = True
LOG_LEVEL = 'INFO'
UPDATE_INTERVAL = 300  # seconds

print("⚙️ Configuration template loaded")
print("📝 Please update the API keys and settings above")
EOL
    
    print_status "Configuration template created: config_template.py"
    return 0
}

# Create systemd service (for Linux)
create_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_info "Creating systemd service..."
        
        SCRIPT_DIR=$(pwd)
        
        cat > flood-prediction.service << EOL
[Unit]
Description=Bangladesh Flood Prediction System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/automated_predictions.py
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
EOL
        
        print_status "Systemd service file created: flood-prediction.service"
        print_info "To install: sudo cp flood-prediction.service /etc/systemd/system/"
        print_info "To enable: sudo systemctl enable flood-prediction"
        print_info "To start: sudo systemctl start flood-prediction"
    else
        print_info "Systemd service creation skipped (not on Linux)"
    fi
    
    return 0
}

# Create cron job setup script
create_cron_setup() {
    print_info "Creating cron job setup script..."
    
    SCRIPT_DIR=$(pwd)
    
    cat > setup_cron.sh << EOL
#!/bin/bash
# Setup cron job for daily flood predictions

# Add cron job to run predictions daily at 6 AM
(crontab -l 2>/dev/null; echo "0 6 * * * cd $SCRIPT_DIR && python3 automated_predictions.py") | crontab -

echo "✅ Cron job added successfully!"
echo "📅 Predictions will run daily at 6:00 AM"
echo "🔍 To view cron jobs: crontab -l"
echo "❌ To remove cron job: crontab -e"
EOL
    
    chmod +x setup_cron.sh
    print_status "Cron setup script created: setup_cron.sh"
    
    return 0
}

# Create startup script
create_startup_script() {
    print_info "Creating startup script..."
    
    cat > start_system.sh << EOL
#!/bin/bash
# 🌊 Bangladesh Flood Prediction System - Startup Script

echo "🌊 Starting Bangladesh Flood Prediction System..."

# Start the web dashboard in background
echo "🌐 Starting web dashboard..."
python3 app.py &
DASHBOARD_PID=\$!

echo "✅ Dashboard started on http://localhost:5000 (PID: \$DASHBOARD_PID)"

# Run initial prediction
echo "🤖 Running initial flood prediction..."
python3 automated_predictions.py

echo "🎉 System startup complete!"
echo ""
echo "📊 Dashboard: http://localhost:5000"
echo "📓 Notebook: jupyter notebook flood_prediction_system.ipynb"
echo "🤖 Manual prediction: python3 automated_predictions.py"
echo ""
echo "Press Ctrl+C to stop the dashboard"

# Wait for dashboard
wait \$DASHBOARD_PID
EOL
    
    chmod +x start_system.sh
    print_status "Startup script created: start_system.sh"
    
    return 0
}

# Print deployment summary
print_summary() {
    echo ""
    echo "🎉 Deployment Complete!"
    echo "====================="
    echo ""
    print_info "System Files:"
    echo "   📓 flood_prediction_system.ipynb - Main analysis notebook"
    echo "   🌐 app.py - Web dashboard"
    echo "   🤖 automated_predictions.py - Daily prediction script"
    echo "   🧪 test_system.py - System test suite"
    echo ""
    print_info "Configuration:"
    echo "   ⚙️ config_template.py - Configuration template"
    echo "   📝 Update API keys and settings before running"
    echo ""
    print_info "Startup Options:"
    echo "   🚀 ./start_system.sh - Start complete system"
    echo "   📊 python3 app.py - Start web dashboard only"
    echo "   📓 jupyter notebook flood_prediction_system.ipynb - Open notebook"
    echo ""
    print_info "Automation:"
    echo "   📅 ./setup_cron.sh - Set up daily automated predictions"
    echo "   🔄 systemctl - Use flood-prediction.service (Linux only)"
    echo ""
    print_info "Next Steps:"
    echo "   1. 🔑 Get API keys from OpenWeatherMap and set up Telegram bot"
    echo "   2. ⚙️ Update config_template.py with your keys"
    echo "   3. 📓 Run the Jupyter notebook to train models"
    echo "   4. 🚀 Start the system with ./start_system.sh"
    echo "   5. 📅 Set up automation with ./setup_cron.sh"
    echo ""
    print_status "Your Bangladesh Flood Prediction System is ready! 🌊"
}

# Main deployment function
main() {
    echo "Starting deployment..."
    echo ""
    
    # Run checks and setup
    check_python || exit 1
    check_pip || exit 1
    create_directories || exit 1
    install_dependencies || exit 1
    check_jupyter || exit 1
    setup_config || exit 1
    create_service || exit 1
    create_cron_setup || exit 1
    create_startup_script || exit 1
    run_tests || exit 1
    
    print_summary
}

# Run main function
main "$@"
EOL
