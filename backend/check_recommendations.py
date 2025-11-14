"""
Check if AI recommendations are being stored for recent tests.
"""
import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

if not url or not key:
    print("❌ Missing SUPABASE credentials")
    sys.exit(1)

client = create_client(url, key)

print("=" * 60)
print("CHECKING AI RECOMMENDATIONS")
print("=" * 60)

# Get recent tests
tests = client.table("network_tests").select("id, status, created_at").order("created_at", desc=True).limit(5).execute()

for test in tests.data:
    test_id = test['id']
    print(f"\n📊 Test: {test_id}")
    print(f"   Status: {test['status']}")
    print(f"   Created: {test['created_at']}")
    
    # Get recommendations for this test
    recs = client.table("ai_recommendations").select("*").eq("test_id", test_id).execute()
    
    if recs.data:
        print(f"   ✅ Recommendations: {len(recs.data)}")
        for i, rec in enumerate(recs.data, 1):
            print(f"      {i}. [{rec['severity']}] {rec['agent_type']}: {rec['recommendation_text'][:60]}...")
    else:
        print(f"   ❌ NO RECOMMENDATIONS FOUND!")
        print(f"   ⚠️  This is the problem - recommendations should always exist")

print("\n" + "=" * 60)
print("If you see 'NO RECOMMENDATIONS FOUND', that's the issue!")
print("=" * 60)
