import sys
import os
import json

# Add web directory to path
sys.path.append(os.path.abspath('web'))

from app import app

def test_regeneration():
    print("Testing /api/regenerate_comparison endpoint...")
    
    with app.test_client() as client:
        response = client.post('/api/regenerate_comparison')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        if response.status_code == 200:
            print("SUCCESS: Endpoint returned 200 OK.")
            return True
        else:
            print("FAILURE: Endpoint returned error.")
            return False

if __name__ == "__main__":
    test_regeneration()
