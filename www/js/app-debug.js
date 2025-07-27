// Flood Prediction iOS App - Simplified with Debug Logging
console.log('🌊 Flood Prediction App Starting...');
console.log('User Agent:', navigator.userAgent);
console.log('Online Status:', navigator.onLine);
console.log('Capacitor Available:', typeof window.Capacitor !== 'undefined');

// Global variables
let map;
let markers = {};
let riskChart;
const API_BASE = 'http://192.168.1.164:10000';

// Debug helper
function debugLog(message, data = null) {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`[${timestamp}] 🔍 ${message}`, data || '');
    
    // Also show in UI if debug element exists
    const debugElement = document.getElementById('debug-info');
    if (debugElement) {
        const div = document.createElement('div');
        div.style.cssText = 'font-size: 12px; color: #666; margin: 2px 0; padding: 2px;';
        div.textContent = `[${timestamp}] ${message}`;
        debugElement.appendChild(div);
        debugElement.scrollTop = debugElement.scrollHeight;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    debugLog('DOM Content Loaded');
    
    // Add debug info panel
    addDebugPanel();
    
    // Start initialization
    initializeApp();
});

function addDebugPanel() {
    const debugPanel = document.createElement('div');
    debugPanel.id = 'debug-panel';
    debugPanel.style.cssText = `
        position: fixed;
        bottom: 10px;
        right: 10px;
        width: 300px;
        height: 150px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 11px;
        z-index: 10000;
        overflow: hidden;
    `;
    
    debugPanel.innerHTML = `
        <div style="font-weight: bold; margin-bottom: 5px;">Debug Console</div>
        <div id="debug-info" style="height: 100px; overflow-y: auto;"></div>
        <button onclick="this.parentElement.style.display='none'" style="margin-top: 5px; padding: 2px 8px; font-size: 10px;">Hide</button>
        <button onclick="testAPI()" style="margin-top: 5px; padding: 2px 8px; font-size: 10px;">Test API</button>
    `;
    
    document.body.appendChild(debugPanel);
    debugLog('Debug panel added');
}

async function initializeApp() {
    try {
        debugLog('Starting app initialization');
        
        // Show loading message
        showLoadingMessage('Initializing flood prediction system...');
        
        // Initialize components step by step
        await initializeMap();
        await initializeChart();
        await loadDashboardData();
        
        debugLog('App initialization completed successfully');
        hideLoadingMessage();
        
    } catch (error) {
        debugLog('App initialization failed', error);
        showError('Failed to initialize app: ' + error.message);
    }
}

function showLoadingMessage(message) {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-message';
    loadingDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(255,255,255,0.95);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        z-index: 9999;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    `;
    loadingDiv.innerHTML = `
        <div style="font-size: 18px; margin-bottom: 10px;">🌊</div>
        <div>${message}</div>
        <div style="margin-top: 10px; font-size: 12px; color: #666;">Please wait...</div>
    `;
    document.body.appendChild(loadingDiv);
}

function hideLoadingMessage() {
    const loading = document.getElementById('loading-message');
    if (loading) {
        loading.remove();
    }
}

function showError(message) {
    hideLoadingMessage();
    
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(231, 76, 60, 0.95);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        z-index: 10000;
        max-width: 300px;
    `;
    errorDiv.innerHTML = `
        <h3>⚠️ Error</h3>
        <p>${message}</p>
        <button onclick="this.parentElement.remove(); testAPI();" style="
            background: white;
            color: #e74c3c;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            margin: 5px;
        ">Test API</button>
        <button onclick="this.parentElement.remove(); initializeApp();" style="
            background: white;
            color: #e74c3c;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            margin: 5px;
        ">Retry</button>
    `;
    document.body.appendChild(errorDiv);
}

async function initializeMap() {
    return new Promise((resolve, reject) => {
        try {
            debugLog('Initializing map...');
            
            const mapElement = document.getElementById('map');
            if (!mapElement) {
                throw new Error('Map element not found');
            }
            
            if (typeof L === 'undefined') {
                throw new Error('Leaflet library not loaded');
            }
            
            map = L.map('map', {
                touchZoom: true,
                scrollWheelZoom: false,
                doubleClickZoom: true,
                boxZoom: false,
                keyboard: false,
                zoomControl: true,
                attributionControl: true
            }).setView([23.6850, 90.3563], 6);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Add Bangladesh boundary
            const bangladeshBounds = [[20.5, 88.0], [26.7, 92.8]];
            L.rectangle(bangladeshBounds, {
                color: '#0F50A6',
                weight: 2,
                opacity: 0.6,
                fillColor: 'transparent',
                dashArray: '5, 5',
                interactive: false
            }).addTo(map);
            
            debugLog('Map initialized successfully');
            resolve();
            
        } catch (error) {
            debugLog('Map initialization failed', error);
            reject(error);
        }
    });
}

async function initializeChart() {
    return new Promise((resolve, reject) => {
        try {
            debugLog('Initializing chart...');
            
            const chartElement = document.getElementById('riskChart');
            if (!chartElement) {
                debugLog('Chart element not found, skipping chart initialization');
                resolve();
                return;
            }
            
            if (typeof Chart === 'undefined') {
                throw new Error('Chart.js library not loaded');
            }
            
            riskChart = new Chart(chartElement.getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Flood Risk Probability',
                        data: [],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true, position: 'top' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1,
                            ticks: {
                                callback: function(value) {
                                    return (value * 100).toFixed(0) + '%';
                                }
                            }
                        }
                    }
                }
            });
            
            debugLog('Chart initialized successfully');
            resolve();
            
        } catch (error) {
            debugLog('Chart initialization failed', error);
            reject(error);
        }
    });
}

async function loadDashboardData() {
    debugLog('Starting dashboard data load...');
    
    try {
        // Test basic connectivity first
        debugLog('Testing basic connectivity...');
        const testResponse = await fetch(`${API_BASE}/api/status`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            mode: 'cors'
        });
        
        debugLog('Test response received', {
            status: testResponse.status,
            ok: testResponse.ok,
            type: testResponse.type
        });
        
        if (!testResponse.ok) {
            throw new Error(`HTTP ${testResponse.status}: ${testResponse.statusText}`);
        }
        
        const testData = await testResponse.json();
        debugLog('Test data parsed successfully', testData);
        
        // Update system status
        updateSystemStatus(testData);
        
        // Load locations
        debugLog('Loading locations...');
        const locationsResponse = await fetch(`${API_BASE}/api/locations`);
        if (!locationsResponse.ok) {
            throw new Error(`Locations API failed: ${locationsResponse.status}`);
        }
        const locationsData = await locationsResponse.json();
        debugLog('Locations loaded', locationsData);
        
        // Update map and locations list
        updateLocationsMap(locationsData);
        await updateLocationsList(locationsData);
        
        // Load alerts
        debugLog('Loading alerts...');
        try {
            const alertsResponse = await fetch(`${API_BASE}/api/alerts`);
            if (alertsResponse.ok) {
                const alertsData = await alertsResponse.json();
                updateAlertsList(alertsData.alerts);
                debugLog('Alerts loaded', alertsData);
            }
        } catch (error) {
            debugLog('Alerts loading failed (non-critical)', error);
        }
        
        debugLog('Dashboard data loaded successfully');
        
    } catch (error) {
        debugLog('Dashboard data loading failed', error);
        throw error;
    }
}

function updateSystemStatus(data) {
    debugLog('Updating system status', data);
    
    const statusElement = document.getElementById('systemStatus');
    const locationsElement = document.getElementById('locationsCount');
    const lastUpdateElement = document.getElementById('lastUpdate');
    
    if (statusElement) {
        statusElement.textContent = data.models_loaded ? 'Operational' : 'Limited';
        statusElement.style.color = data.models_loaded ? '#27ae60' : '#f39c12';
    }
    if (locationsElement) {
        locationsElement.textContent = data.monitored_locations;
    }
    if (lastUpdateElement) {
        lastUpdateElement.textContent = new Date(data.last_update).toLocaleTimeString();
    }
}

function updateLocationsMap(locations) {
    debugLog('Updating locations map', locations);
    
    if (!map) {
        debugLog('Map not available, skipping map update');
        return;
    }
    
    // Clear existing markers
    Object.values(markers).forEach(marker => map.removeLayer(marker));
    markers = {};
    
    // Add markers for each location
    locations.forEach(location => {
        const marker = L.marker([location.lat, location.lon])
            .addTo(map)
            .bindPopup(`
                <strong>${location.name}</strong><br>
                Flood Threshold: ${location.threshold}m
            `);
        
        markers[location.name] = marker;
    });
    
    debugLog(`Added ${locations.length} markers to map`);
}

async function updateLocationsList(locations) {
    debugLog('Updating locations list', locations);
    
    const container = document.getElementById('locationsList');
    if (!container) {
        debugLog('Locations list container not found, skipping list update');
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading location data...</div>';
    
    for (const [index, location] of locations.entries()) {
        try {
            debugLog(`Loading data for location ${index + 1}/${locations.length}: ${location.name}`);
            
            const response = await fetch(`${API_BASE}/api/predict/${location.name}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            debugLog(`Data loaded for ${location.name}`, data);
            
            const riskClass = data.risk_probability >= 0.75 ? 'risk-critical' :
                            data.risk_probability >= 0.6 ? 'risk-high' :
                            data.risk_probability >= 0.4 ? 'risk-medium' :
                            data.risk_probability >= 0.2 ? 'risk-low' : 'risk-minimal';
            
            const locationElement = document.createElement('div');
            locationElement.className = 'location-item';
            locationElement.innerHTML = `
                <div class="location-info">
                    <h4>${location.name}</h4>
                    <div class="location-details">
                        Risk: ${(data.risk_probability * 100).toFixed(0)}% | Status: ${data.status}
                    </div>
                </div>
                <div class="risk-badge ${riskClass}">
                    ${(data.risk_probability * 100).toFixed(0)}%
                </div>
            `;
            
            // Replace loading message with first location, then append others
            if (container.querySelector('.loading')) {
                container.innerHTML = '';
            }
            container.appendChild(locationElement);
            
        } catch (error) {
            debugLog(`Failed to load data for ${location.name}`, error);
            
            const locationElement = document.createElement('div');
            locationElement.className = 'location-item';
            locationElement.innerHTML = `
                <div class="location-info">
                    <h4>${location.name}</h4>
                    <div class="location-details" style="color: #e74c3c;">
                        Error: ${error.message}
                    </div>
                </div>
                <div class="risk-badge" style="background: #95a5a6; color: white;">
                    ERROR
                </div>
            `;
            
            if (container.querySelector('.loading')) {
                container.innerHTML = '';
            }
            container.appendChild(locationElement);
        }
    }
    
    debugLog('Locations list update completed');
}

function updateAlertsList(alerts) {
    debugLog('Updating alerts list', alerts);
    
    const container = document.getElementById('alertsList');
    if (!container) {
        debugLog('Alerts list container not found, skipping alerts update');
        return;
    }
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div class="loading">No recent alerts</div>';
        return;
    }
    
    container.innerHTML = '';
    
    alerts.forEach(alert => {
        const alertElement = document.createElement('div');
        alertElement.className = 'alert-item';
        alertElement.innerHTML = `
            <div>
                <strong>ALERT ${alert.location}</strong><br>
                <small>${new Date(alert.timestamp).toLocaleString()}</small>
            </div>
            <div>
                ${(alert.risk_probability * 100).toFixed(0)}%
            </div>
        `;
        container.appendChild(alertElement);
    });
    
    debugLog(`Added ${alerts.length} alerts to list`);
}

// Global test function
async function testAPI() {
    debugLog('Running API test...');
    
    const tests = [
        { name: 'Status', url: '/api/status' },
        { name: 'Locations', url: '/api/locations' },
        { name: 'Alerts', url: '/api/alerts' }
    ];
    
    for (const test of tests) {
        try {
            debugLog(`Testing ${test.name}...`);
            const response = await fetch(`${API_BASE}${test.url}`);
            const data = await response.json();
            
            if (response.ok) {
                debugLog(`✅ ${test.name} test passed`, data);
            } else {
                debugLog(`❌ ${test.name} test failed - HTTP ${response.status}`, data);
            }
        } catch (error) {
            debugLog(`❌ ${test.name} test failed - ${error.message}`, error);
        }
    }
    
    debugLog('API test completed');
}

// Log that script is loaded
debugLog('App script loaded successfully');
console.log('🌊 Flood Prediction App Script Loaded');
