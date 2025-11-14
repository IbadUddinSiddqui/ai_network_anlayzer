# Testing Guide

## Quick Test Checklist

### ✅ Backend API Tests

1. **Health Check**
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "healthy", "database_connected": true, ...}`

2. **API Documentation**
- Open: http://localhost:8000/docs
- Verify all endpoints are listed
- Test endpoints using Swagger UI

3. **Authentication**
```bash
# This will fail without token (expected)
curl http://localhost:8000/api/v1/run-test
```
Expected: 401 Unauthorized

### ✅ Frontend Tests

1. **Access Dashboard**
- Open: http://localhost:8501
- Verify login/signup page loads

2. **Create Account**
- Click "Sign Up" tab
- Enter email and password
- Verify account creation

3. **Login**
- Enter credentials
- Verify redirect to dashboard

4. **Run Network Test**
- Enter target hosts: `8.8.8.8,1.1.1.1`
- Enter DNS servers: `8.8.8.8,1.1.1.1`
- Click "Start Network Test"
- Verify progress indicator
- Wait for completion (~60 seconds)

5. **View Results**
- Verify charts display
- Check AI recommendations appear
- Verify confidence scores shown

6. **Apply Optimization**
- Click "Apply Optimization" on a recommendation
- Verify success message

7. **Submit Feedback**
- Select rating
- Enter comment
- Click "Submit Feedback"
- Verify success message

### ✅ Database Tests

1. **Check Tables**
```sql
-- In Supabase SQL Editor
SELECT * FROM users LIMIT 5;
SELECT * FROM network_tests LIMIT 5;
SELECT * FROM ai_recommendations LIMIT 5;
```

2. **Verify RLS**
```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

### ✅ Integration Tests

**Full Workflow Test:**

1. Create new user account
2. Login with credentials
3. Run network test with custom hosts
4. Wait for test completion
5. Verify all 5 test types completed:
   - Ping results
   - Jitter results
   - Packet loss results
   - Speed results
   - DNS results
6. Verify AI recommendations generated
7. Apply one optimization
8. Submit feedback
9. Logout
10. Login again
11. Verify test history persists

## Manual Testing Scenarios

### Scenario 1: Happy Path
- User signs up
- Runs test with default settings
- Reviews recommendations
- Applies optimization
- Submits positive feedback

### Scenario 2: Custom Configuration
- User logs in
- Configures custom hosts: `1.1.1.1,9.9.9.9`
- Configures custom DNS: `1.1.1.1,8.8.8.8,208.67.222.222`
- Runs test
- Verifies custom configuration used

### Scenario 3: Error Handling
- Try invalid host: `invalid.host.name`
- Verify graceful error handling
- Check error messages are user-friendly

### Scenario 4: Multiple Tests
- Run 3 tests in sequence
- Verify all tests stored
- Check test history
- Verify recommendations for each test

## Performance Testing

### Load Test
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Expected: <100ms average response time
```

### Network Test Duration
- Typical: 30-60 seconds
- With slow network: up to 2 minutes
- Timeout: 5 minutes

### AI Analysis Duration
- Typical: 5-10 seconds
- With API delays: up to 30 seconds
- Fallback: Immediate (rule-based)

## Automated Testing

### Backend Unit Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov=core
```

### Expected Coverage
- Core modules: >80%
- API routes: >70%
- Repositories: >80%

## Common Issues & Solutions

### Issue: "Connection refused"
**Solution**: Ensure backend is running on port 8000

### Issue: "Authentication failed"
**Solution**: 
- Check Supabase credentials in .env
- Verify Supabase Auth is enabled
- Check JWT secret is correct

### Issue: "Test timeout"
**Solution**:
- Check internet connection
- Verify target hosts are reachable
- Increase timeout in config

### Issue: "AI analysis failed"
**Solution**:
- Check OpenAI API key is valid
- Verify API key has credits
- Check OpenAI API status

### Issue: "Database error"
**Solution**:
- Verify Supabase URL and key
- Check database schema is created
- Verify RLS policies are correct

## Test Data

### Sample Test Hosts
```
# Fast, reliable hosts
8.8.8.8          # Google DNS
1.1.1.1          # Cloudflare DNS
208.67.222.222   # OpenDNS

# For testing latency
google.com
cloudflare.com
github.com
```

### Sample DNS Servers
```
8.8.8.8          # Google
8.8.4.4          # Google Secondary
1.1.1.1          # Cloudflare
1.0.0.1          # Cloudflare Secondary
208.67.222.222   # OpenDNS
208.67.220.220   # OpenDNS Secondary
```

## Monitoring During Tests

### Backend Logs
```bash
# Watch backend logs
cd backend
uvicorn app.main:app --reload --log-level debug
```

### Database Activity
- Open Supabase Dashboard
- Go to Database → Logs
- Monitor queries during test

### API Metrics
- Response times
- Error rates
- Request counts
- Active connections

## Success Criteria

✅ **Backend**
- Health check returns 200
- All endpoints respond correctly
- Authentication works
- Database queries succeed

✅ **Frontend**
- Login/signup works
- Dashboard loads
- Tests can be initiated
- Results display correctly
- Charts render properly

✅ **Integration**
- End-to-end workflow completes
- Data persists correctly
- AI recommendations generated
- No critical errors

✅ **Performance**
- API response < 100ms
- Test completion < 2 minutes
- AI analysis < 30 seconds
- No memory leaks

## Debugging Tips

1. **Check Logs**
   - Backend: Console output
   - Frontend: Streamlit console
   - Database: Supabase logs

2. **Verify Environment**
   ```bash
   # Check environment variables
   env | grep SUPABASE
   env | grep OPENAI
   ```

3. **Test Components Individually**
   - Test network module alone
   - Test AI module with sample data
   - Test database connections

4. **Use API Documentation**
   - http://localhost:8000/docs
   - Test endpoints directly
   - Check request/response formats

## Reporting Issues

When reporting issues, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Error messages
5. Environment details
6. Logs (if applicable)

---

**Happy Testing! 🧪**
