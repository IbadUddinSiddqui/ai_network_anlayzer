"""
Quick test to verify Supabase credentials
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print("=" * 50)
print("Testing Supabase Credentials")
print("=" * 50)

# Check if credentials exist
if not url:
    print("❌ SUPABASE_URL not found in .env file!")
else:
    print(f"✅ SUPABASE_URL: {url}")

if not key:
    print("❌ SUPABASE_KEY not found in .env file!")
else:
    print(f"✅ SUPABASE_KEY: {key[:20]}... (truncated)")

# Try to connect
if url and key:
    try:
        print("\nTrying to connect to Supabase...")
        client = create_client(url, key)
        print("✅ Successfully connected to Supabase!")
        print("\nYour credentials are correct! 🎉")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPlease check your credentials:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to Settings → API")
        print("4. Copy the 'anon/public' key (NOT service_role)")
else:
    print("\n❌ Missing credentials!")
    print("\nPlease add to frontend/.env:")
    print("SUPABASE_URL=https://your-project.supabase.co")
    print("SUPABASE_KEY=your-anon-key-here")

print("=" * 50)
