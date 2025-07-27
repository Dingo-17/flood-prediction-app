#!/usr/bin/env python3
"""
Test script to verify coordinate-based chart updates work correctly
"""
import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_coordinate_prediction_and_chart(lat, lon):
    """Test coordinate prediction and then chart data retrieval"""
    print(f"\n🔄 Testing coordinate ({lat}, {lon})...")
    
    # 1. Make a prediction for this coordinate to generate data
    prediction_url = f"{BASE_URL}/api/predict/coordinates/{lat}/{lon}"
    try:
        response = requests.get(prediction_url)
        if response.status_code == 200:
            data = response.json()
            location_name = data['location']
            print(f"✅ Prediction successful: {location_name}")
            print(f"   Risk: {data['status']} ({data['risk_probability']:.3f})")
            
            # 2. Now test risk trends for this location
            import urllib.parse
            encoded_location = urllib.parse.quote(location_name)
            trends_url = f"{BASE_URL}/api/risk-trends/{encoded_location}"
            
            trends_response = requests.get(trends_url)
            if trends_response.status_code == 200:
                trends_data = trends_response.json()
                print(f"✅ Risk trends successful: {trends_data['total_points']} data points")
                
                if trends_data['total_points'] > 0:
                    print(f"   Latest data: {trends_data['trends'][-1]}")
                    return True
                else:
                    print(f"⚠️ No trend data available")
                    return False
            else:
                print(f"❌ Risk trends failed: {trends_response.status_code}")
                return False
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_static_location_chart(location):
    """Test static location chart data retrieval"""
    print(f"\n🔄 Testing static location: {location}...")
    
    try:
        trends_url = f"{BASE_URL}/api/risk-trends/{location}"
        response = requests.get(trends_url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Risk trends successful: {data['total_points']} data points")
            
            if data['total_points'] > 0:
                print(f"   Date range: {data['trends'][0]['date']} to {data['trends'][-1]['date']}")
                print(f"   Average risk: {sum(t['probability'] for t in data['trends']) / len(data['trends']):.3f}")
                return True
            else:
                print(f"⚠️ No trend data available")
                return False
        else:
            print(f"❌ Risk trends failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🧪 Testing Coordinate Chart Updates")
    print("=" * 50)
    
    # Test coordinate-based locations
    test_coordinates = [
        (23.7805, 90.4199),  # Dhaka area
        (24.8949, 91.8687),  # Sylhet area
        (22.3569, 91.7832),  # Chittagong area
        (25.1906, 89.7006),  # Bahadurabad area
    ]
    
    coordinate_success = 0
    for lat, lon in test_coordinates:
        if test_coordinate_prediction_and_chart(lat, lon):
            coordinate_success += 1
        time.sleep(0.2)  # Small delay between requests
    
    # Test static locations
    static_locations = ['Dhaka', 'Sylhet', 'Chittagong', 'Rangpur', 'Bahadurabad']
    static_success = 0
    for location in static_locations:
        if test_static_location_chart(location):
            static_success += 1
        time.sleep(0.2)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Coordinate locations: {coordinate_success}/{len(test_coordinates)} successful")
    print(f"   Static locations: {static_success}/{len(static_locations)} successful")
    
    if coordinate_success == len(test_coordinates) and static_success == len(static_locations):
        print("✅ All tests passed! Chart updates should work for both coordinate and static locations.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()
