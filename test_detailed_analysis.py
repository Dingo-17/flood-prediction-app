#!/usr/bin/env python3
"""
Test script to simulate the detailed analysis functionality
"""
import requests
import json

BASE_URL = "http://localhost:10000"

def test_detailed_analysis(location):
    """Test the detailed analysis for a specific location"""
    print(f"\n🔍 Testing detailed analysis for: {location}")
    print("=" * 50)
    
    try:
        # Step 1: Test prediction API
        print("1️⃣ Testing prediction API...")
        pred_response = requests.get(f"{BASE_URL}/api/predict/{location}")
        
        if pred_response.status_code != 200:
            print(f"❌ Prediction API failed: {pred_response.status_code}")
            print(f"   Response: {pred_response.text}")
            return False
            
        pred_data = pred_response.json()
        print(f"✅ Prediction API working")
        print(f"   Status: {pred_data.get('status', 'N/A')}")
        print(f"   Risk: {pred_data.get('flood_risk', 'N/A')}")
        
        # Check recent_data structure
        if 'recent_data' not in pred_data:
            print("❌ Missing 'recent_data' in prediction response")
            return False
        
        if not isinstance(pred_data['recent_data'], list):
            print("❌ 'recent_data' is not a list")
            return False
            
        print(f"   Recent data points: {len(pred_data['recent_data'])}")
        
        # Step 2: Test history API
        print("\n2️⃣ Testing history API...")
        hist_response = requests.get(f"{BASE_URL}/api/history/{location}")
        
        if hist_response.status_code != 200:
            print(f"❌ History API failed: {hist_response.status_code}")
            print(f"   Response: {hist_response.text}")
            return False
            
        hist_data = hist_response.json()
        print(f"✅ History API working")
        
        # Check history structure
        if 'history' not in hist_data:
            print("❌ Missing 'history' in history response")
            return False
            
        if not isinstance(hist_data['history'], list):
            print("❌ 'history' is not a list")
            return False
            
        print(f"   History points: {len(hist_data['history'])}")
        
        # Step 3: Test calculations that might fail
        print("\n3️⃣ Testing calculations...")
        
        history = hist_data['history']
        if len(history) == 0:
            print("⚠️  History is empty - this could cause division by zero")
            avg_probability = 0
        else:
            total_prob = sum(h.get('probability', 0) for h in history)
            avg_probability = round(total_prob / len(history) * 100)
            print(f"✅ Average probability calculation: {avg_probability}%")
        
        high_risk_days = len([h for h in history if h.get('prediction', 0) == 1])
        print(f"✅ High risk days calculation: {high_risk_days}")
        
        # Step 4: Test data rendering simulation
        print("\n4️⃣ Testing data rendering simulation...")
        
        # Simulate the recent data rendering
        recent_data_html = []
        for day in pred_data['recent_data']:
            try:
                date = day.get('date', 'N/A')
                rainfall = float(day.get('rainfall', 0))
                water_level = float(day.get('estimated_water_level', 0))
                recent_data_html.append(f"{date}: {rainfall:.1f}mm, {water_level:.2f}m")
            except (TypeError, ValueError) as e:
                print(f"❌ Error processing recent data item: {e}")
                print(f"   Data: {day}")
                return False
        
        print(f"✅ Recent data rendering: {len(recent_data_html)} items")
        
        print(f"\n🎉 All tests passed for {location}!")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Test detailed analysis for multiple locations"""
    locations = ["Dhaka", "Sylhet", "Chittagong", "Location (23.810, 90.412)"]
    
    print("🧪 DETAILED ANALYSIS TEST SUITE")
    print("=" * 60)
    
    passed = 0
    for location in locations:
        if test_detailed_analysis(location):
            passed += 1
    
    print(f"\n📊 SUMMARY: {passed}/{len(locations)} locations passed all tests")
    
    if passed == len(locations):
        print("🎉 All detailed analysis tests passed!")
    else:
        print("⚠️  Some tests failed - check the errors above")

if __name__ == "__main__":
    main()
