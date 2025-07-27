#!/usr/bin/env python3
"""
Test to verify real-time data fetching vs cached/static data
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5002"

def test_realtime_vs_cached():
    """Compare real-time endpoint vs regular endpoint"""
    location = "Dhaka"
    
    print("🧪 Testing Real-Time Data Fetching")
    print("=" * 50)
    
    # Test multiple calls to see if data changes
    for i in range(3):
        print(f"\n📊 Test Run #{i+1} - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Test real-time endpoint
            print("  🔄 Fetching real-time data...")
            realtime_response = requests.get(f"{BASE_URL}/api/predict/realtime/{location}")
            
            if realtime_response.status_code == 200:
                realtime_data = realtime_response.json()
                print(f"  ✅ Real-time: {realtime_data['risk_probability']:.3f} risk, {realtime_data['current_rainfall']:.2f}mm rain")
                print(f"     Data source: {realtime_data.get('data_source', 'N/A')}")
                print(f"     Weather conditions: {realtime_data.get('weather_conditions', {}).get('7day_total_rainfall', 'N/A')} mm (7-day total)")
                
                # Show recent weather data
                recent_data = realtime_data.get('recent_data', [])
                if recent_data:
                    print(f"     Recent weather: {len(recent_data)} days of data")
                    latest = recent_data[-1]
                    print(f"     Latest: {latest['date']} - {latest['rainfall']:.2f}mm rain, {latest['estimated_water_level']:.2f}m water")
            else:
                print(f"  ❌ Real-time failed: {realtime_response.status_code}")
            
            # Test regular endpoint for comparison
            print("  📁 Fetching cached data...")
            cached_response = requests.get(f"{BASE_URL}/api/predict/{location}")
            
            if cached_response.status_code == 200:
                cached_data = cached_response.json()
                print(f"  ✅ Cached: {cached_data['risk_probability']:.3f} risk, {cached_data['current_rainfall']:.2f}mm rain")
                
                # Compare timestamps
                realtime_ts = realtime_data.get('timestamp', '') if realtime_response.status_code == 200 else ''
                cached_ts = cached_data.get('timestamp', '')
                
                if realtime_ts and cached_ts:
                    print(f"     Timestamps: RT={realtime_ts[-8:-3]} vs Cached={cached_ts[-8:-3]}")
            else:
                print(f"  ❌ Cached failed: {cached_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        if i < 2:  # Don't sleep after last iteration
            print("  ⏳ Waiting 3 seconds...")
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print("📋 Analysis:")
    print("• Real-time endpoint should fetch fresh weather data each time")
    print("• Risk values may vary slightly due to fresh data/randomness")
    print("• 'data_source': 'real-time' indicates fresh data fetch")
    print("• Weather conditions should show realistic patterns")

def test_different_locations():
    """Test real-time data for different locations"""
    locations = ['Dhaka', 'Sylhet', 'Chittagong']
    
    print(f"\n🌍 Testing Real-Time Data Across Locations")
    print("=" * 50)
    
    for location in locations:
        try:
            response = requests.get(f"{BASE_URL}/api/predict/realtime/{location}")
            if response.status_code == 200:
                data = response.json()
                weather = data.get('weather_conditions', {})
                print(f"📍 {location}:")
                print(f"   Risk: {data['risk_probability']:.3f} ({data['status']})")
                print(f"   Rainfall: Current={data['current_rainfall']:.2f}mm, 7-day={weather.get('7day_total_rainfall', 'N/A')}mm")
                print(f"   Water Level: {data['current_water_level']:.2f}m (threshold: {data['flood_threshold']}m)")
                print(f"   Trend: {weather.get('recent_trend', 'N/A')}")
            else:
                print(f"❌ {location}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {location}: Error - {e}")
    
    print("\n📊 Geographic consistency check:")
    print("• Similar nearby locations should have similar weather patterns")
    print("• Risk levels should reflect local geographic factors")
    print("• All locations should have realistic weather data")

if __name__ == "__main__":
    test_realtime_vs_cached()
    test_different_locations()
