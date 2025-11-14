"""
Simple test to check if backend is working.
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get the most recent test from your output
# Replace with actual test ID from your database check
TEST_ID = "e2509132-ac09-46f3-a63a-a1e1106ec9be"  # From your earlier check

backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000')

print("=" * 60)
print("TESTING BACKEND API")
print("=" * 60)

# You'll need a valid token - get it from your frontend session
print("\n⚠️  You need to provide an access token")
print("Get it from Streamlit session or login")
print("\nFor now, testing without auth (will fail if auth required)...\n")

try:
    response = requests.get(f"{backend_url}/api/v1/get-results/{TEST_ID}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ API Response:")
        print(f"   Status: {data.get('status')}")
        print(f"   Test Results: {bool(data.get('test_results'))}")
        print(f"   AI Recommendations: {len(data.get('ai_recommendations', []))}")
        
        if data.get('test_results'):
            test_data = data['test_results']
            print(f"\n   Test Data:")
            print(f"      Ping: {len(test_data.get('ping_results', []))} hosts")
            print(f"      Speed: {'Yes' if test_data.get('speed_results') else 'No'}")
            print(f"      Packet Loss: {'Yes' if test_data.get('packet_loss_results') else 'No'}")
            print(f"      DNS: {len(test_data.get('dns_results', []))} servers")
            print(f"      Jitter: {'Yes' if test_data.get('jitter_results') else 'No'}")
    else:
        print(f"\n❌ Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Failed to connect: {e}")

print("\n" + "=" * 60)
