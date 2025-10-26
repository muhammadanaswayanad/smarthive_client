#!/usr/bin/env python3
"""
Test script to verify SmartHive warning system works correctly
"""

import requests
import json

# Test endpoint URL
BASE_URL = "http://localhost:8069"
WARNING_ENDPOINT = f"{BASE_URL}/smarthive_client/warning_data"

def test_warning_endpoint():
    """Test the warning data endpoint"""
    print("Testing SmartHive warning data endpoint...")
    
    try:
        # For JSON endpoints, we need to send a POST request
        response = requests.post(
            WARNING_ENDPOINT,
            headers={
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            json={},
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response data: {json.dumps(data, indent=2)}")
                
                if data.get('show_warning'):
                    print("✅ Warning system is active!")
                    print(f"Message: {data.get('message', 'No message')}")
                    print(f"Payment Status: {data.get('payment_status', 'Unknown')}")
                    print(f"Outstanding Amount: {data.get('outstanding_amount', 0)}")
                    if data.get('block_reason'):
                        print(f"🚫 BLOCKED: {data.get('block_reason')}")
                else:
                    print("ℹ️  No warnings configured")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("Make sure Odoo is running on localhost:8069")

if __name__ == "__main__":
    test_warning_endpoint()