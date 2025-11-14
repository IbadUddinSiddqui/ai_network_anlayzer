# Quick Deployment Checklist

## 🚀 Deploy in 15 Minutes

### Step 1: GitHub (5 minutes)

```bash
# In your project root
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-network-analyzer.git
git push -u origin main
```

**✅ Checkpoint:** Your code is on GitHub

---

### Step 2: Prepare Backend (2 minutes)

1. **Check `backend/requirements.txt` exists**
   - Should list all Python packages

2. **Create `Procfile` in root** (if not exists):
   ```
   web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Verify `.gitignore` excludes:**
   ```
   .env
   backend/.env
   .venv/
   backend/.venv/
   __pycache__/
   ```

**✅ Checkpoint:** Backend is ready for deployment

---

### Step 3: Deploy to Render (5 minutes)

1. **Go to https://render.com**
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select `ai-network-analyzer`

3. **Configure:**
   ```
   Name: ai-network-analyzer-backend
   Region: Oregon (or closest)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3
   
   Build Command:
   pip install -r backend/requirements.txt
   
   Start Command:
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   
   Instance Type: Free
   ```

4. **Add Environment Variables:**
   Click "Advanced" → Add these:
   ```
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   SUPABASE_SERVICE_KEY=your_service_key
   JWT_SECRET_KEY=your_jwt_secret
   GEMINI_API_KEY=your_gemini_key
   ```

5. **Click "Create Web Service"**

**✅ Checkpoint:** Backend is deploying (wait 5-10 min)

---

### Step 4: Test Deployment (3 minutes)

1. **Wait for "Live" status** in Render dashboard

2. **Test API:**
   - Open: `https://your-service-name.onrender.com/docs`
   - Should see FastAPI docs

3. **Update Frontend:**
   Edit `frontend/.streamlit/secrets.toml`:
   ```toml
   BACKEND_URL = "https://your-service-name.onrender.com"
   ```

4. **Test locally:**
   ```bash
   cd frontend
   streamlit run app.py
   ```
   - Try signing up
   - Run a test

**✅ Checkpoint:** Everything works!

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure you have:

- [ ] GitHub account
- [ ] Render account (free)
- [ ] Supabase project set up
- [ ] Gemini API key
- [ ] All environment variables ready
- [ ] Code committed to Git
- [ ] `.env` files in `.gitignore`

---

## 🔑 Environment Variables You Need

Copy these from your local `.env` files:

```bash
# From backend/.env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
JWT_SECRET_KEY=your_secret_key
GEMINI_API_KEY=AIzaSy...
```

**Generate JWT Secret:**
```bash
# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Mac/Linux
openssl rand -hex 32
```

---

## 🎯 Recommended Approach

### ✅ Deploy Whole Repo (Easiest)

**Pros:**
- Single repository
- Easier to manage
- Better for version control

**Structure:**
```
ai-network-analyzer/
├── backend/
│   ├── app/
│   ├── core/
│   └── requirements.txt
├── frontend/
│   └── app.py
├── Procfile
└── .gitignore
```

**Render Config:**
- Root Directory: (empty)
- Build: `pip install -r backend/requirements.txt`
- Start: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### ⚠️ Separate Backend Repo (Advanced)

Only if you want completely separate repos:

```bash
cd backend
git init
git add .
git commit -m "Backend only"
# Create separate GitHub repo
git push
```

**Render Config:**
- Root Directory: (empty) or `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 🐛 Common Issues & Fixes

### Issue: "Module not found"
```bash
# Fix: Update requirements.txt
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### Issue: "Port already in use"
**Fix:** Make sure start command uses `$PORT`:
```
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

### Issue: CORS errors
**Fix:** Update `backend/app/main.py`:
```python
origins = [
    "https://your-frontend.streamlit.app",
    "http://localhost:8501",
]
```

### Issue: Environment variables not working
**Fix:**
1. Check spelling in Render dashboard
2. Click "Manual Deploy" → "Clear build cache & deploy"
3. Check logs for errors

### Issue: Free tier sleeps
**Fix:**
- Accept 30s cold start
- Or upgrade to $7/month plan
- Or use UptimeRobot to ping every 5 min

---

## 📊 Deployment Status

Track your progress:

- [ ] Code on GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] Environment variables added
- [ ] Deployment successful
- [ ] API docs accessible
- [ ] Frontend connected
- [ ] Tests working
- [ ] AI recommendations working

---

## 🔗 Important URLs

After deployment, save these:

```
Backend API: https://your-service-name.onrender.com
API Docs: https://your-service-name.onrender.com/docs
GitHub Repo: https://github.com/YOUR_USERNAME/ai-network-analyzer
Render Dashboard: https://dashboard.render.com
```

---

## 💰 Cost

**Free Tier:**
- Backend: Render Free (sleeps after 15 min)
- Frontend: Streamlit Cloud Free
- Database: Supabase Free
- AI: Gemini Free tier

**Total: $0/month**

**Upgrade Options:**
- Render Starter: $7/month (always on)
- Streamlit Cloud: Free (sufficient)
- Supabase: Free (sufficient)

---

## 🎓 Next Steps

After backend is deployed:

1. **Deploy Frontend:**
   - Go to https://streamlit.io/cloud
   - Connect GitHub repo
   - Deploy `frontend/app.py`

2. **Test Everything:**
   - Sign up / Log in
   - Run network tests
   - Check AI recommendations

3. **Monitor:**
   - Check Render logs
   - Monitor Supabase usage
   - Track Gemini API calls

4. **Optimize:**
   - Add custom domain (optional)
   - Set up monitoring
   - Configure alerts

---

## 📞 Need Help?

**Check:**
1. Render logs (Dashboard → Logs)
2. Browser console (F12)
3. API docs (`/docs` endpoint)

**Resources:**
- Full guide: `RENDER_DEPLOYMENT_GUIDE.md`
- Render docs: https://render.com/docs
- Streamlit docs: https://docs.streamlit.io

**Common Commands:**
```bash
# Push updates
git add .
git commit -m "Update"
git push

# Test locally
cd backend
uvicorn app.main:app --reload

# Check Python version
python --version

# Install dependencies
pip install -r backend/requirements.txt
```

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✅ Render shows "Live" status
2. ✅ API docs load at `/docs`
3. ✅ Frontend can connect to backend
4. ✅ You can sign up / log in
5. ✅ Network tests run successfully
6. ✅ AI recommendations appear
7. ✅ No errors in logs

**Congratulations! 🎉**

Your AI Network Analyzer is now live!
