"""
Quick test to verify all imports work correctly.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    print("1. Testing error_handling...")
    from core.utils.error_handling import retry_async, retry_sync, log_and_capture_exception
    print("   ✓ error_handling imports OK")
except Exception as e:
    print(f"   ✗ error_handling failed: {e}")
    sys.exit(1)

try:
    print("2. Testing validation...")
    from core.validation.test_results import TestResultValidator
    print("   ✓ validation imports OK")
except Exception as e:
    print(f"   ✗ validation failed: {e}")
    sys.exit(1)

try:
    print("3. Testing database models...")
    from core.database.models import TestStatus, IndividualTestStatus, TestStatusDetail, TestErrors
    print("   ✓ database models imports OK")
except Exception as e:
    print(f"   ✗ database models failed: {e}")
    sys.exit(1)

try:
    print("4. Testing test_runner...")
    from core.network.test_runner import NetworkTestRunner
    print("   ✓ test_runner imports OK")
except Exception as e:
    print(f"   ✗ test_runner failed: {e}")
    sys.exit(1)

try:
    print("5. Testing AI analyzer...")
    from core.ai import AIAnalyzer
    print("   ✓ AI analyzer imports OK")
except Exception as e:
    print(f"   ✗ AI analyzer failed: {e}")
    sys.exit(1)

try:
    print("6. Testing API routes...")
    from app.api.routes import tests
    print("   ✓ API routes imports OK")
except Exception as e:
    print(f"   ✗ API routes failed: {e}")
    sys.exit(1)

print("\n✅ All imports successful!")
print("\nYou can now start the backend with:")
print("  uvicorn app.main:app --reload")
