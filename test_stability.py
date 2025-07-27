#!/usr/bin/env python3
"""
Test script to verify prediction stability - no more wild fluctuations!
"""

import requests
import json
import time
from datetime import datetime

def test_prediction_stability():
    """Test that predictions are stable across multiple rapid requests"""
    
    base_url = "http://127.0.0.1:10000"
    locations = ["Dhaka", "Sylhet", "Chittagong", "Rajshahi", "Khulna"]
    
    print("🧪 Testing Prediction Stability")
    print("=" * 50)
    
    for location in locations:
        print(f"\n📍 Testing {location}:")
        predictions = []
        
        # Make 5 rapid requests
        for i in range(5):
            try:
                response = requests.get(f"{base_url}/api/predict/realtime/{location}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    risk_prob = data.get('risk_probability', 0)
                    status = data.get('status', 'UNKNOWN')
                    predictions.append((risk_prob, status))
                    print(f"  Request {i+1}: {risk_prob:.3f} ({status})")
                else:
                    print(f"  Request {i+1}: ERROR {response.status_code}")
            except Exception as e:
                print(f"  Request {i+1}: EXCEPTION {e}")
            
            time.sleep(0.5)  # Small delay between requests
        
        # Check stability
        if predictions:
            risk_probs = [p[0] for p in predictions]
            statuses = [p[1] for p in predictions]
            
            # All predictions should be identical
            if len(set(risk_probs)) == 1 and len(set(statuses)) == 1:
                print(f"  ✅ STABLE: All predictions identical")
            else:
                print(f"  ❌ UNSTABLE: Varying predictions detected!")
                print(f"     Risk probabilities: {set(risk_probs)}")
                print(f"     Statuses: {set(statuses)}")
        
    print(f"\n🕐 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_prediction_stability()
