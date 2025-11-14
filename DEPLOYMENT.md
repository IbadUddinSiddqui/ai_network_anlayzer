# Deployment Guide

## Production Deployment on Render

### Prerequisites
- GitHub account
- Render account (https://render.com)
- Supabase project
- OpenAI API key

### Step 1: Prepare Repository

1. Push code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. **Create New Web Service**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

2. **Configure Service**
   - Name: `ai-network-analyzer-api`
   - Region: Choose closest to your users
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```
   SUPABASE_URL=<your-supabase-url>
   SUPABASE_KEY=<your-supabase-key>
   OPENAI_API_KEY=<your-openai-key>
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   CORS_ORIGINS=https://your-frontend-url.streamlit.app
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL (e.g., https://your-app.onrender.com)

### Step 3: Deploy Frontend to Streamlit Cloud

1. **Prepare Streamlit Secrets**
   - Create `.streamlit/secrets.toml` (don't commit this!)
   ```toml
   SUPABASE_URL = "your-supabase-url"
   SUPABASE_KEY = "your-supabase-key"
   BACKEND_API_URL = "https://your-backend.onrender.com"
   ```

2. **Deploy to Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select your repository
   - Set main file path: `frontend/app.py`
   - Add secrets from above
   - Click "Deploy"

### Step 4: Configure Database

1. **Run Schema**
   - Open Supabase SQL Editor
   - Copy contents of `database/schema.sql`
   - Execute the SQL

2. **Verify Tables**
   - Check that all 5 tables are created
   - Verify RLS policies are active

### Step 5: Test Deployment

1. **Health Check**
   ```bash
   curl https://your-backend.onrender.com/health
   ```

2. **Test Frontend**
   - Open your Streamlit app URL
   - Create an account
   - Run a network test
   - Verify AI recommendations appear

## Environment Variables Reference

### Backend (.env)
```bash
# Required
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
OPENAI_API_KEY=sk-xxx

# Optional
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-frontend.streamlit.app
RATE_LIMIT_PER_MINUTE=100
```

### Frontend (.streamlit/secrets.toml)
```toml
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "your-anon-key"
BACKEND_API_URL = "https://your-backend.onrender.com"
```

## Monitoring

### Health Checks
- Backend: `https://your-backend.onrender.com/health`
- Check database connectivity
- Monitor response times

### Logs
- **Render**: View logs in Render dashboard
- **Streamlit**: View logs in Streamlit Cloud dashboard
- **Supabase**: Check database logs in Supabase dashboard

### Metrics to Monitor
- API response times
- Error rates
- Database query performance
- OpenAI API usage
- User activity

## Troubleshooting

### Backend Issues

**Problem**: 500 Internal Server Error
- Check environment variables are set correctly
- Verify Supabase connection
- Check logs for detailed error messages

**Problem**: Authentication fails
- Verify SUPABASE_JWT_SECRET is set
- Check token format
- Verify RLS policies in Supabase

### Frontend Issues

**Problem**: Can't connect to backend
- Verify BACKEND_API_URL is correct
- Check CORS settings in backend
- Verify backend is running

**Problem**: Login fails
- Check Supabase Auth is enabled
- Verify email confirmation settings
- Check Supabase logs

### Database Issues

**Problem**: Tables not found
- Run schema.sql in Supabase SQL Editor
- Verify all tables are created
- Check RLS policies are enabled

## Scaling Considerations

### Horizontal Scaling
- Render automatically scales based on load
- Consider upgrading to paid plan for better performance

### Database Optimization
- Add indexes for frequently queried columns
- Monitor query performance
- Consider read replicas for high traffic

### Cost Management
- Monitor OpenAI API usage
- Implement caching for AI responses
- Set rate limits appropriately

## Security Checklist

- [ ] All secrets stored in environment variables
- [ ] HTTPS enabled on all endpoints
- [ ] CORS configured with specific origins
- [ ] RLS policies enabled in Supabase
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Error messages don't expose sensitive info
- [ ] Regular security updates

## Backup Strategy

### Database Backups
- Supabase provides automatic daily backups
- Consider manual backups before major changes
- Test restore procedures regularly

### Code Backups
- GitHub serves as primary backup
- Tag releases for easy rollback
- Document deployment procedures

## Support

For issues:
1. Check logs in Render/Streamlit dashboards
2. Review Supabase logs
3. Check GitHub Issues
4. Contact support team
