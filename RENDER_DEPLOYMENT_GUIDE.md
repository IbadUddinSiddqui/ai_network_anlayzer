# Complete Render Deployment Guide

## Table of Contents
1. [GitHub Setup](#github-setup)
2. [Prepare Backend for Deployment](#prepare-backend)
3. [Deploy to Render](#deploy-to-render)
4. [Environment Variables](#environment-variables)
5. [Testing Deployment](#testing)
6. [Troubleshooting](#troubleshooting)

---

## GitHub Setup

### Option 1: Deploy Whole Repo (Recommended) ✅

**Advantages:**
- Easier to manage
- Single repository for frontend and backend
- Better version control
- Simpler CI/CD setup

**Steps:**

1. **Initialize Git (if not already done):**
```bash
git init
```

2. **Check your .gitignore:**
Make sure it includes:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
backend/.venv/
backend/.venv copy/

# Environment variables
.env
backend/.env
frontend/.env
*.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

3. **Add all files:**
```bash
git add .
git commit -m "Initial commit - AI Network Analyzer"
```

4. **Create GitHub repository:**
- Go to https://github.com/new
- Name it: `ai-network-analyzer` (or your preferred name)
- Don't initialize with README (you already have one)
- Click "Create repository"

5. **Push to GitHub:**
```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-network-analyzer.git
git branch -M main
git push -u origin main
```

### Option 2: Separate Backend Repo (Alternative)

**Only if you want backend completely separate:**

```bash
cd backend
git init
git add .
git commit -m "Backend - AI Network Analyzer"
# Create separate repo on GitHub
git remote add origin https://github.com/YOUR_USERNAME/ai-network-analyzer-backend.git
git push -u origin main
```

---

## Prepare Backend for Deployment

### 1. Create/Update `backend/requirements.txt`

Make sure it includes all dependencies:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
supabase==2.0.3
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
speedtest-cli==2.1.3
dnspython==2.4.2
google-generativeai==0.3.1
requests==2.31.0
```

### 2. Create `backend/Procfile` (if not exists)

```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**OR** if deploying from root:

```
web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

### 3. Create `backend/render.yaml` (Optional - for Infrastructure as Code)

```yaml
services:
  - type: web
    name: ai-network-analyzer-backend
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
```

### 4. Update `backend/app/main.py` for Production

Check your CORS settings:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="AI Network Analyzer API",
    description="Backend API for network testing and AI analysis",
    version="1.0.0"
)

# CORS - Update for production
origins = [
    "http://localhost:8501",  # Local Streamlit
    "http://localhost:3000",  # Local development
    "https://your-frontend-app.streamlit.app",  # Production frontend
    "*"  # Remove this in production, add specific domains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your routes here...
```

### 5. Create `backend/runtime.txt` (Optional)

```
python-3.11.0
```

---

## Deploy to Render

### Step 1: Sign Up / Log In

1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repositories

### Step 2: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select your repository: `ai-network-analyzer`

### Step 3: Configure Service

**Basic Settings:**
- **Name:** `ai-network-analyzer-backend` (or your choice)
- **Region:** Choose closest to you (e.g., Oregon)
- **Branch:** `main`
- **Root Directory:** Leave empty (if whole repo) or `backend` (if separate)
- **Runtime:** `Python 3`
- **Build Command:**
  ```bash
  pip install -r backend/requirements.txt
  ```
  OR if root directory is `backend`:
  ```bash
  pip install -r requirements.txt
  ```

- **Start Command:**
  ```bash
  uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
  ```
  OR if root directory is `backend`:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select **"Free"** (for testing)
- Note: Free tier sleeps after 15 min of inactivity

### Step 4: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
JWT_SECRET_KEY=your_jwt_secret_key
GEMINI_API_KEY=your_gemini_api_key
PYTHON_VERSION=3.11.0
```

**To get these values:**
- Copy from your `backend/.env` file
- Or from Supabase dashboard and Google AI Studio

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Watch the logs for any errors

---

## Environment Variables

### Required Variables

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `SUPABASE_URL` | Your Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Anon/public key | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_KEY` | Service role key (secret!) | Supabase Dashboard → Settings → API |
| `JWT_SECRET_KEY` | Secret for JWT tokens | Generate: `openssl rand -hex 32` |
| `GEMINI_API_KEY` | Google Gemini API key | Google AI Studio |

### Generate JWT Secret

**On Windows (PowerShell):**
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**On Mac/Linux:**
```bash
openssl rand -hex 32
```

---

## Testing Deployment

### 1. Check Deployment Status

- Go to your Render dashboard
- Check the **"Logs"** tab
- Look for: `Application startup complete`

### 2. Test API Endpoint

Your backend URL will be: `https://your-service-name.onrender.com`

**Test health endpoint:**
```bash
curl https://your-service-name.onrender.com/
```

**Test docs:**
Open in browser: `https://your-service-name.onrender.com/docs`

### 3. Update Frontend

Update `frontend/.env` or `frontend/.streamlit/secrets.toml`:

```toml
BACKEND_URL = "https://your-service-name.onrender.com"
```

### 4. Test Full Flow

1. Start frontend locally:
   ```bash
   cd frontend
   streamlit run app.py
   ```

2. Try to:
   - Sign up / Log in
   - Run a network test
   - View results

---

## Troubleshooting

### Common Issues

#### 1. Build Fails - "Module not found"

**Problem:** Missing dependencies

**Solution:**
```bash
# Update requirements.txt
pip freeze > backend/requirements.txt

# Commit and push
git add backend/requirements.txt
git commit -m "Update dependencies"
git push
```

#### 2. App Crashes - "Port already in use"

**Problem:** Wrong start command

**Solution:** Make sure start command uses `$PORT`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 3. CORS Errors

**Problem:** Frontend can't connect to backend

**Solution:** Update CORS in `backend/app/main.py`:
```python
origins = [
    "https://your-frontend-app.streamlit.app",
    "http://localhost:8501",
]
```

#### 4. Environment Variables Not Working

**Problem:** Variables not loaded

**Solution:**
- Check spelling in Render dashboard
- Restart service after adding variables
- Check logs for "KeyError" messages

#### 5. Database Connection Fails

**Problem:** Can't connect to Supabase

**Solution:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Check Supabase project is active
- Verify RLS policies allow service role

#### 6. Free Tier Sleeps

**Problem:** First request takes 30+ seconds

**Solution:**
- Upgrade to paid tier ($7/month)
- Or use a keep-alive service (e.g., UptimeRobot)
- Or accept the cold start delay

### Viewing Logs

**In Render Dashboard:**
1. Go to your service
2. Click **"Logs"** tab
3. Look for errors in red

**Common log messages:**
- ✅ `Application startup complete` - Good!
- ❌ `ModuleNotFoundError` - Missing dependency
- ❌ `KeyError: 'SUPABASE_URL'` - Missing env var
- ❌ `Connection refused` - Database issue

---

## Post-Deployment Checklist

- [ ] Backend deployed successfully
- [ ] All environment variables set
- [ ] API docs accessible at `/docs`
- [ ] Health check endpoint working
- [ ] Frontend can connect to backend
- [ ] Authentication working
- [ ] Network tests running
- [ ] AI recommendations generating
- [ ] Database queries working
- [ ] CORS configured correctly

---

## Deployment Commands Reference

### Push Updates

```bash
# Make changes
git add .
git commit -m "Your commit message"
git push

# Render will auto-deploy
```

### Manual Redeploy

In Render dashboard:
1. Go to your service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

### View Logs

```bash
# In Render dashboard, click "Logs" tab
# Or use Render CLI:
render logs -s your-service-name
```

---

## Next Steps

1. **Deploy Frontend to Streamlit Cloud:**
   - See `STREAMLIT_DEPLOYMENT_GUIDE.md`

2. **Set Up Custom Domain (Optional):**
   - Render Settings → Custom Domain
   - Add your domain
   - Update DNS records

3. **Monitor Performance:**
   - Render Dashboard → Metrics
   - Set up alerts

4. **Upgrade Plan (Optional):**
   - Free tier: Sleeps after 15 min
   - Starter ($7/mo): Always on
   - Standard ($25/mo): More resources

---

## Cost Breakdown

### Free Tier (Render)
- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ 512 MB RAM
- ⚠️ Shared CPU

### Paid Tier ($7/month)
- ✅ Always on
- ✅ 512 MB RAM
- ✅ Shared CPU
- ✅ No sleep

### Recommended Setup
- **Backend:** Render Free (or $7/mo if you need always-on)
- **Frontend:** Streamlit Cloud Free
- **Database:** Supabase Free
- **AI:** Google Gemini Free tier

**Total Cost:** $0 - $7/month

---

## Security Best Practices

1. **Never commit `.env` files**
   - Already in `.gitignore`
   - Use Render environment variables

2. **Use strong JWT secret**
   - Generate with `openssl rand -hex 32`
   - Never share or commit

3. **Protect service key**
   - `SUPABASE_SERVICE_KEY` is powerful
   - Only use in backend
   - Never expose to frontend

4. **Update CORS**
   - Remove `"*"` in production
   - Only allow your frontend domain

5. **Enable HTTPS**
   - Render provides this automatically
   - Always use `https://` URLs

---

## Support

**Render Documentation:**
- https://render.com/docs

**Common Issues:**
- https://render.com/docs/troubleshooting

**Community:**
- https://community.render.com

**Your Project:**
- Check logs in Render dashboard
- Review error messages
- Test locally first

---

## Quick Reference

**Your URLs:**
- Backend: `https://your-service-name.onrender.com`
- API Docs: `https://your-service-name.onrender.com/docs`
- Frontend: `https://your-app.streamlit.app`

**Important Files:**
- `backend/requirements.txt` - Dependencies
- `backend/app/main.py` - Main application
- `Procfile` or start command - How to run
- `.gitignore` - What not to commit

**Key Commands:**
```bash
# Deploy updates
git push

# Check logs
# (Use Render dashboard)

# Test locally
cd backend
uvicorn app.main:app --reload
```

Good luck with your deployment! 🚀
