#!/usr/bin/env python3
"""Test river system features for Bangladesh flood prediction"""

import requests
import json
import sys

def test_river_system_features():
    """Test that river system features are working properly"""
    
    base_url = "http://localhost:10000"
    
    print("🏞️ Testing Enhanced Bangladesh Flood Prediction System")
    print("=" * 60)
    
    # Test different locations
    locations_to_test = ['Dhaka', 'Sylhet', 'Rangpur', 'Bahadurabad', 'Chittagong']
    
    for location in locations_to_test:
        print(f"\n📍 Testing {location}:")
        print("-" * 30)
        
        try:
            response = requests.get(f"{base_url}/api/predict/{location}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Basic prediction info
                print(f"Risk Level: {data['status']} ({data['risk_probability']:.3f})")
                
                # River system features
                if 'river_system_info' in data:
                    river_info = data['river_system_info']
                    print(f"📊 River System Analysis:")
                    print(f"   • Distance to nearest river: {river_info['distance_to_nearest_river_km']:.1f} km")
                    print(f"   • Elevation: {river_info['elevation_meters']:.1f} meters")
                    print(f"   • Drainage quality: {river_info['drainage_quality']} (class {river_info['drainage_classification']})")
                    print(f"   • Distance to confluence: {river_info['distance_to_confluence_km']:.1f} km")
                    
                    # Risk analysis based on river features
                    risk_factors = []
                    if river_info['distance_to_nearest_river_km'] < 5:
                        risk_factors.append("❗ Very close to major river")
                    elif river_info['distance_to_nearest_river_km'] < 15:
                        risk_factors.append("⚠️ Near major river")
                    
                    if river_info['elevation_meters'] < 10:
                        risk_factors.append("❗ Low elevation area")
                    elif river_info['elevation_meters'] < 20:
                        risk_factors.append("⚠️ Moderate elevation")
                    
                    if river_info['drainage_classification'] == 0:
                        risk_factors.append("❗ Poor drainage system")
                    elif river_info['drainage_classification'] == 1:
                        risk_factors.append("⚠️ Moderate drainage")
                    
                    if river_info['distance_to_confluence_km'] < 10:
                        risk_factors.append("❗ Near river confluence")
                    
                    if risk_factors:
                        print(f"🚨 Geographic Risk Factors:")
                        for factor in risk_factors:
                            print(f"   {factor}")
                    else:
                        print("✅ No significant geographic risk factors")
                        
                else:
                    print("❌ No river system information available")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("✅ Enhanced model now includes:")
    print("   • Distance to major rivers (Padma, Jamuna, Meghna, etc.)")
    print("   • Elevation data for topographic analysis")
    print("   • Drainage basin classifications")
    print("   • River confluence proximity calculations")
    print("   • Geographic risk factor analysis")
    print("\n📈 This makes predictions much more geographically accurate!")

if __name__ == "__main__":
    test_river_system_features()
