# Troubleshooting Guide: Tests Running But No Results

## 🔍 Issue
- Backend shows test is running
- Frontend shows "completed" but no results appear
- Tests seem to run indefinitely

## 🛠️ Quick Fixes

### 1. Check Database Migration
The most common issue is missing database columns.

**Run this in Supabase SQL Editor:**
```sql
-- Check if columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'network_tests' 
AND column_name IN ('test_status', 'errors');
```

**If columns are missing, run:**
```sql
ALTER TABLE network_tests 
ADD COLUMN IF NOT EXISTS test_status JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS errors JSONB DEFAULT '{}';
```

### 2. Check Test Status in Database
While a test is running, check what's in the database:

```bash
cd backend
python check_test_status.py
```

This will show you:
- Recent test IDs
- Their status (running/completed/partial/failed)
- What results are stored
- Any errors

### 3. Check Backend Logs
Look for these patterns in backend terminal:

**Good (test completing):**
```
[Test abc-123] Network tests completed. Overall status: completed
[Test abc-123] Individual test status: {'ping': 'success', ...}
[Test abc-123] AI analysis completed successfully
[Test abc-123] Stored 5 recommendations
[Test abc-123] Test execution completed successfully
```

**Bad (test stuck):**
```
[Test abc-123] Running ping tests...
[Test abc-123] Running ping tests...
[Test abc-123] Running ping tests...
(repeating forever)
```

### 4. Check Frontend Polling
The frontend now shows debug info every 10 attempts:
- "🔍 Checking status... Current: running"
- "⏳ Waiting for test to complete..."

If you see "Current: completed" but no results, there's a frontend issue.
If you see "Current: running" forever, the backend test is stuck.

### 5. Common Issues & Solutions

#### Issue: "Could not find 'errors' column"
**Solution:** Run database migration (see #1 above)

#### Issue: Test runs forever
**Possible causes:**
- Speed test is very slow (can take 30-60 seconds)
- Packet loss test requires admin privileges
- Network connectivity issues

**Solution:**
- Check backend logs for specific errors
- Try running with fewer tests enabled
- Run backend with admin privileges

#### Issue: Frontend shows "completed" but no results
**Possible causes:**
- Frontend polling stopped too early
- Database not updated yet
- API response format mismatch

**Solution:**
- Refresh the page and check again
- Run `check_test_status.py` to see database state
- Check browser console for errors (F12)

#### Issue: AI recommendations missing
**Possible causes:**
- Gemini API key not set
- API rate limit exceeded
- AI analysis failed

**Solution:**
- Check `GEMINI_API_KEY` environment variable
- Look for "Using fallback recommendations" in logs
- Fallback recommendations should still appear

### 6. Manual Test Flow

Test the complete flow manually:

**Step 1: Start backend**
```bash
cd backend
uvicorn app.main:app --reload
```

**Step 2: In another terminal, check database**
```bash
cd backend
python check_test_status.py
```

**Step 3: Start frontend**
```bash
cd frontend
streamlit run app.py
```

**Step 4: Run a simple test**
- Select only "Ping" test
- Use default host (8.8.8.8)
- Click "Start Network Test"
- Watch backend logs

**Step 5: Check results**
- Wait for "Test execution completed successfully" in backend
- Run `check_test_status.py` again
- Frontend should show results

### 7. Reset and Try Again

If all else fails:

```bash
# Stop backend (Ctrl+C)
# Stop frontend (Ctrl+C)

# Clear any stuck processes
# Windows:
taskkill /F /IM python.exe

# Restart backend
cd backend
uvicorn app.main:app --reload

# Restart frontend
cd frontend
streamlit run app.py
```

### 8. Check Specific Test Times

Expected test durations:
- **Ping**: 1-2 seconds per host
- **Jitter**: 5-10 seconds
- **Packet Loss**: 10-30 seconds (depends on packet_count)
- **Speed**: 30-60 seconds (slowest!)
- **DNS**: 2-5 seconds per server
- **AI Analysis**: 5-15 seconds

**Total for all tests: 1-2 minutes**

If tests take longer than 3 minutes, something is wrong.

### 9. Enable Debug Mode

Add this to your backend `.env`:
```
LOG_LEVEL=DEBUG
```

Restart backend and you'll see much more detailed logs.

### 10. Quick Diagnostic Commands

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if you can create a test
curl -X POST http://localhost:8000/api/v1/run-test \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target_hosts":["8.8.8.8"],"dns_servers":["8.8.8.8"]}'

# Check test results
curl http://localhost:8000/api/v1/get-results/TEST_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🆘 Still Not Working?

1. Check backend logs for the exact error
2. Run `check_test_status.py` to see database state
3. Check browser console (F12) for frontend errors
4. Verify database migration ran successfully
5. Try with only one test enabled (Ping)

The most common issue is **missing database columns** - make sure you ran the migration!
