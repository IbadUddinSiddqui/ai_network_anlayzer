# 🚀 Free Backend Deployment Guide

## Best Free Options for Your FastAPI Backend

### 🏆 **Top Recommendations**

---

## 1. **Render** (RECOMMENDED) ⭐

### Why Render?
- ✅ **750 hours/month free** (enough for 24/7)
- ✅ Auto-deploy from GitHub
- ✅ Built-in SSL/HTTPS
- ✅ Easy environment variables
- ✅ Automatic health checks
- ✅ Great for FastAPI/Python
- ✅ No credit card required

### Free Tier Limits:
- 512 MB RAM
- Shared CPU
- Sleeps after 15 min inactivity (wakes on request)
- 100 GB bandwidth/month

### Deployment Steps:

1. **Create `render.yaml` in project root:**
```yaml
services:
  - type: web
    name: ai-network-analyzer-backend
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
```

2. **Push to GitHub:**
```bash
git add .
git commit -m "Add Render config"
git push origin main
```

3. **Deploy on Render:**
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your repository
   - Render will auto-detect `render.yaml`
   - Add environment variables in dashboard
   - Click "Create Web Service"

4. **Your API will be live at:**
   `https://ai-network-analyzer-backend.onrender.com`

### Pros:
- ✅ Easiest setup
- ✅ Auto-deploy on git push
- ✅ Free SSL
- ✅ Good uptime

### Cons:
- ⚠️ Cold starts (15-30 seconds after sleep)
- ⚠️ Limited resources

---

## 2. **Railway** 💜

### Why Railway?
- ✅ **$5 free credit/month**
- ✅ No sleep/cold starts
- ✅ Better performance than Render
- ✅ Easy deployment
- ✅ Great developer experience

### Free Tier:
- $5 credit/month (≈ 500 hours)
- 512 MB RAM
- 1 GB disk
- Shared CPU

### Deployment Steps:

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login and init:**
```bash
railway login
railway init
```

3. **Create `railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

4. **Deploy:**
```bash
railway up
```

5. **Add environment variables:**
```bash
railway variables set SUPABASE_URL=your_url
railway variables set SUPABASE_SERVICE_KEY=your_key
railway variables set GEMINI_API_KEY=your_key
```

### Pros:
- ✅ No cold starts
- ✅ Better performance
- ✅ Fast deployments

### Cons:
- ⚠️ Only $5/month credit
- ⚠️ Requires credit card after trial

---

## 3. **Fly.io** 🪰

### Why Fly.io?
- ✅ **3 free VMs** (256MB RAM each)
- ✅ Global edge network
- ✅ No cold starts
- ✅ Good for APIs

### Free Tier:
- 3 shared-cpu-1x VMs
- 256 MB RAM each
- 3 GB persistent storage
- 160 GB bandwidth

### Deployment Steps:

1. **Install Fly CLI:**
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

2. **Login:**
```bash
fly auth login
```

3. **Create `fly.toml` in backend folder:**
```toml
app = "ai-network-analyzer"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"
  ENVIRONMENT = "production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

4. **Deploy:**
```bash
cd backend
fly launch
fly secrets set SUPABASE_URL=your_url
fly secrets set SUPABASE_SERVICE_KEY=your_key
fly secrets set GEMINI_API_KEY=your_key
fly deploy
```

### Pros:
- ✅ Global CDN
- ✅ No cold starts
- ✅ Good performance

### Cons:
- ⚠️ Requires credit card
- ⚠️ More complex setup

---

## 4. **PythonAnywhere** 🐍

### Why PythonAnywhere?
- ✅ **Always free tier**
- ✅ Python-focused
- ✅ No credit card needed
- ✅ Simple setup

### Free Tier:
- 512 MB disk space
- 1 web app
- Always-on (no sleep)
- Limited CPU

### Deployment Steps:

1. **Sign up:** https://www.pythonanywhere.com

2. **Upload code via Git:**
```bash
# In PythonAnywhere console
git clone https://github.com/yourusername/your-repo.git
cd your-repo/backend
```

3. **Install dependencies:**
```bash
pip install --user -r requirements.txt
```

4. **Configure Web App:**
   - Go to "Web" tab
   - Add new web app
   - Choose "Manual configuration"
   - Python 3.10
   - Set source code: `/home/yourusername/your-repo/backend`
   - Set WSGI file to point to your FastAPI app

5. **WSGI Configuration:**
```python
import sys
path = '/home/yourusername/your-repo/backend'
if path not in sys.path:
    sys.path.append(path)

from app.main import app as application
```

### Pros:
- ✅ Always free
- ✅ No credit card
- ✅ Python-focused

### Cons:
- ⚠️ Limited resources
- ⚠️ Manual setup
- ⚠️ Slower performance

---

## 5. **Vercel** (Serverless) ⚡

### Why Vercel?
- ✅ **Generous free tier**
- ✅ Serverless (no cold starts)
- ✅ Global CDN
- ✅ Easy deployment

### Free Tier:
- 100 GB bandwidth
- Unlimited requests
- Serverless functions

### Deployment Steps:

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Create `vercel.json` in project root:**
```json
{
  "builds": [
    {
      "src": "backend/app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/app/main.py"
    }
  ]
}
```

3. **Deploy:**
```bash
vercel
```

4. **Add environment variables:**
```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_KEY
vercel env add GEMINI_API_KEY
```

### Pros:
- ✅ Serverless (scales to zero)
- ✅ Fast global CDN
- ✅ Easy deployment

### Cons:
- ⚠️ 10-second timeout on free tier
- ⚠️ Not ideal for long-running tasks (speed tests)

---

## 📊 Comparison Table

| Platform | Free Tier | Cold Starts | Setup Difficulty | Best For |
|----------|-----------|-------------|------------------|----------|
| **Render** | 750 hrs/mo | Yes (15s) | ⭐ Easy | **Recommended** |
| **Railway** | $5/mo credit | No | ⭐⭐ Medium | Best performance |
| **Fly.io** | 3 VMs | No | ⭐⭐⭐ Hard | Global apps |
| **PythonAnywhere** | Always free | No | ⭐⭐ Medium | Simple Python apps |
| **Vercel** | Generous | No | ⭐ Easy | Serverless APIs |

---

## 🎯 **My Recommendation: Render**

For your AI Network Analyzer, I recommend **Render** because:

1. ✅ **Easiest to set up** - Just push to GitHub
2. ✅ **Auto-deploy** - Updates automatically
3. ✅ **Free SSL** - HTTPS out of the box
4. ✅ **Good for FastAPI** - Python-friendly
5. ✅ **No credit card** - Truly free to start

### Quick Start with Render:

```bash
# 1. Create render.yaml (already provided above)
# 2. Push to GitHub
git add .
git commit -m "Deploy to Render"
git push

# 3. Go to render.com and connect your repo
# 4. Add environment variables
# 5. Deploy!
```

---

## 🔧 Post-Deployment Setup

### Update Frontend to Use Deployed Backend:

1. **Update `frontend/.env`:**
```env
BACKEND_API_URL=https://your-app.onrender.com
```

2. **Update Streamlit secrets:**
```toml
# frontend/.streamlit/secrets.toml
BACKEND_API_URL = "https://your-app.onrender.com"
```

3. **Test the connection:**
```bash
curl https://your-app.onrender.com/health
```

---

## 🚨 Important Notes

### For Network Tests:
- ⚠️ **Ping tests** may not work on some platforms (require root)
- ⚠️ **Speed tests** take 20-30 seconds (may timeout on Vercel)
- ✅ **Best platforms**: Render, Railway, Fly.io (allow long-running tasks)

### Environment Variables Needed:
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...
SUPABASE_KEY=eyJhbGc...
GEMINI_API_KEY=AIzaSy...
ENVIRONMENT=production
```

---

## 📈 Scaling Later

When you outgrow free tier:

1. **Render**: $7/month (Starter)
2. **Railway**: Pay-as-you-go ($0.000463/GB-s)
3. **Fly.io**: $1.94/month per VM
4. **DigitalOcean**: $4/month (Droplet)
5. **AWS/GCP**: Pay-as-you-go

---

## 🎉 Ready to Deploy!

**Recommended Path:**
1. Start with **Render** (easiest, free)
2. If you need better performance → **Railway**
3. If you need global edge → **Fly.io**
4. If you need always-free → **PythonAnywhere**

**Next Steps:**
1. Choose a platform
2. Follow the deployment steps
3. Add environment variables
4. Update frontend URL
5. Test your deployed API!

---

**Need help with deployment? Let me know which platform you choose!** 🚀
