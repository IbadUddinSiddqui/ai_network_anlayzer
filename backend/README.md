# Backend - AI Network Analyzer

FastAPI-based backend for network testing, AI analysis, and data management.

## Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # API endpoint handlers
│   │   └── middleware/      # Authentication, logging
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   └── dependencies.py      # Dependency injection
├── core/
│   ├── network/             # Network testing module
│   │   ├── ping_test.py
│   │   ├── jitter_test.py
│   │   ├── packet_loss_test.py
│   │   ├── speed_test.py
│   │   ├── dns_test.py
│   │   └── test_runner.py
│   ├── ai/                  # AI analysis module
│   │   ├── agents/          # Specialized sub-agents
│   │   ├── main_agent.py    # Main orchestrator
│   │   └── prompts.py       # Agent prompts
│   └── database/            # Database layer
│       ├── client.py        # Supabase client
│       ├── models.py        # Pydantic models
│       └── repositories/    # CRUD operations
└── tests/                   # Test suite
```

## Modules

### Network Testing Module
Executes comprehensive network performance tests:
- **Ping Test**: Measures latency using ping3
- **Jitter Test**: Calculates latency variation
- **Packet Loss Test**: Measures packet loss using scapy
- **Speed Test**: Measures bandwidth using speedtest-cli
- **DNS Test**: Measures DNS resolution time using dnspython

### AI Analysis Module
Multi-agent system for intelligent network diagnostics:
- **Main Agent**: Orchestrates sub-agents and merges insights
- **Latency Diagnoser**: Analyzes ping latency patterns
- **Packet Loss Advisor**: Diagnoses packet loss issues
- **Bandwidth Optimizer**: Analyzes speed metrics
- **DNS & Routing Advisor**: Optimizes DNS configuration

### Database Layer
Repository pattern for data persistence:
- **User Repository**: User management
- **Test Repository**: Network test results
- **Recommendation Repository**: AI recommendations
- **Optimization Repository**: Applied optimizations
- **Feedback Repository**: User feedback

## API Endpoints

### Authentication
All endpoints require JWT authentication via Supabase Auth.

### Endpoints

**POST /api/v1/run-test**
- Initiates network test
- Returns test_id for polling

**GET /api/v1/get-results/{test_id}**
- Retrieves test results and AI recommendations
- Polls until test completes

**POST /api/v1/apply-optimization**
- Records optimization action
- Links to recommendation_id

**POST /api/v1/feedback**
- Stores user feedback
- Optional test_id and recommendation_id

**GET /health**
- Health check endpoint
- Verifies database connectivity

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov=core --cov-report=html

# Run specific test file
pytest tests/test_network_module.py -v
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
open http://localhost:8000/docs
```

## Configuration

Environment variables are loaded from `.env` file:
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anon key
- `OPENAI_API_KEY`: OpenAI API key
- `LOG_LEVEL`: Logging level (DEBUG/INFO/ERROR)

## Error Handling

Custom exception hierarchy:
- `NetworkAnalyzerException`: Base exception
- `NetworkTestException`: Network test failures
- `AIAnalysisException`: AI analysis failures
- `DatabaseException`: Database operation failures

All errors are logged with context (user_id, test_id, request_id).

## Logging

Structured logging with JSON format:
```python
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "message": "Network test completed",
  "user_id": "uuid",
  "test_id": "uuid",
  "duration_ms": 5000
}
```
