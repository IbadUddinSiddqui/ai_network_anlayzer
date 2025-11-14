# 🚀 Quick Start with Google Gemini

## 3-Minute Setup

### 1️⃣ Get Gemini API Key (30 seconds)
```
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy key (starts with AIza...)
```

### 2️⃣ Configure Environment (30 seconds)
```bash
# Edit .env file
GEMINI_API_KEY=AIzaSyYourKeyHere
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
BACKEND_API_URL=http://localhost:8000
```

### 3️⃣ Install & Run (2 minutes)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### 4️⃣ Test (30 seconds)
```
1. Open: http://localhost:8501
2. Create account
3. Run network test
4. See AI recommendations! ✅
```

---

## ✅ That's It!

**Total Time: ~3 minutes**

Your AI Network Analyzer is running with FREE Gemini AI!

---

## 🎯 Key Points

- ✅ **FREE**: 60 requests/minute
- ✅ **No Credit Card**: Start immediately
- ✅ **Same Quality**: Powerful AI analysis
- ✅ **Easy Setup**: Just one API key

---

## 🐛 Quick Fixes

**Backend won't start?**
```bash
# Check .env has GEMINI_API_KEY
cat .env | grep GEMINI
```

**Module not found?**
```bash
pip install google-generativeai
```

**API key invalid?**
```
Get new key: https://makersuite.google.com/app/apikey
```

---

## 📚 Full Docs

- Setup: `GEMINI_SETUP.md`
- Migration: `GEMINI_MIGRATION_COMPLETE.md`
- Testing: `TESTING_GUIDE.md`
- General: `README.md`

---

**Happy Testing! 🎉**
