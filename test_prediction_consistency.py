#!/usr/bin/env python3
"""
Test to verify consistent flood risk predictions between static locations and nearby coordinates
"""
import requests
import json

BASE_URL = "http://localhost:5002"

def test_prediction_consistency():
    """Test that nearby coordinates have similar risk levels to static locations"""
    
    # Define test cases: static location and nearby coordinates
    test_cases = [
        {
            'static_location': 'Dhaka',
            'static_coords': (23.8103, 90.4125),
            'test_coords': [
                (23.810, 90.412),   # Very close to Dhaka
                (23.815, 90.415),   # Slightly northeast
                (23.805, 90.410),   # Slightly southwest
            ]
        },
        {
            'static_location': 'Sylhet', 
            'static_coords': (24.8949, 91.8687),
            'test_coords': [
                (24.895, 91.869),   # Very close to Sylhet
                (24.900, 91.870),   # Slightly north
                (24.890, 91.865),   # Slightly south
            ]
        }
    ]
    
    print("🧪 Testing Prediction Consistency")
    print("=" * 60)
    
    for case in test_cases:
        static_location = case['static_location']
        static_coords = case['static_coords']
        
        print(f"\n📍 Testing {static_location} at {static_coords}")
        
        # Get static location prediction
        try:
            response = requests.get(f"{BASE_URL}/api/predict/{static_location}")
            if response.status_code == 200:
                static_data = response.json()
                static_risk = static_data['risk_probability']
                static_rainfall = static_data['current_rainfall']
                static_water = static_data['current_water_level']
                
                print(f"   Static location: {static_risk:.3f} risk ({static_risk*100:.1f}%)")
                print(f"   Rainfall: {static_rainfall:.2f}mm, Water: {static_water:.2f}m")
            else:
                print(f"   ❌ Failed to get static prediction: {response.status_code}")
                continue
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
            
        # Test nearby coordinates
        print(f"\n   📊 Testing nearby coordinates:")
        for lat, lon in case['test_coords']:
            try:
                response = requests.get(f"{BASE_URL}/api/predict/coordinates/{lat}/{lon}")
                if response.status_code == 200:
                    coord_data = response.json()
                    coord_risk = coord_data['risk_probability'] 
                    coord_rainfall = coord_data['current_rainfall']
                    coord_water = coord_data['current_water_level']
                    nearest_ref = coord_data.get('nearest_reference', 'N/A')
                    
                    # Calculate difference
                    risk_diff = abs(coord_risk - static_risk)
                    risk_diff_percent = risk_diff * 100
                    
                    status = "✅ Good" if risk_diff < 0.2 else "⚠️ High diff" if risk_diff < 0.5 else "❌ Too different"
                    
                    print(f"     ({lat}, {lon}): {coord_risk:.3f} risk ({coord_risk*100:.1f}%) | Diff: {risk_diff_percent:.1f}pp | {status}")
                    print(f"       Rainfall: {coord_rainfall:.2f}mm, Water: {coord_water:.2f}m | {nearest_ref}")
                else:
                    print(f"     ({lat}, {lon}): ❌ Failed ({response.status_code})")
            except Exception as e:
                print(f"     ({lat}, {lon}): ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Legend:")
    print("✅ Good: Risk difference < 20 percentage points")
    print("⚠️ High diff: Risk difference 20-50 percentage points") 
    print("❌ Too different: Risk difference > 50 percentage points")
    print("\nNote: Some variation is normal due to geographic factors,")
    print("but nearby locations should have similar risk levels.")

if __name__ == "__main__":
    test_prediction_consistency()
