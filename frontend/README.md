# Frontend - AI Network Analyzer

Streamlit-based interactive dashboard for network testing and AI recommendations.

## Structure

```
frontend/
├── components/
│   ├── auth.py              # Login/signup components
│   ├── test_runner.py       # Test initiation UI
│   ├── results_display.py   # Results visualization
│   ├── recommendations.py   # AI insights display
│   └── charts.py            # Chart components
├── utils/
│   ├── api_client.py        # Backend API client
│   └── session.py           # Session management
└── app.py                   # Main Streamlit application
```

## Components

### Authentication Component
- Login form with email/password
- Signup form with validation
- Supabase Auth integration
- Session token management

### Test Runner Component
- "Run Network Test" button
- Configuration options (target hosts, DNS servers)
- Progress indicator during test execution
- Real-time status updates

### Results Display Component
- Tabbed interface for different metrics
- **Latency Tab**: Line chart of ping over time
- **Jitter Tab**: Bar chart of jitter measurements
- **Speed Tab**: Gauge charts for upload/download
- **Packet Loss Tab**: Percentage indicator with color coding
- **DNS Tab**: Comparison chart of DNS servers

### Recommendations Component
- Card-based layout for AI insights
- Confidence score visualization
- Severity indicators (critical/warning/info)
- "Apply Optimization" buttons
- Expandable details sections

### Charts Component
- Plotly and Altair visualizations
- Responsive design
- Interactive tooltips
- Color-coded metrics

## Features

### Dashboard Pages
1. **Login/Signup**: Authentication flow
2. **Main Dashboard**: Test runner and results
3. **History View**: Past tests with filtering
4. **Settings**: User preferences

### User Experience
- Real-time updates during test execution
- Responsive design for various screen sizes
- User-friendly error messages
- Loading indicators and progress bars

## Running the Frontend

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py

# Access dashboard
open http://localhost:8501
```

## Configuration

Create `.streamlit/secrets.toml`:
```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-supabase-anon-key"

[api]
backend_url = "http://localhost:8000"
```

## Session Management

User sessions are stored in Streamlit session state:
- `authenticated`: Boolean flag
- `user_id`: User UUID
- `access_token`: JWT token
- `user_email`: User email

## API Integration

The frontend communicates with the backend via REST API:
```python
# Example API call
api_client = APIClient(backend_url, access_token)
test_id = api_client.run_test(target_hosts, dns_servers)
results = api_client.get_results(test_id)
```

## Styling

Custom CSS for enhanced UI:
- Card-based layouts
- Color-coded severity indicators
- Responsive grid system
- Custom buttons and forms

## Development Tips

1. Use `st.cache_data` for expensive operations
2. Store state in `st.session_state`
3. Use `st.rerun()` for dynamic updates
4. Handle errors gracefully with try-except
5. Show loading spinners for async operations
