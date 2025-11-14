# ✅ Deployment Checklist

## Pre-Deployment

- [ ] All code is committed to Git
- [ ] Environment variables are documented
- [ ] Dependencies are in `requirements.txt`
- [ ] Health check endpoint works (`/health`)
- [ ] CORS is configured for production
- [ ] Database connection is tested

## Files Created for Deployment

- [x] `render.yaml` - Render configuration
- [x] `Procfile` - Process file for Heroku/Railway
- [x] `runtime.txt` - Python version specification
- [x] `FREE_DEPLOYMENT_GUIDE.md` - Complete deployment guide

## Render Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Sign Up on Render
- Go to https://render.com
- Sign up with GitHub
- Authorize Render to access your repositories

### 3. Create New Web Service
- Click "New +" button
- Select "Web Service"
- Connect your repository
- Render will auto-detect `render.yaml`

### 4. Add Environment Variables
Go to Environment tab and add:

```
SUPABASE_URL=https://mvsmfyobnhqhkspmjeaw.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12c21meW9ibmhxaGtzcG1qZWF3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjUxOTMzOCwiZXhwIjoyMDc4MDk1MzM4fQ.fEL-6lVPJZGZy-oEySbwiWtnLSdE-ntxTEcMCoAN6uc
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12c21meW9ibmhxaGtzcG1qZWF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1MTkzMzgsImV4cCI6MjA3ODA5NTMzOH0.-5sZxtsvKRUpWPz0K7tUdKobD7-xiNW2z46-LKJLoRU
GEMINI_API_KEY=AIzaSyBjFurdyAeGywt321BJ7FVyIHJnynn4eBI
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase
```

### 5. Deploy
- Click "Create Web Service"
- Wait for build to complete (5-10 minutes)
- Your API will be live!

### 6. Get Your API URL
Your backend will be available at:
```
https://ai-network-analyzer-backend.onrender.com
```

## Post-Deployment

### 1. Test the API
```bash
# Test health endpoint
curl https://your-app.onrender.com/health

# Test API docs
# Visit: https://your-app.onrender.com/docs
```

### 2. Update Frontend
Update `frontend/.env`:
```env
BACKEND_API_URL=https://your-app.onrender.com
```

Update `frontend/.streamlit/secrets.toml`:
```toml
BACKEND_API_URL = "https://your-app.onrender.com"
```

### 3. Test Full Flow
- [ ] Login works
- [ ] Test selection works
- [ ] Tests execute successfully
- [ ] Results display correctly
- [ ] AI recommendations appear

## Troubleshooting

### Build Fails
- Check `requirements.txt` is correct
- Verify Python version in `runtime.txt`
- Check build logs in Render dashboard

### API Not Responding
- Check if service is running in Render dashboard
- Verify environment variables are set
- Check application logs

### CORS Errors
- Verify `CORS_ORIGINS` includes your frontend URL
- Check CORS middleware in `backend/app/main.py`

### Database Connection Fails
- Verify Supabase credentials
- Check if Supabase project is active
- Test connection from local machine first

### Tests Timeout
- Speed tests take 20-30 seconds (normal)
- Free tier may have slower performance
- Consider upgrading to paid tier if needed

## Monitoring

### Check Logs
```bash
# In Render dashboard
# Go to Logs tab
# Monitor real-time logs
```

### Check Metrics
- Response times
- Error rates
- Memory usage
- CPU usage

## Maintenance

### Update Deployment
```bash
# Just push to GitHub
git add .
git commit -m "Update feature"
git push origin main

# Render auto-deploys!
```

### Rollback
- Go to Render dashboard
- Click "Rollback" to previous version

## Cost Optimization

### Free Tier Limits
- 750 hours/month (enough for 24/7)
- Sleeps after 15 min inactivity
- 512 MB RAM
- Shared CPU

### Keep Service Awake
Use a cron job to ping your API every 10 minutes:
```bash
# Use cron-job.org or similar
curl https://your-app.onrender.com/health
```

### Upgrade When Needed
- Starter: $7/month (no sleep)
- Standard: $25/month (more resources)

## Security Checklist

- [ ] Environment variables are not in code
- [ ] HTTPS is enabled (automatic on Render)
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] Input validation is working
- [ ] JWT secrets are secure
- [ ] Database credentials are protected

## Performance Optimization

- [ ] Enable caching if needed
- [ ] Optimize database queries
- [ ] Use connection pooling
- [ ] Monitor response times
- [ ] Set up error tracking (Sentry)

## Success Criteria

✅ Backend is live and accessible
✅ Health check returns 200 OK
✅ API docs are accessible at /docs
✅ Frontend can connect to backend
✅ All tests execute successfully
✅ AI recommendations are generated
✅ No errors in logs

## Next Steps

1. Deploy frontend to Streamlit Cloud
2. Set up custom domain (optional)
3. Add monitoring (Sentry, LogRocket)
4. Set up analytics
5. Add more features!

---

**Your backend is ready to deploy!** 🚀

**Recommended**: Start with Render (easiest and free)

**Questions?** Check FREE_DEPLOYMENT_GUIDE.md for detailed instructions!
