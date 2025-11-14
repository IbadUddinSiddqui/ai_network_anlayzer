# AI Network Analyzer & Optimization Agent

A full-stack AI-powered SaaS platform that monitors, analyzes, and optimizes network performance using intelligent multi-agent analysis.

## 🚀 Features

- **Comprehensive Network Testing**: Measure ping latency, jitter, packet loss, upload/download speeds, and DNS resolution times
- **AI-Powered Analysis**: Multi-agent system with specialized sub-agents for latency, packet loss, bandwidth, and DNS diagnostics
- **Interactive Dashboard**: Streamlit-based UI with real-time graphs and visualizations
- **Actionable Recommendations**: AI-generated insights with confidence scores and severity indicators
- **Historical Tracking**: Store and analyze network performance over time
- **Secure Authentication**: Supabase Auth integration with JWT tokens
- **Production-Ready**: Modular architecture, comprehensive logging, and deployment automation

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
┌──────▼──────────┐
│    Streamlit    │
│    Dashboard    │
└──────┬──────────┘
       │
┌──────▼──────────┐
│  FastAPI Backend│
└─┬─────┬─────┬───┘
  │     │     │
  ▼     ▼     ▼
┌───┐ ┌───┐ ┌────────┐
│Net│ │AI │ │Supabase│
│Test│ │Agt│ │  DB    │
└───┘ └───┘ └────────┘
```

## 📋 Tech Stack

- **Frontend**: Streamlit, Plotly, Altair
- **Backend**: FastAPI, Pydantic
- **Network Testing**: Scapy, Ping3, Speedtest-CLI, dnspython
- **AI**: Google Gemini API
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Deployment**: Render, Docker
- **CI/CD**: GitHub Actions

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.11+
- Supabase account
- Google Gemini API key (FREE!)
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-network-analyzer
```

2. **Set up backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up frontend**
```bash
cd frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Set up database**
- Create a Supabase project at https://supabase.com
- Run the SQL schema from `database/schema.sql` in Supabase SQL Editor
- Copy your Supabase URL and keys to `.env`

6. **Run the backend**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Run the frontend**
```bash
cd frontend
streamlit run app.py
```

8. **Access the application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🎯 Quick Start Guide

### First Time Setup

1. **Create Supabase Project**
   - Go to https://supabase.com and create a new project
   - Copy your project URL and anon key
   - Run the schema from `database/schema.sql` in SQL Editor

2. **Get Google Gemini API Key** (FREE!)
   - Visit https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key (starts with AIza...)

3. **Configure Environment**
   ```bash
   # Create .env file
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GEMINI_API_KEY=your_gemini_key
   BACKEND_API_URL=http://localhost:8000
   ```

4. **Start Services**
   ```bash
   # Terminal 1 - Backend
   cd backend && uvicorn app.main:app --reload
   
   # Terminal 2 - Frontend
   cd frontend && streamlit run app.py
   ```

5. **Create Account**
   - Open http://localhost:8501
   - Click "Sign Up" tab
   - Create your account
   - Login and start testing!

## 📁 Project Structure

```
ai-network-analyzer/
├── backend/
│   ├── app/                    # FastAPI application
│   │   ├── api/               # API routes and middleware
│   │   ├── main.py            # Application entry point
│   │   └── config.py          # Configuration management
│   ├── core/                  # Core business logic
│   │   ├── network/           # Network testing module
│   │   ├── ai/                # AI analysis module
│   │   └── database/          # Database layer
│   └── tests/                 # Test suite
├── frontend/
│   ├── components/            # UI components
│   ├── utils/                 # Utilities
│   └── app.py                 # Main Streamlit app
├── database/
│   ├── schema.sql             # Database schema
│   └── migrations/            # Database migrations
└── .github/
    └── workflows/             # CI/CD pipelines
```

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon/public key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key (FREE!) | Yes |
| `ENVIRONMENT` | Environment (development/production) | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/ERROR) | No |
| `BACKEND_API_URL` | Backend API URL for frontend | Yes |

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest tests/ -v --cov=app --cov=core
```

## 🚢 Deployment

### Deploy to Render

1. **Create a Render account** at https://render.com

2. **Create a new Web Service**
- Connect your GitHub repository
- Select `backend` as the root directory
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set environment variables** in Render dashboard

4. **Deploy frontend** to Streamlit Cloud or Render

### Docker Deployment

```bash
docker-compose up -d
```

## 📊 API Endpoints

### POST /api/v1/run-test
Initiate a network test
```json
{
  "target_hosts": ["8.8.8.8", "1.1.1.1"],
  "dns_servers": ["8.8.8.8", "1.1.1.1"]
}
```

### GET /api/v1/get-results/{test_id}
Retrieve test results and AI recommendations

### POST /api/v1/apply-optimization
Record an optimization action
```json
{
  "recommendation_id": "uuid",
  "action_taken": "Changed DNS to 8.8.8.8",
  "notes": "Optional notes"
}
```

### POST /api/v1/feedback
Submit user feedback
```json
{
  "test_id": "uuid",
  "rating": 5,
  "comment": "Very helpful recommendations"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for AI capabilities
- Supabase for database and authentication
- Streamlit for the dashboard framework
- FastAPI for the backend framework

## 📧 Support

For issues and questions, please open a GitHub issue or contact the maintainers.

---

Built with ❤️ for network administrators and DevOps engineers
