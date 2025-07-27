// Global variables
let map;
let markers = {};
let riskChart;

// API Configuration
const API_CONFIG = {
    // Production URL (Render.com)
    PRODUCTION: 'https://ai-flood-prediction-system.onrender.com',
    // Local development URL
    DEVELOPMENT: 'http://192.168.1.164:10000',
    // Current environment
    ENV: 'production' // Change to 'development' for local testing
};

// Get the current API base URL
const API_BASE_URL = API_CONFIG.ENV === 'production' ? API_CONFIG.PRODUCTION : API_CONFIG.DEVELOPMENT;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing flood prediction app...');
    initializeMap();
    loadDashboardData();
    initializeChart();
    optimizeForMobile();
    
    // Auto-refresh every 5 minutes
    setInterval(refreshData, 300000);
});

function initializeMap() {
    console.log('Initializing map...');
    // Initialize Leaflet map centered on Bangladesh with mobile-friendly options
    map = L.map('map', {
        touchZoom: true,
        scrollWheelZoom: false,
        doubleClickZoom: true,
        boxZoom: false,
        keyboard: false,
        zoomControl: true,
        attributionControl: true
    }).setView([23.6850, 90.3563], 7);
    
    // Enable scroll wheel zoom only when map is focused
    map.on('focus', function() { map.scrollWheelZoom.enable(); });
    map.on('blur', function() { map.scrollWheelZoom.disable(); });
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Add Bangladesh boundary rectangle
    const bangladeshBounds = [
        [20.5, 88.0], // Southwest corner
        [26.7, 92.8]  // Northeast corner
    ];
    
    L.rectangle(bangladeshBounds, {
        color: '#0F50A6',
        weight: 2,
        opacity: 0.6,
        fillColor: 'transparent',
        dashArray: '5, 5',
        interactive: false
    }).addTo(map);
    
    // Add click handler for coordinate-based predictions
    map.on('click', async function(e) {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;
        
        // Validate coordinates are within Bangladesh bounds
        if (lat < 20.5 || lat > 26.7 || lon < 88.0 || lon > 92.8) {
            L.popup()
                .setLatLng(e.latlng)
                .setContent(`
                    <div style="text-align: center; padding: 10px; font-family: 'Open Sans', sans-serif;">
                        <div style="color: #e74c3c; font-weight: 600; margin-bottom: 5px;">Location Outside Bangladesh</div>
                        <div style="font-size: 12px; color: #666;">
                            Flood predictions are only available within Bangladesh boundaries.
                        </div>
                    </div>
                `)
                .openOn(map);
            return;
        }
        
        // Show loading popup
        const loadingPopup = L.popup()
            .setLatLng(e.latlng)
            .setContent('<div style="text-align: center; padding: 10px;">Loading prediction...</div>')
            .openOn(map);
        
        try {
            // Use Mac's IP address for iOS app
            const response = await fetch(`${API_BASE_URL}/api/predict/coordinates/${lat}/${lon}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Create detailed popup content
            const riskColor = data.risk_probability > 0.6 ? '#e74c3c' : 
                            data.risk_probability > 0.4 ? '#f39c12' : '#27ae60';
            
            // Get primary flood risk type
            let primaryRiskInfo = '';
            if (data.flood_risk_profile && !data.flood_risk_profile.primary_risk_type) {
                const profiles = data.flood_risk_profile;
                const highestRisk = Object.entries(profiles)
                    .sort((a, b) => b[1].risk_percentage - a[1].risk_percentage)[0];
                
                if (highestRisk) {
                    const [riskType, riskData] = highestRisk;
                    const typeNames = {
                        'riverine': 'River Overflow',
                        'urban_drainage': 'Drainage',
                        'flash': 'Flash Flood',
                        'tidal': 'Coastal'
                    };
                    primaryRiskInfo = `<div><strong>Primary Risk:</strong> ${typeNames[riskType] || riskType}</div>`;
                }
            }
            
            const popupContent = `
                <div style="min-width: 180px; max-width: 250px; font-family: 'Open Sans', sans-serif;">
                    <h4 style="margin: 0 0 8px 0; color: #031D40; font-size: 14px;">${data.location}</h4>
                    <div style="background: ${riskColor}; color: white; padding: 4px 8px; border-radius: 12px; text-align: center; font-weight: 600; margin-bottom: 8px; font-size: 13px;">
                        ${data.status} (${(data.risk_probability * 100).toFixed(0)}%)
                    </div>
                    <div style="font-size: 11px; color: #113240; line-height: 1.3;">
                        <div style="margin-bottom: 2px;"><strong>Rainfall:</strong> ${data.current_rainfall.toFixed(1)}mm</div>
                        <div style="margin-bottom: 2px;"><strong>Water Level:</strong> ${data.current_water_level.toFixed(1)}m</div>
                        <div style="margin-bottom: 2px;"><strong>Elevation:</strong> ${data.geographic_factors.elevation_m.toFixed(1)}m</div>
                        <div style="margin-bottom: 2px;"><strong>River Distance:</strong> ${data.geographic_factors.distance_to_river_km.toFixed(1)}km</div>
                        ${primaryRiskInfo}
                        ${data.geographic_factors.interpolated ? '<div style="font-style: italic; margin-top: 4px; font-size: 10px;">*Interpolated data</div>' : ''}
                    </div>
                </div>
            `;
            
            loadingPopup.setContent(popupContent);
            
            // Update the detailed flood risk profile section
            console.log('Updating flood risk profile for:', data.location);
            updateFloodRiskProfile(data.location, data);
            
        } catch (error) {
            console.error('Error fetching coordinate prediction:', error);
            loadingPopup.setContent(`<div style="color: #e74c3c; padding: 10px;">
                <div><strong>Error loading prediction</strong></div>
                <div style="font-size: 12px; margin-top: 5px;">${error.message}</div>
            </div>`);
        }
    });
}

// Mobile-specific optimizations
function isMobile() {
    return window.innerWidth <= 768;
}

function optimizeForMobile() {
    if (isMobile()) {
        // Adjust map initial zoom for mobile
        if (map) {
            map.setZoom(6);
        }
        
        // Add touch-friendly markers
        document.querySelectorAll('.location-item').forEach(item => {
            item.style.cursor = 'pointer';
        });
        
        // Optimize popup positioning for mobile
        if (map && map.options) {
            map.options.closePopupOnClick = false;
        }
    }
}

// Handle window resize for responsive behavior
window.addEventListener('resize', function() {
    if (map) {
        setTimeout(() => {
            map.invalidateSize();
            optimizeForMobile();
        }, 100);
    }
});

// Optimize chart for mobile
function initializeChart() {
    console.log('Initializing chart...');
    const ctx = document.getElementById('riskChart');
    if (!ctx) {
        console.error('Chart canvas not found');
        return;
    }
    
    const isMobileDevice = isMobile();
    
    riskChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Flood Risk Probability',
                data: [],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                borderWidth: isMobileDevice ? 1.5 : 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: !isMobileDevice,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        },
                        font: {
                            size: isMobileDevice ? 10 : 12
                        }
                    },
                    grid: {
                        color: 'rgba(99, 187, 242, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        maxTicksLimit: isMobileDevice ? 4 : 7,
                        font: {
                            size: isMobileDevice ? 10 : 12
                        }
                    },
                    grid: {
                        color: 'rgba(99, 187, 242, 0.1)'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            elements: {
                point: {
                    radius: isMobileDevice ? 3 : 4,
                    hoverRadius: isMobileDevice ? 5 : 6
                }
            }
        }
    });
}

async function loadDashboardData() {
    console.log('Loading dashboard data...');
    try {
        // Use Mac's IP address for iOS app
        const BASE_URL = 'http://192.168.1.164:10000';
        
        console.log('Testing API connectivity...');
        
        // Load system status with detailed error handling
        console.log('Loading system status...');
        try {
            const statusResponse = await fetch(`${BASE_URL}/api/status`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                mode: 'cors'
            });
            
            console.log('Status response status:', statusResponse.status);
            console.log('Status response ok:', statusResponse.ok);
            
            if (!statusResponse.ok) {
                throw new Error(`Status API failed: ${statusResponse.status} ${statusResponse.statusText}`);
            }
            
            const statusData = await statusResponse.json();
            console.log('Status data received:', statusData);
            updateSystemStatus(statusData);
        } catch (statusError) {
            console.error('Status API error:', statusError);
            throw statusError;
        }

        // Load locations with detailed error handling
        console.log('Loading locations...');
        try {
            const locationsResponse = await fetch(`${BASE_URL}/api/locations`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                mode: 'cors'
            });
            
            console.log('Locations response status:', locationsResponse.status);
            
            if (!locationsResponse.ok) {
                throw new Error(`Locations API failed: ${locationsResponse.status} ${locationsResponse.statusText}`);
            }
            
            const locationsData = await locationsResponse.json();
            console.log('Locations data received:', locationsData);
            updateLocationsMap(locationsData);
            await updateLocationsList(locationsData);
        } catch (locationsError) {
            console.error('Locations API error:', locationsError);
            throw locationsError;
        }

        // Load alerts with detailed error handling
        console.log('Loading alerts...');
        try {
            const alertsResponse = await fetch(`${BASE_URL}/api/alerts`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                mode: 'cors'
            });
            
            if (!alertsResponse.ok) {
                throw new Error(`Alerts API failed: ${alertsResponse.status} ${alertsResponse.statusText}`);
            }
            
            const alertsData = await alertsResponse.json();
            console.log('Alerts data received:', alertsData);
            updateAlertsList(alertsData.alerts);
        } catch (alertsError) {
            console.error('Alerts API error:', alertsError);
            // Don't throw - alerts are not critical
        }

        // Load initial flood risk profile for first location
        const locationsResponse = await fetch(`${BASE_URL}/api/locations`);
        const locationsData = await locationsResponse.json();
        
        if (locationsData && locationsData.length > 0) {
            console.log('Loading initial flood risk profile...');
            try {
                const firstLocation = locationsData[0].name;
                const profileResponse = await fetch(`${BASE_URL}/api/predict/${firstLocation}`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    mode: 'cors'
                });
                
                if (!profileResponse.ok) {
                    throw new Error(`Profile API failed: ${profileResponse.status} ${profileResponse.statusText}`);
                }
                
                const profileData = await profileResponse.json();
                console.log('Profile data received for', firstLocation, ':', profileData);
                updateFloodRiskProfile(firstLocation, profileData);
            } catch (profileError) {
                console.error('Profile API error:', profileError);
                // Don't throw - profile is not critical for initial load
            }
        }

        console.log('Dashboard data loaded successfully');
        
        // Hide any error messages
        const existingError = document.querySelector('.connection-error');
        if (existingError) {
            existingError.remove();
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        
        // Show error message to user
        const statusElement = document.getElementById('systemStatus');
        if (statusElement) {
            statusElement.textContent = 'Connection Error';
            statusElement.style.color = '#e74c3c';
        }
        
        // Check if backend is running
        showConnectionError(error.message);
    }
}

function showConnectionError(errorMessage = 'Unknown error') {
    // Remove any existing error messages
    const existingError = document.querySelector('.connection-error');
    if (existingError) {
        existingError.remove();
    }
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'connection-error';
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
        font-family: 'Open Sans', sans-serif;
        max-width: 300px;
        max-height: 400px;
        overflow-y: auto;
    `;
    errorDiv.innerHTML = `
        <h3>Connection Error</h3>
        <p>Cannot connect to the flood prediction server.</p>
        <p><small>Make sure your Flask backend is running on 192.168.1.164:10000</small></p>
        <p><small><strong>Error:</strong> ${errorMessage}</small></p>
        <button onclick="this.parentElement.remove(); loadDashboardData();" style="
            background: white;
            color: #e74c3c;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 10px;
            margin-right: 5px;
        ">Retry</button>
        <button onclick="testDirectAPI();" style="
            background: white;
            color: #e74c3c;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 10px;
        ">Test API</button>
    `;
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 15 seconds
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 15000);
}

// Add a function to test API directly and show results
window.testDirectAPI = async function() {
    const BASE_URL = 'http://192.168.1.164:10000';
    
    try {
        console.log('Testing direct API call...');
        const response = await fetch(`${BASE_URL}/api/status`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            mode: 'cors'
        });
        
        console.log('Direct API test - Response status:', response.status);
        console.log('Direct API test - Response ok:', response.ok);
        console.log('Direct API test - Response headers:', [...response.headers.entries()]);
        
        if (response.ok) {
            const data = await response.json();
            alert('✅ API Test Successful!\n\nStatus: ' + data.status + '\nLocations: ' + data.monitored_locations);
            // Try to reload dashboard
            loadDashboardData();
        } else {
            alert('❌ API Test Failed!\n\nStatus: ' + response.status + '\nError: ' + response.statusText);
        }
    } catch (error) {
        console.error('Direct API test error:', error);
        alert('❌ API Test Failed!\n\nError: ' + error.message + '\n\nCheck console for details.');
    }
};

function updateSystemStatus(data) {
    console.log('Updating system status...');
    const statusElement = document.getElementById('systemStatus');
    const locationsElement = document.getElementById('locationsCount');
    const lastUpdateElement = document.getElementById('lastUpdate');
    
    if (statusElement) {
        statusElement.textContent = data.models_loaded ? 'Operational' : 'Limited';
    }
    if (locationsElement) {
        locationsElement.textContent = data.monitored_locations;
    }
    if (lastUpdateElement) {
        lastUpdateElement.textContent = new Date(data.last_update).toLocaleTimeString();
    }
}

function updateLocationsMap(locations) {
    console.log('Updating locations map...');
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
}

async function updateLocationsList(locations) {
    console.log('Updating locations list...');
    const container = document.getElementById('locationsList');
    if (!container) {
        console.error('Locations list container not found');
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading locations...</div>';

    for (const location of locations) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/predict/${location.name}`);
            const data = await response.json();
            
            const riskClass = data.risk_probability >= 0.75 ? 'risk-critical' :
                            data.risk_probability >= 0.6 ? 'risk-high' :
                            data.risk_probability >= 0.4 ? 'risk-medium' :
                            data.risk_probability >= 0.2 ? 'risk-low' : 'risk-minimal';
            
            const locationElement = document.createElement('div');
            locationElement.className = 'location-item';
            locationElement.onclick = () => showLocationDetails(location.name);
            
            // Add geographic context
            const geoInfo = data.geographic_factors ? 
                `Elevation: ${data.geographic_factors.elevation_m}m | River: ${data.geographic_factors.distance_to_river_km}km` :
                `Rainfall: ${data.current_rainfall.toFixed(1)}mm | Water Level: ${data.current_water_level.toFixed(1)}m`;
            
            // Create flood risk profile summary
            let riskProfileHtml = '';
            if (data.flood_risk_profile) {
                const profiles = data.flood_risk_profile;
                const highestRisk = Object.entries(profiles)
                    .sort((a, b) => b[1].risk_percentage - a[1].risk_percentage)[0];
                
                if (highestRisk) {
                    const [riskType, riskData] = highestRisk;
                    const typeNames = {
                        'riverine': 'River Overflow',
                        'urban_drainage': 'Drainage Issues',
                        'flash': 'Flash Flood',
                        'tidal': 'Coastal/Tidal'
                    };
                    riskProfileHtml = `
                        <div class="location-details" style="font-size: 0.75rem; margin-top: 3px; opacity: 0.9; color: #0F50A6;">
                            Primary: ${typeNames[riskType] || riskType} (${riskData.risk_percentage.toFixed(0)}% risk)
                        </div>
                    `;
                }
            }
            
            locationElement.innerHTML = `
                <div class="location-info">
                    <h4>${location.name}</h4>
                    <div class="location-details">
                        ${geoInfo}
                    </div>
                    ${data.geographic_factors ? `
                        <div class="location-details" style="font-size: 0.8rem; margin-top: 2px; opacity: 0.8;">
                            ${data.geographic_factors.topography} • ${data.geographic_factors.drainage_quality} drainage
                        </div>
                    ` : ''}
                    ${riskProfileHtml}
                </div>
                <div class="risk-badge ${riskClass}">
                    ${data.status} (${(data.risk_probability * 100).toFixed(0)}%)
                </div>
            `;
            
            // Replace loading message with first location, then append others
            if (container.querySelector('.loading')) {
                container.innerHTML = '';
            }
            container.appendChild(locationElement);
            
            // Update marker with enhanced styling
            if (markers[location.name]) {
                const riskLevel = data.risk_probability;
                const markerColor = riskLevel >= 0.75 ? '#8B0000' :
                                  riskLevel >= 0.6 ? '#e74c3c' :
                                  riskLevel >= 0.4 ? '#f39c12' :
                                  riskLevel >= 0.2 ? '#27ae60' : '#2ecc71';
                
                const markerSize = Math.max(12, Math.min(20, 12 + riskLevel * 8));
                
                const icon = L.divIcon({
                    html: `<div style="
                        width: ${markerSize}px; 
                        height: ${markerSize}px; 
                        background: ${markerColor}; 
                        border-radius: 50%; 
                        border: 3px solid white; 
                        box-shadow: 0 3px 8px rgba(0,0,0,0.4);
                        position: relative;
                    ">
                        ${riskLevel >= 0.75 ? '<div style="position: absolute; top: -2px; left: -2px; width: ' + (markerSize + 4) + 'px; height: ' + (markerSize + 4) + 'px; border: 2px solid ' + markerColor + '; border-radius: 50%; animation: pulse 2s infinite;"></div>' : ''}
                    </div>`,
                    iconSize: [markerSize + 6, markerSize + 6],
                    className: 'enhanced-marker'
                });
                markers[location.name].setIcon(icon);
                
                // Update popup content
                markers[location.name].bindPopup(`
                    <div style="font-family: 'Open Sans', sans-serif; min-width: 180px;">
                        <h4 style="margin: 0 0 8px 0; color: #031D40;">${location.name}</h4>
                        <div style="background: ${markerColor}; color: white; padding: 4px 8px; border-radius: 12px; text-align: center; font-weight: 600; font-size: 12px; margin-bottom: 8px;">
                            ${data.status}
                        </div>
                        <div style="font-size: 11px; color: #113240; line-height: 1.3;">
                            <div><strong>Risk Level:</strong> ${(data.risk_probability * 100).toFixed(0)}%</div>
                            <div><strong>Elevation:</strong> ${data.geographic_factors ? data.geographic_factors.elevation_m + 'm' : 'N/A'}</div>
                            <div><strong>Drainage:</strong> ${data.geographic_factors ? data.geographic_factors.drainage_quality : 'N/A'}</div>
                            ${data.flood_risk_profile ? Object.entries(data.flood_risk_profile).sort((a, b) => b[1].risk_percentage - a[1].risk_percentage)[0] ? 
                                `<div><strong>Primary Risk:</strong> ${Object.entries(data.flood_risk_profile).sort((a, b) => b[1].risk_percentage - a[1].risk_percentage)[0][0].replace('_', ' ')}</div>` : '' : ''}
                        </div>
                    </div>
                `);
            }
            
        } catch (error) {
            console.error(`Error loading data for ${location.name}:`, error);
            
            // Show error state
            const locationElement = document.createElement('div');
            locationElement.className = 'location-item';
            locationElement.innerHTML = `
                <div class="location-info">
                    <h4>${location.name}</h4>
                    <div class="location-details" style="color: #e74c3c;">
                        Error loading data
                    </div>
                </div>
                <div class="risk-badge" style="background: #95a5a6; color: white;">
                    UNKNOWN
                </div>
            `;
            
            if (container.querySelector('.loading')) {
                container.innerHTML = '';
            }
            container.appendChild(locationElement);
        }
    }
}

function updateAlertsList(alerts) {
    console.log('Updating alerts list...');
    const container = document.getElementById('alertsList');
    if (!container) {
        console.error('Alerts list container not found');
        return;
    }
    
    if (alerts.length === 0) {
        container.innerHTML = '<div class="loading">No recent alerts</div>';
        return;
    }
    
    container.innerHTML = '';
    
    alerts.reverse().forEach(alert => {
        const alertElement = document.createElement('div');
        const alertClass = alert.alert_type === 'flood_warning' ? 'alert-warning' : 'alert-info';
        const alertIcon = alert.alert_type === 'flood_warning' ? 'ALERT' : 'INFO';
        
        alertElement.className = `alert-item ${alertClass}`;
        alertElement.innerHTML = `
            <div>
                <strong>${alertIcon} ${alert.location}</strong><br>
                <small>${new Date(alert.timestamp).toLocaleString()}</small>
            </div>
            <div>
                ${(alert.risk_probability * 100).toFixed(0)}%
            </div>
        `;
        
        container.appendChild(alertElement);
    });
}

async function showLocationDetails(locationName) {
    console.log('Showing location details for:', locationName);
    try {
        // Update flood risk profile
        const profileResponse = await fetch(`${API_BASE_URL}/api/predict/${locationName}`);
        const profileData = await profileResponse.json();
        updateFloodRiskProfile(locationName, profileData);
        
        // Update risk trends chart
        const response = await fetch(`${API_BASE_URL}/api/history/${locationName}`);
        const data = await response.json();
        
        if (data.history && data.history.length > 0) {
            updateRiskChart(data.history);
            
            // Focus map on location
            const locationsResponse = await fetch(`${API_BASE_URL}/api/locations`);
            const locations = await locationsResponse.json();
            const location = locations.find(l => l.name === locationName);
            
            if (location) {
                map.setView([location.lat, location.lon], 10);
                if (markers[locationName]) {
                    markers[locationName].openPopup();
                }
            }
        }
    } catch (error) {
        console.error('Error loading location details:', error);
    }
}

function updateFloodRiskProfile(locationName, data) {
    console.log('Updating flood risk profile for:', locationName);
    const container = document.getElementById('floodRiskProfile');
    if (!container) {
        console.error('Flood risk profile container not found');
        return;
    }
    
    if (!data.flood_risk_profile) {
        container.innerHTML = '<div class="loading">No detailed flood risk profile available for this location.</div>';
        return;
    }
    
    const floodTypes = data.flood_risk_profile;
    const typeNames = {
        'riverine': 'Riverine Flooding',
        'urban_drainage': 'Urban Drainage Issues',
        'flash': 'Flash Flooding',
        'tidal': 'Tidal/Coastal Flooding'
    };
    
    let profileHtml = `
        <div style="margin-bottom: 1rem; padding: 0.8rem; background: linear-gradient(135deg, #031D40 0%, #0F50A6 100%); border-radius: 12px; color: white;">
            <h4 style="margin: 0; font-size: 1.1rem;">${locationName} - Detailed Risk Analysis</h4>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.85rem; opacity: 0.9;">Overall Risk: ${(data.risk_probability * 100).toFixed(1)}% (${data.status})</p>
        </div>
    `;
    
    // Sort flood types by risk percentage (highest first)
    const sortedTypes = Object.entries(floodTypes).sort((a, b) => b[1].risk_percentage - a[1].risk_percentage);
    
    sortedTypes.forEach(([floodType, profile]) => {
        const severityClass = profile.severity_level.toLowerCase();
        const typeName = typeNames[floodType] || floodType.replace('_', ' ');
        
        profileHtml += `
            <div class="flood-risk-item ${severityClass}">
                <div class="flood-type-header">
                    <div class="flood-type-name">${typeName}</div>
                    <div class="flood-risk-percentage ${severityClass}">
                        ${profile.risk_percentage.toFixed(0)}%
                    </div>
                </div>
                <div class="flood-description">${profile.description}</div>
                <div class="flood-degree">Degree: <strong>${profile.flood_degree}</strong></div>
                <div class="flood-depth">Estimated Depth: <strong>${profile.estimated_depth}</strong></div>
                <div class="flood-damage">Impact: ${profile.typical_damage}</div>
            </div>
        `;
    });
    
    container.innerHTML = profileHtml;
}

function updateRiskChart(historyData) {
    console.log('Updating risk chart...');
    if (!riskChart) {
        console.error('Chart not initialized');
        return;
    }
    
    const labels = historyData.map(item => item.date);
    const probabilities = historyData.map(item => item.probability);
    
    riskChart.data.labels = labels;
    riskChart.data.datasets[0].data = probabilities;
    riskChart.update();
}

function refreshData() {
    console.log('Refreshing data...');
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.textContent = 'Refreshing...';
        refreshBtn.disabled = true;
    }
    
    loadDashboardData().finally(() => {
        if (refreshBtn) {
            refreshBtn.textContent = 'Refresh';
            refreshBtn.disabled = false;
        }
    });
}

// Add some CSS for enhanced markers and popups
const style = document.createElement('style');
style.textContent = `
    .custom-marker {
        background: none !important;
        border: none !important;
    }
    
    .leaflet-popup-content-wrapper {
        background: rgba(242, 242, 242, 0.95);
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(3, 29, 64, 0.15);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99, 187, 242, 0.2);
    }
    
    .leaflet-popup-tip {
        background: rgba(242, 242, 242, 0.95);
        box-shadow: none;
    }
    
    .leaflet-popup-content {
        color: #031D40;
        font-family: 'Open Sans', sans-serif;
        font-size: 14px;
        margin: 12px 16px;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.7;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

console.log('Flood prediction app JavaScript loaded successfully');
