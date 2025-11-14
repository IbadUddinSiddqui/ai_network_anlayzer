# Implementation Plan

- [x] 1. Set up project structure and configuration



  - Create root directory structure with backend/, frontend/, database/, .github/ folders
  - Initialize Python virtual environments for backend and frontend
  - Create requirements.txt files with all dependencies (FastAPI, Streamlit, Scapy, Ping3, Speedtest-CLI, OpenAI SDK, Supabase client)
  - Set up .env.example with required environment variables
  - Create .gitignore for Python projects
  - Initialize README.md with project overview


  - _Requirements: 8.1, 8.3_

- [ ] 2. Set up database schema and Supabase integration
  - Create database/schema.sql with all 5 tables (users, network_tests, ai_recommendations, optimization_history, feedback)
  - Add indexes for performance (user_id, test_timestamp, test_id)
  - Create backend/core/database/client.py for Supabase client initialization


  - Implement connection pooling and error handling


  - Create Pydantic models in backend/core/database/models.py for all database entities
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [ ] 3. Implement network testing module
- [x] 3.1 Create ping test functionality


  - Implement backend/core/network/ping_test.py using ping3 library
  - Send 10 ICMP packets to target hosts
  - Calculate min, max, avg, stddev latency
  - Return structured PingResult with error handling for unreachable hosts
  - _Requirements: 1.1, 1.7_



- [ ] 3.2 Create jitter calculation functionality
  - Implement backend/core/network/jitter_test.py
  - Perform consecutive ping measurements
  - Calculate absolute differences between consecutive latencies
  - Return avg_jitter_ms and max_jitter_ms

  - _Requirements: 1.2, 1.7_


- [ ] 3.3 Create packet loss test functionality
  - Implement backend/core/network/packet_loss_test.py using scapy
  - Send configurable number of packets (default 100)

  - Track successful responses

  - Calculate loss percentage
  - Handle permission errors (requires admin on some systems)
  - _Requirements: 1.3, 1.7_


- [-] 3.4 Create speed test functionality

  - Implement backend/core/network/speed_test.py using speedtest-cli
  - Measure download and upload speeds in Mbps
  - Capture server location and ping
  - Handle timeout errors gracefully
  - _Requirements: 1.4, 1.7_

- [ ] 3.5 Create DNS latency test functionality
  - Implement backend/core/network/dns_test.py using dnspython
  - Query multiple DNS servers (8.8.8.8, 1.1.1.1, etc.)
  - Test resolution for common domains


  - Calculate average resolution time per DNS server


  - _Requirements: 1.5, 1.7_

- [ ] 3.6 Create test orchestrator
  - Implement backend/core/network/test_runner.py
  - Orchestrate all network tests with async execution where possible


  - Aggregate results into unified NetworkTestResult JSON
  - Implement progress tracking and timeout handling
  - Add comprehensive logging for debugging
  - _Requirements: 1.6, 1.7, 1.8_

- [x]* 3.7 Write unit tests for network module


  - Create backend/tests/test_network_module.py
  - Mock network calls to test logic without actual requests
  - Test edge cases (100% packet loss, timeouts, invalid hosts)
  - Verify JSON output format matches Pydantic models
  - _Requirements: 10.1, 10.2, 10.4, 10.5_


- [ ] 4. Implement AI analysis module with multi-agent system
- [ ] 4.1 Create agent prompt templates
  - Implement backend/core/ai/prompts.py with structured prompts for each agent
  - Define input/output JSON schemas for agent communication
  - Include context about normal ranges and thresholds
  - Create synthesis prompt for main agent to merge insights
  - _Requirements: 2.8_


- [ ] 4.2 Implement Latency Diagnoser sub-agent
  - Create backend/core/ai/agents/latency_diagnoser.py
  - Analyze ping latency patterns from test results
  - Identify high latency issues (>100ms threshold)
  - Generate recommendations with confidence scores
  - Return structured JSON with insights


  - _Requirements: 2.2, 2.7, 2.8_

- [ ] 4.3 Implement Packet Loss Advisor sub-agent
  - Create backend/core/ai/agents/packet_loss_advisor.py
  - Analyze packet loss percentage
  - Identify network stability issues (>5% threshold)
  - Recommend hardware or ISP investigation


  - Return structured recommendations with confidence
  - _Requirements: 2.3, 2.7, 2.8_

- [ ] 4.4 Implement Bandwidth Optimizer sub-agent
  - Create backend/core/ai/agents/bandwidth_optimizer.py
  - Analyze upload/download speeds
  - Compare against expected ISP speeds
  - Suggest QoS configurations or plan upgrades
  - Return actionable recommendations
  - _Requirements: 2.4, 2.7, 2.8_

- [ ] 4.5 Implement DNS & Routing Advisor sub-agent
  - Create backend/core/ai/agents/dns_routing_advisor.py

  - Analyze DNS resolution times across servers
  - Compare performance differences
  - Recommend optimal DNS configuration (e.g., switch to 8.8.8.8)
  - Return recommendations with confidence scores
  - _Requirements: 2.5, 2.7, 2.8_

- [ ] 4.6 Implement main orchestrator agent
  - Create backend/core/ai/main_agent.py
  - Initialize OpenAI client with API key
  - Delegate analysis to all four sub-agents in parallel
  - Merge insights from sub-agents using synthesis prompt
  - Prioritize recommendations by severity and confidence
  - Handle AI API errors with fallback generic recommendations
  - _Requirements: 2.1, 2.6, 2.7, 2.9_

- [ ] 4.7 Create AI analyzer interface
  - Implement AIAnalyzer class in backend/core/ai/__init__.py
  - Provide clean interface for API layer to invoke AI analysis
  - Handle rate limiting for OpenAI API
  - Implement retry logic with exponential backoff
  - Add comprehensive error logging
  - _Requirements: 2.1, 2.9_

- [ ]* 4.8 Write unit tests for AI module
  - Create backend/tests/test_ai_module.py
  - Mock OpenAI API responses for predictable testing
  - Test agent orchestration logic
  - Verify confidence score calculations
  - Test fallback recommendation generation
  - _Requirements: 10.1, 10.4, 10.5_

- [ ] 5. Implement database repositories
- [x] 5.1 Create user repository


  - Implement backend/core/database/repositories/user_repository.py
  - Create methods: get_user_by_id, get_user_by_email, create_user
  - Handle Supabase Auth integration
  - Add error handling for constraint violations
  - _Requirements: 3.1, 3.7_


- [ ] 5.2 Create test repository
  - Implement backend/core/database/repositories/test_repository.py
  - Create methods: create_test, get_test_by_id, get_user_tests (with pagination)
  - Store JSONB test results efficiently
  - Add filtering by timestamp and status
  - _Requirements: 3.2, 3.6, 3.7_


- [ ] 5.3 Create recommendation repository
  - Implement backend/core/database/repositories/recommendation_repository.py
  - Create methods: create_recommendation, get_recommendations_by_test_id, bulk_create
  - Link recommendations to test_id
  - Support querying by agent_type and severity

  - _Requirements: 3.3, 3.7_

- [ ] 5.4 Create optimization repository
  - Implement backend/core/database/repositories/optimization_repository.py
  - Create methods: create_optimization, get_user_optimizations
  - Link to recommendation_id and user_id
  - Support historical tracking with timestamps

  - _Requirements: 3.4, 3.7_

- [ ] 5.5 Create feedback repository
  - Implement backend/core/database/repositories/feedback_repository.py
  - Create methods: create_feedback, get_user_feedback, get_feedback_stats
  - Support optional test_id and recommendation_id references
  - Validate rating range (1-5)
  - _Requirements: 3.5, 3.7_

- [ ]* 5.6 Write integration tests for repositories
  - Create backend/tests/test_repositories.py
  - Test CRUD operations for each repository
  - Verify referential integrity constraints
  - Test transaction rollbacks on errors
  - _Requirements: 10.3, 10.4, 10.5_

- [x] 6. Implement authentication middleware



  - Create backend/app/api/middleware/auth.py
  - Validate Supabase JWT tokens on protected endpoints
  - Extract user_id from token payload
  - Inject user context into request state
  - Handle invalid/expired tokens with 401 responses
  - Add logging for authentication failures
  - _Requirements: 4.2, 4.3, 4.4, 4.5, 6.5_

- [ ] 7. Implement FastAPI endpoints
- [x] 7.1 Create /run-test endpoint


  - Implement POST /api/v1/run-test in backend/app/api/routes/tests.py
  - Accept TestConfig with target_hosts and dns_servers
  - Validate input using Pydantic models
  - Trigger async network test execution
  - Store initial test record with "running" status
  - Return test_id immediately
  - _Requirements: 6.1, 6.6, 6.7_

- [ ] 7.2 Create /get-results endpoint
  - Implement GET /api/v1/get-results/{test_id} in backend/app/api/routes/tests.py
  - Verify user owns the test (authorization check)
  - Retrieve test results and AI recommendations from database
  - Return combined response with status
  - Handle test not found errors
  - _Requirements: 6.2, 6.4, 6.7_

- [ ] 7.3 Create /apply-optimization endpoint
  - Implement POST /api/v1/apply-optimization in backend/app/api/routes/optimizations.py
  - Accept recommendation_id, action_taken, and optional notes
  - Verify user owns the recommendation
  - Store optimization action in database
  - Return optimization_id and success status
  - _Requirements: 6.3, 6.7_

- [ ] 7.4 Create /feedback endpoint
  - Implement POST /api/v1/feedback in backend/app/api/routes/feedback.py
  - Accept test_id, recommendation_id (optional), rating, and comment
  - Validate rating is between 1-5
  - Store feedback in database
  - Return feedback_id and success status
  - _Requirements: 6.4, 6.6, 6.7_

- [ ] 7.5 Set up FastAPI application with middleware
  - Create backend/app/main.py as application entry point
  - Configure CORS for frontend domains
  - Register authentication middleware
  - Register all route modules
  - Add global exception handlers
  - Create /health endpoint for monitoring
  - Configure logging with structured format
  - _Requirements: 6.5, 6.7, 6.8_

- [ ] 7.6 Create configuration management
  - Implement backend/app/config.py
  - Load environment variables (SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, etc.)
  - Validate required configuration on startup
  - Provide configuration objects for dependency injection
  - _Requirements: 7.3, 7.4, 7.6_

- [ ]* 7.7 Write API endpoint tests
  - Create backend/tests/test_api_endpoints.py
  - Test each endpoint with valid and invalid inputs
  - Verify authentication middleware blocks unauthenticated requests
  - Test error responses and status codes
  - Mock database and external service calls
  - _Requirements: 10.1, 10.4, 10.5_

- [ ] 8. Implement Streamlit frontend components
- [ ] 8.1 Create API client utility
  - Implement frontend/utils/api_client.py
  - Create methods for all backend endpoints (run_test, get_results, apply_optimization, feedback)
  - Handle authentication token injection in headers
  - Implement error handling and retry logic
  - Return parsed JSON responses
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 8.2 Create session management utility
  - Implement frontend/utils/session.py
  - Store authentication tokens in Streamlit session state
  - Provide login/logout functions
  - Handle token expiration and refresh
  - _Requirements: 4.2, 4.6_

- [ ] 8.3 Create authentication components
  - Implement frontend/components/auth.py
  - Build login form with email/password inputs
  - Build signup form with validation
  - Integrate with Supabase Auth
  - Store session token on successful authentication
  - Display error messages for failed authentication
  - _Requirements: 4.1, 4.2, 4.5_

- [ ] 8.4 Create test runner component
  - Implement frontend/components/test_runner.py
  - Display "Run Network Test" button prominently
  - Show configuration options (target hosts, DNS servers)
  - Display progress indicator during test execution
  - Poll /get-results endpoint until test completes
  - Handle test failures with user-friendly messages
  - _Requirements: 5.1, 5.2, 1.8_

- [ ] 8.5 Create results visualization component
  - Implement frontend/components/charts.py
  - Create line chart for ping latency over time using Plotly/Altair
  - Create bar chart for jitter measurements
  - Create gauge charts for upload/download speeds
  - Create percentage indicator for packet loss with color coding
  - Create comparison chart for DNS server performance
  - _Requirements: 5.3, 5.4, 5.5_

- [ ] 8.6 Create results display component
  - Implement frontend/components/results_display.py
  - Organize charts in tabs (Latency, Jitter, Speed, Packet Loss, DNS)
  - Display raw metrics alongside visualizations
  - Show test timestamp and status
  - _Requirements: 5.3, 5.4, 5.5_

- [ ] 8.7 Create AI recommendations component
  - Implement frontend/components/recommendations.py
  - Display recommendations in card-based layout
  - Show confidence score with progress bar or badge
  - Add severity indicator with color coding (red=critical, yellow=warning, green=info)
  - Include "Apply Optimization" button for each recommendation
  - Add expandable details section
  - Handle apply optimization action with API call
  - _Requirements: 5.6, 5.7, 5.8_

- [ ] 8.8 Create main dashboard application
  - Implement frontend/app.py as Streamlit entry point
  - Check authentication status on load
  - Show login/signup page if not authenticated
  - Display main dashboard with header (user info, logout button)
  - Integrate test runner component
  - Integrate results display component
  - Integrate recommendations component
  - Add history view with past tests table
  - Implement responsive design with Streamlit columns
  - _Requirements: 5.1, 5.9, 5.10_

- [ ] 9. Implement end-to-end workflow integration
  - Wire test runner to trigger /run-test endpoint
  - Connect test completion to AI analysis invocation
  - Ensure AI recommendations are stored in database after analysis
  - Link apply optimization button to /apply-optimization endpoint
  - Connect feedback submission to /feedback endpoint
  - Add comprehensive error handling across the entire flow
  - Implement logging at each integration point
  - _Requirements: 1.8, 2.1, 3.2, 3.3, 3.4, 3.5, 6.8_

- [ ]* 10. Write end-to-end integration tests
  - Create backend/tests/test_integration.py
  - Test complete workflow: create user → run test → get results → apply optimization → submit feedback
  - Verify database records created at each step
  - Test error scenarios (network failure, AI failure, database failure)
  - Validate data consistency across tables
  - _Requirements: 10.3, 10.4, 10.5_

- [ ] 11. Set up deployment configuration
- [ ] 11.1 Create Dockerfile for backend
  - Create backend/Dockerfile
  - Use Python 3.11 slim base image
  - Install system dependencies for Scapy and network tools
  - Copy application code and install Python dependencies
  - Expose port 8000
  - Set CMD to run Uvicorn server
  - _Requirements: 7.1, 7.2_

- [ ] 11.2 Create Render configuration
  - Create render.yaml for infrastructure as code
  - Configure web service for FastAPI backend
  - Set environment variables from Render dashboard
  - Configure health check endpoint
  - Set auto-deploy on git push
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 11.3 Create GitHub Actions CI/CD workflow
  - Create .github/workflows/ci-cd.yml
  - Add job for linting (flake8, black)
  - Add job for running unit tests
  - Add job for running integration tests
  - Add job for building Docker image
  - Add job for deploying to Render (on main branch only)
  - Configure secrets for API keys
  - _Requirements: 7.1, 7.2, 7.5_

- [ ] 11.4 Create environment configuration files
  - Create .env.example with all required variables
  - Document each environment variable in README
  - Add instructions for obtaining Supabase and OpenAI credentials
  - Create docker-compose.yml for local development
  - _Requirements: 7.3, 7.6, 8.3_

- [ ] 12. Create comprehensive documentation
  - Update README.md with project overview, features, and architecture diagram
  - Add setup instructions for local development
  - Document API endpoints with request/response examples
  - Add deployment instructions for Render
  - Create backend/README.md with module-specific documentation
  - Create frontend/README.md with component documentation
  - Add code comments explaining complex logic
  - Document environment variables and configuration options
  - _Requirements: 8.2, 8.3, 8.5_

- [ ] 13. Implement logging and monitoring
  - Configure structured logging in backend with user_id, test_id, request_id context
  - Set up log levels (DEBUG for development, INFO for production)
  - Add error tracking integration (optional: Sentry)
  - Create /health endpoint with database connectivity check
  - Add request/response logging middleware
  - Implement performance metrics tracking (response times)
  - _Requirements: 6.8, 8.4_

- [ ] 14. Implement security hardening
  - Add rate limiting middleware (100 requests/minute per user)
  - Configure CORS with whitelist of allowed origins
  - Implement input sanitization for all user inputs
  - Add SQL injection prevention (use parameterized queries)
  - Validate all environment variables on startup
  - Add security headers (HSTS, X-Content-Type-Options, etc.)
  - Review and remove any hardcoded credentials
  - _Requirements: 4.3, 4.4, 6.5, 7.6_

- [ ] 15. Optimize for scalability and performance
  - Implement database connection pooling in Supabase client
  - Add async/await for all I/O operations
  - Create database indexes on frequently queried columns
  - Implement pagination for get_user_tests endpoint
  - Add caching headers for static responses
  - Optimize JSONB queries in PostgreSQL
  - Test concurrent request handling
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_
