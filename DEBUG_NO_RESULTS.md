# Debug: No Results Appearing

## Current Status

✅ **Backend:** Tests complete successfully (verified with `check_test_status.py`)
✅ **Database:** Results are stored
❌ **Frontend:** Results not appearing

## Root Cause Analysis

The issue is likely one of these:

### 1. API Response Format Mismatch
Frontend expects:
```json
{
  "status": "completed",
  "test_results": {...},
  "ai_recommendations": [...]
}
```

But might be getting something different.

### 2. Polling Catching Exceptions
The `except Exception` block might be catching errors silently.

### 3. Session State Not Updating
`st.session_state.test_results` might not be setting correctly.

## Quick Fix Steps

### Step 1: Add Debug Output

In `frontend/app.py`, find the polling section and add this RIGHT after getting results:

```python
results = asyncio.run(api_client.get_results(test_id))

# ADD THIS DEBUG OUTPUT
st.write("DEBUG - Got response!")
st.write(f"Status: {results.get('status')}")
st.write(f"Has test_results: {bool(results.get('test_results'))}")
st.write(f"Has AI recs: {len(results.get('ai_recommendations', []))}")
```

### Step 2: Check What's Being Returned

The debug output will show you exactly what the API is returning.

### Step 3: Check Backend Logs

Look for these lines in backend terminal:
```
[Test abc] ========== TEST EXECUTION COMPLETE ==========
[Test abc] Final Status: completed
[Test abc] AI Recommendations: 5 stored
```

If you see this, the backend is working correctly.

## Manual Test

Try this in Python to see what the API returns:

```python
import requests

# Replace with your actual test ID and token
TEST_ID = "your-test-id-here"
TOKEN = "your-access-token-here"

response = requests.get(
    f"http://localhost:8000/api/v1/get-results/{TEST_ID}",
    headers={"Authorization": f"Bearer {TOKEN}"}
)

print(response.status_code)
print(response.json())
```

## Simplified Polling Code

Here's a SUPER SIMPLE version that should work:

```python
# After starting test
progress_container = st.empty()

# Poll for up to 5 minutes
for i in range(100):
    with progress_container.container():
        st.info(f"⏳ Waiting for results... ({i+1}/100)")
    
    time.sleep(3)
    
    try:
        results = asyncio.run(api_client.get_results(test_id))
        
        # Check if complete
        if results.get('status') in ['completed', 'partial', 'failed']:
            test_data = results.get('test_results', {})
            
            # Check if we have ANY test data
            if test_data:
                # Save and show
                st.session_state.test_results = results
                with progress_container.container():
                    st.success("✅ Results ready!")
                time.sleep(1)
                st.rerun()
                break
    except:
        continue

# If we get here, timed out
if 'test_results' not in st.session_state:
    st.error("Timed out")
```

## What to Check

1. **Backend logs** - Is test completing?
2. **Database** - Run `python backend/check_test_status.py`
3. **API response** - What is `/get-results` returning?
4. **Frontend errors** - Check browser console (F12)
5. **Session state** - Is `st.session_state.test_results` being set?

## Most Likely Issues

### Issue 1: API Returns 401/403 (Auth Error)
**Solution:** Check if token is valid

### Issue 2: API Returns 404 (Test Not Found)
**Solution:** Check if test_id is correct

### Issue 3: API Returns 500 (Server Error)
**Solution:** Check backend logs for error

### Issue 4: Results Format Wrong
**Solution:** Add debug output to see actual format

### Issue 5: Exception Being Caught
**Solution:** Remove `except: continue` and see actual error

## Emergency Fix

If nothing works, try this MINIMAL version:

```python
if st.button("Start Test"):
    # Start test
    result = asyncio.run(api_client.run_test(...))
    test_id = result['test_id']
    
    # Wait with spinner
    with st.spinner("Running tests... This may take 2-3 minutes"):
        time.sleep(120)  # Wait 2 minutes
        
        # Get results
        results = asyncio.run(api_client.get_results(test_id))
        st.session_state.test_results = results
        st.rerun()
```

This removes all complexity and just waits a fixed time.

---

**Please share:**
1. Backend terminal output when running a test
2. What frontend shows (timeout? error? nothing?)
3. Browser console errors (F12 → Console tab)

This will help me identify the exact issue!
