"""
Quick script to check test status in database.
Run this while a test is running to see what's happening.
"""
import os
import sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

if not url or not key:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY")
    sys.exit(1)

# Create client
client = create_client(url, key)

print("=" * 60)
print("CHECKING RECENT TESTS")
print("=" * 60)

# Get recent tests
try:
    response = client.table("network_tests").select("*").order("created_at", desc=True).limit(5).execute()
    
    if not response.data:
        print("\n❌ No tests found in database")
    else:
        for i, test in enumerate(response.data, 1):
            print(f"\n📊 Test {i}:")
            print(f"   ID: {test['id']}")
            print(f"   Status: {test['status']}")
            print(f"   Created: {test['created_at']}")
            
            # Check test_status
            if 'test_status' in test and test['test_status']:
                print(f"   Individual Status: {test['test_status']}")
            else:
                print(f"   Individual Status: Not set")
            
            # Check errors
            if 'errors' in test and test['errors']:
                has_errors = any(v for v in test['errors'].values() if v)
                if has_errors:
                    print(f"   Errors: {test['errors']}")
                else:
                    print(f"   Errors: None")
            else:
                print(f"   Errors: Not set")
            
            # Check results
            print(f"   Ping Results: {len(test.get('ping_results', []))} hosts")
            print(f"   Jitter: {'Yes' if test.get('jitter_results') else 'No'}")
            print(f"   Packet Loss: {'Yes' if test.get('packet_loss_results') else 'No'}")
            print(f"   Speed: {'Yes' if test.get('speed_results') else 'No'}")
            print(f"   DNS: {len(test.get('dns_results', []))} servers")
            
            print(f"   " + "-" * 50)

except Exception as e:
    print(f"\n❌ Error querying database: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ Check complete")
print("=" * 60)
