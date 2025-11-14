# 🔑 Setup Your Credentials

## Your Supabase Information

Based on your keys, your Supabase project reference is: `mvsmfyobnhqhkspmjeaw`

### Your Credentials:

**Project URL:**
```
https://mvsmfyobnhqhkspmjeaw.supabase.co
```

**Anon Key (use this for frontend):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12c21meW9ibmhxaGtzcG1qZWF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1MTkzMzgsImV4cCI6MjA3ODA5NTMzOH0.-5sZxtsvKRUpWPz0K7tUdKobD7-xiNW2z46-LKJLoRU
```

**Service Role Key (use this for backend if needed):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12c21meW9ibmhxaGtzcG1qZWF3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjUxOTMzOCwiZXhwIjoyMDc4MDk1MzM4fQ.fEL-6lVPJZGZy-oEySbwiWtnLSdE-ntxTEcMCoAN6uc
```

---

## 🔧 Fix Steps

### 1. Update Backend `.env`

Edit `backend/.env`:
```bash
SUPABASE_URL=https://mvsmfyobnhqhkspmjeaw.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12c21meW9ibmhxaGtzcG1qZWF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1MTkzMzgsImV4cCI6MjA3ODA5NTMzOH0.-5sZxtsvKRUpWPz0K7tUdKobD7-xiNW2z46-LKJLoRU
GEMINI_API_KEY=your-gemini-key-here
BACKEND_API_URL=http://localhost:8000
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 2. Update Frontend `.env`

Edit `frontend/.env`:
```bash
SUPABASE_URL=https://mvsmfyobnhqhkspmjeaw.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12c21meW9ibmhxaGtzcG1qZWF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1MTkzMzgsImV4cCI6MjA3ODA5NTMzOH0.-5sZxtsvKRUpWPz0K7tUdKobD7-xiNW2z46-LKJLoRU
BACKEND_API_URL=http://localhost:8000
```

### 3. Update Frontend Streamlit Secrets

Edit `frontend/.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "https://mvsmfyobnhqhkspmjeaw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12c21meW9ibmhxaGtzcG1qZWF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI1MTkzMzgsImV4cCI6MjA3ODA5NTMzOH0.-5sZxtsvKRUpWPz0K7tUdKobD7-xiNW2z46-LKJLoRU"
BACKEND_API_URL = "http://localhost:8000"
```

### 4. Upgrade Supabase Package

```bash
# In frontend folder
cd frontend
uv pip install --upgrade supabase

# Or reinstall all
uv pip install -r requirements.txt --upgrade
```

### 5. Restart Everything

```bash
# Stop both backend and frontend (Ctrl+C)

# Restart backend
cd backend
uvicorn app.main:app --reload

# Restart frontend (new terminal)
cd frontend
streamlit run app.py
```

---

## ✅ Test Again

1. Open http://localhost:8501
2. Click "Sign Up"
3. Enter email and password
4. Should work now! 🎉

---

## 🐛 If Still Not Working

Run the test again:
```bash
cd frontend
python test_supabase.py
```

Should now show:
```
✅ Successfully connected to Supabase!
```

---

**Your credentials are correct! Just need to upgrade the Supabase package.** 🚀
