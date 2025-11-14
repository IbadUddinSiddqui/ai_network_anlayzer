# 🤖 Google Gemini Setup Guide

## Get Your Gemini API Key

### Step 1: Go to Google AI Studio

Visit: https://makersuite.google.com/app/apikey

### Step 2: Create API Key

1. Click **"Get API Key"** or **"Create API Key"**
2. Select your Google Cloud project (or create a new one)
3. Click **"Create API key in new project"** if you don't have one
4. Copy your API key (starts with: `AIza...`)

### Step 3: Add to Environment

Edit your `.env` file:

```bash
# Google Gemini Configuration
GEMINI_API_KEY=AIzaSyYourApiKeyHere

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# Backend URL
BACKEND_API_URL=http://localhost:8000
```

### Step 4: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install `google-generativeai` package.

### Step 5: Test It!

Start your backend:

```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Configuration validated successfully
INFO:     AIAnalyzer initialized successfully
```

---

## ✅ What Changed from OpenAI

### API Changes
- ❌ Removed: `openai` package
- ✅ Added: `google-generativeai` package

### Model Changes
- ❌ Old: `gpt-4o-mini`
- ✅ New: `gemini-pro`

### Environment Variables
- ❌ Old: `OPENAI_API_KEY`
- ✅ New: `GEMINI_API_KEY`

### Code Changes
All AI agents now use Google Gemini:
- ✅ `LatencyDiagnoser` - Uses Gemini
- ✅ `PacketLossAdvisor` - Uses Gemini
- ✅ `BandwidthOptimizer` - Uses Gemini
- ✅ `DNSRoutingAdvisor` - Uses Gemini
- ✅ `MainAgent` - Uses Gemini

---

## 🎯 Gemini Features

### Advantages
- ✅ **Free Tier**: 60 requests per minute
- ✅ **No Credit Card**: Free to start
- ✅ **Good Performance**: Fast responses
- ✅ **JSON Support**: Structured outputs

### Pricing (if you exceed free tier)
- Free: 60 requests/minute
- Paid: Very affordable rates

---

## 🧪 Test Your Setup

### 1. Check API Key
```bash
# In Python
import google.generativeai as genai
genai.configure(api_key='your-key-here')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Hello!')
print(response.text)
```

### 2. Test Backend
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "database_connected": true
}
```

### 3. Run Full Test
1. Start backend
2. Start frontend
3. Login
4. Run network test
5. Check AI recommendations appear!

---

## 🐛 Troubleshooting

### Error: "Gemini API key must be provided"
**Solution**: Check your `.env` file has `GEMINI_API_KEY` set

### Error: "API key not valid"
**Solution**: 
1. Go to https://makersuite.google.com/app/apikey
2. Verify your API key is active
3. Copy the correct key

### Error: "Quota exceeded"
**Solution**: 
- Free tier: 60 requests/minute
- Wait a minute and try again
- Or upgrade to paid tier

### Error: "Module not found: google.generativeai"
**Solution**:
```bash
pip install google-generativeai
```

---

## 📊 Comparison: OpenAI vs Gemini

| Feature | OpenAI | Gemini |
|---------|--------|--------|
| Free Tier | Limited trial | 60 req/min free |
| Credit Card | Required | Not required |
| Model | gpt-4o-mini | gemini-pro |
| Speed | Fast | Fast |
| JSON Output | Native | Supported |
| Cost | $$ | $ (cheaper) |

---

## 🚀 You're Ready!

Your AI Network Analyzer now uses **Google Gemini**!

All AI recommendations will be powered by Gemini Pro model.

**Next Steps:**
1. Get your Gemini API key
2. Add to `.env` file
3. Install dependencies
4. Start testing!

---

## 📞 Need Help?

- **Gemini Docs**: https://ai.google.dev/docs
- **API Keys**: https://makersuite.google.com/app/apikey
- **Pricing**: https://ai.google.dev/pricing

---

**Enjoy your AI-powered network analysis with Gemini! 🎉**
