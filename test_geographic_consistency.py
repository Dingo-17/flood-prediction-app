#!/usr/bin/env python3
"""
Test script to verify geographic consistency between static locations and nearby coordinates
"""

import requests
import json
from datetime import datetime

def test_geographic_consistency():
    """Test that nearby locations have similar flood risk predictions"""
    
    base_url = "http://127.0.0.1:10000"
    
    # Test locations with their coordinates
    test_cases = [
        {
            'name': 'Chittagong',
            'static_coords': (22.3569, 91.7832),
            'nearby_points': [
                (22.360, 91.785, "3km NE"),
                (22.350, 91.780, "5km SW"), 
                (22.366, 91.783, "1km N"),
                (22.347, 91.783, "1km S")
            ]
        },
        {
            'name': 'Dhaka', 
            'static_coords': (23.8103, 90.4125),
            'nearby_points': [
                (23.815, 90.415, "2km NE"),
                (23.805, 90.410, "3km SW"),
                (23.820, 90.412, "1km N"),
                (23.800, 90.413, "1km S")
            ]
        },
        {
            'name': 'Sylhet',
            'static_coords': (24.8949, 91.8687),
            'nearby_points': [
                (24.900, 91.870, "2km NE"),
                (24.890, 91.865, "3km SW")
            ]
        }
    ]
    
    print("🗺️  Geographic Consistency Test")
    print("=" * 60)
    
    for case in test_cases:
        print(f"\n📍 Testing {case['name']} region:")
        
        # Get static location prediction
        try:
            response = requests.get(f"{base_url}/api/predict/realtime/{case['name']}", timeout=5)
            if response.status_code == 200:
                static_data = response.json()
                static_risk = static_data.get('risk_probability', 0)
                print(f"  Static location: {static_risk:.3f} ({static_risk*100:.1f}%)")
            else:
                print(f"  Static location: ERROR {response.status_code}")
                continue
        except Exception as e:
            print(f"  Static location: EXCEPTION {e}")
            continue
            
        # Test nearby coordinates
        coordinate_risks = []
        for lat, lon, description in case['nearby_points']:
            try:
                response = requests.get(f"{base_url}/api/predict/coordinates/{lat}/{lon}", timeout=5)
                if response.status_code == 200:
                    coord_data = response.json()
                    coord_risk = coord_data.get('risk_probability', 0)
                    coordinate_risks.append(coord_risk)
                    print(f"  {description:8}: {coord_risk:.3f} ({coord_risk*100:.1f}%)")
                else:
                    print(f"  {description:8}: ERROR {response.status_code}")
            except Exception as e:
                print(f"  {description:8}: EXCEPTION {e}")
        
        # Check consistency
        if coordinate_risks:
            all_risks = [static_risk] + coordinate_risks
            min_risk = min(all_risks)
            max_risk = max(all_risks)
            risk_range = max_risk - min_risk
            avg_risk = sum(all_risks) / len(all_risks)
            
            print(f"  📊 Analysis:")
            print(f"     Range: {min_risk:.3f} - {max_risk:.3f} ({risk_range:.3f} spread)")
            print(f"     Average: {avg_risk:.3f}")
            
            # Check if range is reasonable (should be < 10% difference for nearby locations)
            if risk_range < 0.10:  # Less than 10% spread
                print(f"     ✅ CONSISTENT: Low geographic variation")
            elif risk_range < 0.20:  # Less than 20% spread  
                print(f"     ⚠️  MODERATE: Some geographic variation")
            else:
                print(f"     ❌ INCONSISTENT: High geographic variation")
    
    print(f"\n🕐 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_geographic_consistency()
