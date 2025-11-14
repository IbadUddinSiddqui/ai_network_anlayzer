# Design Document: Fix Test Result Inconsistencies

## Overview

This design addresses the inconsistent test results issue by implementing comprehensive error handling, validation, retry logic, and user feedback mechanisms. The solution focuses on making failures visible, recoverable, and informative rather than silent.

## Architecture

### High-Level Flow

```
User Initiates Test
    ↓
API Creates Test Record (status: "running")
    ↓
Background Task Executes Tests
    ↓
[For Each Test Type]
    ↓
    Try Execute Test
        ↓
        [On Failure] → Retry (max 2 times)
            ↓
            [Still Fails] → Log Error + Store Partial Results
        ↓
        [On Success] → Validate Results
            ↓
            [Invalid] → Log Warning + Mark as Partial
            ↓
            [Valid] → Store Results
    ↓
Run AI Analysis (with retry)
    ↓
    [On Failure] → Use Fallback Recommendations
    ↓
Store Recommendations
    ↓
Update Test Status ("completed" or "partial" or "failed")
    ↓
Frontend Polls for Results
    ↓
Display Results with Status Indicators
```

## Components and Interfaces

### 1. Enhanced Error Handling Module

**Location:** `backend/core/utils/error_handling.py`

```python
class TestExecutionError(Exception):
    """Base exception for test execution errors"""
    pass

class ValidationError(Exception):
    """Exception for validation failures"""
    pass

def log_and_capture_exception(logger, context: str, exception: Exception) -> Dict:
    """
    Log exception with full context and return error dict
    
    Returns:
        {
            "error": str(exception),
            "error_type": type(exception).__name__,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
    """
    pass

async def retry_async(func, max_retries: int = 2, delay: float = 2.0, *args, **kwargs):
    """
    Retry async function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts
        delay: Initial delay between retries
    
    Returns:
        Function result or raises last exception
    """
    pass
```

### 2. Result Validation Module

**Location:** `backend/core/validation/test_results.py`

```python
class TestResultValidator:
    """Validates test results for completeness and correctness"""
    
    def validate_ping_results(self, results: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate ping results
        
        Returns:
            (is_valid, list_of_errors)
        """
        pass
    
    def validate_speed_results(self, results: Dict) -> Tuple[bool, List[str]]:
        """Validate speed test results"""
        pass
    
    def validate_packet_loss_results(self, results: Dict) -> Tuple[bool, List[str]]:
        """Validate packet loss results"""
        pass
    
    def validate_jitter_results(self, results: Dict) -> Tuple[bool, List[str]]:
        """Validate jitter results"""
        pass
    
    def validate_dns_results(self, results: List[Dict]) -> Tuple[bool, List[str]]:
        """Validate DNS results"""
        pass
    
    def validate_all_results(self, test_results: Dict, config: TestConfig) -> Dict:
        """
        Validate all test results based on what was requested
        
        Returns:
            {
                "is_complete": bool,
                "validation_errors": List[str],
                "missing_tests": List[str],
                "partial_tests": List[str]
            }
        """
        pass
```

### 3. Enhanced Test Runner

**Location:** `backend/core/network/test_runner.py` (modifications)

**Changes:**
- Add retry logic to each test method
- Add result validation after each test
- Store partial results even if some tests fail
- Return detailed status information

```python
class NetworkTestRunner:
    def __init__(self):
        self.test_id = None
        self.progress_callback = None
        self.validator = TestResultValidator()
        self.max_retries = 2
        self.retry_delay = 2.0
    
    async def _run_test_with_retry(
        self,
        test_func,
        test_name: str,
        *args,
        **kwargs
    ) -> Tuple[Dict, Optional[str]]:
        """
        Run a test with retry logic
        
        Returns:
            (result_dict, error_message)
        """
        pass
    
    async def run_all_tests(self, ...) -> Dict:
        """
        Modified to:
        - Use retry logic for each test
        - Validate results after each test
        - Continue even if some tests fail
        - Return detailed status
        
        Returns:
            {
                "test_id": str,
                "timestamp": str,
                "status": "completed" | "partial" | "failed",
                "ping_results": [...],
                "jitter_results": {...},
                "packet_loss_results": {...},
                "speed_results": {...},
                "dns_results": [...],
                "test_status": {
                    "ping": "success" | "failed" | "skipped",
                    "jitter": "success" | "failed" | "skipped",
                    "packet_loss": "success" | "failed" | "skipped",
                    "speed": "success" | "failed" | "skipped",
                    "dns": "success" | "failed" | "skipped"
                },
                "errors": {
                    "ping": Optional[str],
                    "jitter": Optional[str],
                    ...
                }
            }
        """
        pass
```

### 4. Enhanced API Routes

**Location:** `backend/app/api/routes/tests.py` (modifications)

**Changes to `get_results` function:**

```python
@router.get("/get-results/{test_id}", response_model=TestResultsResponse)
async def get_results(...):
    """
    Modified to:
    - Log exceptions instead of silently catching
    - Return validation errors to frontend
    - Include test status for each test type
    """
    
    # Replace:
    # try:
    #     jitter = JitterResult(**test["jitter_results"])
    # except:
    #     pass
    
    # With:
    try:
        jitter = JitterResult(**test["jitter_results"])
    except Exception as e:
        logger.error(
            f"Failed to parse jitter results for test {test_id}: {e}",
            exc_info=True
        )
        jitter = None
```

**Changes to `execute_network_test` function:**

```python
async def execute_network_test(...):
    """
    Modified to:
    - Use retry logic for AI analysis
    - Validate results before storing
    - Store partial results on failure
    - Always generate recommendations (fallback if needed)
    - Update test with detailed status
    """
    
    try:
        # Run tests with retry
        test_results = await runner.run_all_tests(...)
        
        # Validate results
        validation = validator.validate_all_results(test_results, config)
        
        # Determine overall status
        if validation["is_complete"]:
            status = "completed"
        elif validation["missing_tests"]:
            status = "partial"
        else:
            status = "failed"
        
        # Store results (even if partial)
        test_data = {
            "ping_results": test_results["ping_results"],
            "jitter_results": test_results["jitter_results"],
            "packet_loss_results": test_results["packet_loss_results"],
            "speed_results": test_results["speed_results"],
            "dns_results": test_results["dns_results"],
            "status": status,
            "test_status": test_results.get("test_status", {}),
            "errors": test_results.get("errors", {})
        }
        
        # Update database
        await update_test_with_retry(test_id, test_data)
        
        # Run AI analysis with retry
        try:
            analysis = await retry_async(
                analyzer.analyze,
                max_retries=2,
                delay=1.0,
                test_results
            )
        except Exception as e:
            logger.error(f"AI analysis failed after retries: {e}")
            # Use fallback
            analysis = analyzer._generate_fallback_analysis(test_results)
        
        # Store recommendations (always, even if fallback)
        await store_recommendations_with_validation(test_id, analysis)
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}", exc_info=True)
        # Store error in database
        await update_test_error(test_id, str(e))
```

### 5. Enhanced Database Models

**Location:** `backend/core/database/models.py` (additions)

```python
class TestStatus(str, Enum):
    """Network test status enumeration."""
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"  # NEW: Some tests succeeded, some failed
    FAILED = "failed"

class IndividualTestStatus(str, Enum):
    """Status for individual test types"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

class TestStatusDetail(BaseModel):
    """Detailed status for each test type"""
    ping: IndividualTestStatus = IndividualTestStatus.SKIPPED
    jitter: IndividualTestStatus = IndividualTestStatus.SKIPPED
    packet_loss: IndividualTestStatus = IndividualTestStatus.SKIPPED
    speed: IndividualTestStatus = IndividualTestStatus.SKIPPED
    dns: IndividualTestStatus = IndividualTestStatus.SKIPPED

class TestErrors(BaseModel):
    """Error messages for failed tests"""
    ping: Optional[str] = None
    jitter: Optional[str] = None
    packet_loss: Optional[str] = None
    speed: Optional[str] = None
    dns: Optional[str] = None

class NetworkTestResult(BaseModel):
    """Complete network test results."""
    test_id: UUID
    timestamp: datetime
    ping_results: List[PingResult] = Field(default_factory=list)
    jitter_results: Optional[JitterResult] = None
    packet_loss_results: Optional[PacketLossResult] = None
    speed_results: Optional[SpeedResult] = None
    dns_results: List[DNSResult] = Field(default_factory=list)
    status: TestStatus
    test_status: Optional[TestStatusDetail] = None  # NEW
    errors: Optional[TestErrors] = None  # NEW
```

### 6. Frontend Error Display

**Location:** `frontend/app.py` (modifications)

**Add status indicators:**

```python
# After displaying results, show test status
if 'test_status' in test_data:
    st.markdown("### Test Status")
    
    status_icons = {
        'success': '✅',
        'failed': '❌',
        'skipped': '⏭️'
    }
    
    cols = st.columns(5)
    test_types = ['ping', 'jitter', 'packet_loss', 'speed', 'dns']
    test_names = ['Ping', 'Jitter', 'Packet Loss', 'Speed', 'DNS']
    
    for col, test_type, test_name in zip(cols, test_types, test_names):
        status = test_data['test_status'].get(test_type, 'skipped')
        icon = status_icons.get(status, '❓')
        
        with col:
            st.markdown(f"{icon} **{test_name}**")
            st.caption(status.title())

# Show errors if any
if 'errors' in test_data and any(test_data['errors'].values()):
    with st.expander("⚠️ View Test Errors"):
        for test_type, error in test_data['errors'].items():
            if error:
                st.error(f"**{test_type.title()}:** {error}")
```

## Data Models

### Database Schema Changes

**Add columns to `network_tests` table:**

```sql
ALTER TABLE network_tests 
ADD COLUMN test_status JSONB DEFAULT '{}',
ADD COLUMN errors JSONB DEFAULT '{}';
```

### Test Result Structure

```json
{
  "test_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z",
  "status": "partial",
  "ping_results": [...],
  "jitter_results": {...},
  "packet_loss_results": {},
  "speed_results": {...},
  "dns_results": [...],
  "test_status": {
    "ping": "success",
    "jitter": "success",
    "packet_loss": "failed",
    "speed": "success",
    "dns": "success"
  },
  "errors": {
    "ping": null,
    "jitter": null,
    "packet_loss": "Permission denied - requires administrator privileges",
    "speed": null,
    "dns": null
  }
}
```

## Error Handling

### Error Categories

1. **Network Errors** - Connection timeouts, DNS failures
   - Retry: Yes (2 times)
   - Fallback: Empty results with error message

2. **Permission Errors** - Requires admin/root privileges
   - Retry: No
   - Fallback: Skip test, log warning

3. **Validation Errors** - Invalid result structure
   - Retry: No
   - Fallback: Log error, use partial results

4. **AI Analysis Errors** - API failures, rate limits
   - Retry: Yes (2 times)
   - Fallback: Use rule-based recommendations

5. **Database Errors** - Connection failures, constraint violations
   - Retry: Yes (3 times)
   - Fallback: Log error, return 500

### Logging Strategy

**Log Levels:**
- `ERROR`: Test failures, AI failures, database errors
- `WARNING`: Validation failures, partial results, retries
- `INFO`: Test start/complete, successful retries
- `DEBUG`: Individual test progress, detailed results

**Log Format:**
```
[TIMESTAMP] [LEVEL] [MODULE] [TEST_ID] Message
Context: {...}
Exception: ... (if applicable)
```

## Testing Strategy

### Unit Tests

1. **Test Retry Logic**
   - Test successful retry after failure
   - Test exhausted retries
   - Test exponential backoff

2. **Test Validation**
   - Test valid results pass validation
   - Test invalid results fail validation
   - Test partial results are detected

3. **Test Error Handling**
   - Test exceptions are logged
   - Test partial results are stored
   - Test fallback recommendations work

### Integration Tests

1. **Test End-to-End Flow**
   - Test with all tests succeeding
   - Test with some tests failing
   - Test with all tests failing
   - Test with AI analysis failing

2. **Test Database Operations**
   - Test storing partial results
   - Test storing error messages
   - Test retrieving results with errors

### Manual Testing

1. **Simulate Network Failures**
   - Disconnect network during test
   - Use invalid DNS servers
   - Test with firewall blocking

2. **Simulate Permission Errors**
   - Run without admin privileges
   - Test packet loss without permissions

3. **Simulate AI Failures**
   - Use invalid API key
   - Exceed rate limits

## Performance Considerations

- **Retry Delays**: Use exponential backoff to avoid overwhelming services
- **Timeout Values**: Set reasonable timeouts (30s for speed test, 5s for ping)
- **Parallel Execution**: Continue running tests in parallel where possible
- **Database Writes**: Batch recommendation inserts to reduce DB calls

## Security Considerations

- **Error Messages**: Don't expose sensitive information in error messages
- **API Keys**: Validate API key presence before attempting AI analysis
- **Input Validation**: Validate all user inputs before test execution
- **Rate Limiting**: Respect API rate limits with proper backoff

## Migration Plan

1. **Phase 1**: Add new database columns (test_status, errors)
2. **Phase 2**: Update backend models and validation
3. **Phase 3**: Update test runner with retry logic
4. **Phase 4**: Update API routes with better error handling
5. **Phase 5**: Update frontend to display status and errors
6. **Phase 6**: Deploy and monitor

## Rollback Plan

If issues occur:
1. Database columns are nullable, so old code continues to work
2. Frontend gracefully handles missing test_status/errors fields
3. Can revert backend changes without data loss
