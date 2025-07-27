#!/usr/bin/env python3
"""
Test script to verify the detailed analysis fix for both static and coordinate locations
"""

import requests
import json

BASE_URL = "http://127.0.0.1:10001"

def test_coordinate_prediction():
    """Test coordinate prediction to generate data"""
    print("🧪 Testing coordinate prediction...")
    
    # Test coordinates (Dhaka area)
    lat, lon = 23.7805, 90.4199
    
    response = requests.get(f"{BASE_URL}/api/predict/coordinates/{lat}/{lon}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Coordinate prediction successful")
        print(f"Location: {data['location']}")
        print(f"Risk: {data['status']}")
        print(f"Probability: {data['risk_probability']:.2%}")
        return data['location']
    else:
        print(f"❌ Coordinate prediction failed: {response.text}")
        return None

def test_risk_trends(location):
    """Test risk trends endpoint"""
    print(f"\n🧪 Testing risk trends for: {location}")
    
    import urllib.parse
    encoded_location = urllib.parse.quote(location)
    response = requests.get(f"{BASE_URL}/api/risk-trends/{encoded_location}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Risk trends successful")
        print(f"Location: {data['location']}")
        print(f"Data points: {data['total_points']}")
        print(f"Trends: {len(data['trends'])} entries")
        return True
    else:
        print(f"❌ Risk trends failed: {response.text}")
        return False

def test_static_location():
    """Test static location prediction"""
    print("\n🧪 Testing static location (Dhaka)...")
    
    response = requests.get(f"{BASE_URL}/api/predict/Dhaka")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Static location prediction successful")
        print(f"Location: Dhaka")
        print(f"Risk: {data['status']}")
        print(f"Probability: {data['risk_probability']:.2%}")
        return True
    else:
        print(f"❌ Static location prediction failed: {response.text}")
        return False

def test_history_endpoint(location):
    """Test history endpoint"""
    print(f"\n🧪 Testing history endpoint for: {location}")
    
    response = requests.get(f"{BASE_URL}/api/history/{location}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ History endpoint successful")
        print(f"History entries: {len(data.get('history', []))}")
        return True
    else:
        print(f"❌ History endpoint failed: {response.text}")
        return False

def main():
    print("🚀 Testing Detailed Analysis Fix")
    print("=" * 50)
    
    # Test 1: Generate coordinate data
    coord_location = test_coordinate_prediction()
    
    # Test 2: Test risk trends for coordinate location
    if coord_location:
        test_risk_trends(coord_location)
    
    # Test 3: Test static location
    test_static_location()
    
    # Test 4: Test risk trends for static location
    test_risk_trends("Dhaka")
    
    # Test 5: Test history endpoint for static location
    test_history_endpoint("Dhaka")
    
    # Test 6: Test history endpoint for coordinate location (should fail)
    if coord_location:
        test_history_endpoint(coord_location)
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")
    print("\nNow test the dashboard:")
    print("1. Click on a static location (e.g., Dhaka)")
    print("2. Click 'View Detailed Analysis' - should show full details")
    print("3. Click on the map to select coordinates")
    print("4. Click 'View Detailed Analysis' - should now show full details")

if __name__ == "__main__":
    main()
