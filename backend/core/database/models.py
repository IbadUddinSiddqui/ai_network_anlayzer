"""
Pydantic models for data validation and serialization.
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class TestStatus(str, Enum):
    """Network test status enumeration."""
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"  # Some tests succeeded, some failed
    FAILED = "failed"


class IndividualTestStatus(str, Enum):
    """Status for individual test types."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class Severity(str, Enum):
    """Recommendation severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


# ============================================================================
# Request Models
# ============================================================================

class TestConfig(BaseModel):
    """Configuration for network test execution."""
    target_hosts: List[str] = Field(
        default=["8.8.8.8", "1.1.1.1"],
        description="List of hosts to ping"
    )
    dns_servers: List[str] = Field(
        default=["8.8.8.8", "1.1.1.1"],
        description="List of DNS servers to test"
    )
    packet_count: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Number of packets for packet loss test"
    )
    # Test selection flags
    run_ping: bool = Field(default=True, description="Run ping test")
    run_jitter: bool = Field(default=True, description="Run jitter test")
    run_packet_loss: bool = Field(default=True, description="Run packet loss test")
    run_speed: bool = Field(default=True, description="Run speed test")
    run_dns: bool = Field(default=True, description="Run DNS test")
    
    @validator('target_hosts', 'dns_servers')
    def validate_not_empty(cls, v):
        """Ensure lists are not empty."""
        if not v:
            raise ValueError("List cannot be empty")
        return v
    
    @validator('run_dns')
    def validate_at_least_one_test(cls, v, values):
        """Ensure at least one test is selected."""
        # This runs last since run_dns is the last field
        if not any([
            values.get('run_ping', True),
            values.get('run_jitter', True),
            values.get('run_packet_loss', True),
            values.get('run_speed', True),
            v
        ]):
            raise ValueError("At least one test must be selected")
        return v


class OptimizationActionRequest(BaseModel):
    """Request model for applying an optimization."""
    recommendation_id: UUID = Field(description="ID of the recommendation being applied")
    action_taken: str = Field(min_length=1, max_length=1000, description="Description of action taken")
    notes: Optional[str] = Field(None, max_length=2000, description="Optional notes")


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    test_id: Optional[UUID] = Field(None, description="Optional test ID")
    recommendation_id: Optional[UUID] = Field(None, description="Optional recommendation ID")
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=2000, description="Optional comment")


# ============================================================================
# Network Test Result Models
# ============================================================================

class PingResult(BaseModel):
    """Result from ping test."""
    host: str
    packets_sent: int
    packets_received: int
    min_ms: float
    max_ms: float
    avg_ms: float
    stddev_ms: float


class JitterResult(BaseModel):
    """Result from jitter test."""
    avg_jitter_ms: float
    max_jitter_ms: float
    measurements: List[float] = Field(default_factory=list)


class PacketLossResult(BaseModel):
    """Result from packet loss test."""
    packets_sent: int
    packets_received: int
    loss_percentage: float


class SpeedResult(BaseModel):
    """Result from speed test."""
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    server_location: str


class DNSResult(BaseModel):
    """Result from DNS test."""
    dns_server: str
    avg_resolution_ms: float
    queries_tested: int
    successful_queries: int


class TestStatusDetail(BaseModel):
    """Detailed status for each test type."""
    ping: IndividualTestStatus = IndividualTestStatus.SKIPPED
    jitter: IndividualTestStatus = IndividualTestStatus.SKIPPED
    packet_loss: IndividualTestStatus = IndividualTestStatus.SKIPPED
    speed: IndividualTestStatus = IndividualTestStatus.SKIPPED
    dns: IndividualTestStatus = IndividualTestStatus.SKIPPED


class TestErrors(BaseModel):
    """Error messages for failed tests."""
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
    test_status: Optional[TestStatusDetail] = None
    errors: Optional[TestErrors] = None


# ============================================================================
# AI Recommendation Models
# ============================================================================

class AIRecommendation(BaseModel):
    """AI-generated recommendation."""
    id: UUID
    test_id: UUID
    agent_type: str = Field(description="Type of agent that generated recommendation")
    recommendation_text: str = Field(description="Human-readable recommendation")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    severity: Severity
    created_at: datetime


class AIRecommendationCreate(BaseModel):
    """Model for creating AI recommendation."""
    test_id: UUID
    agent_type: str
    recommendation_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    severity: Severity


# ============================================================================
# Database Entity Models
# ============================================================================

class User(BaseModel):
    """User profile model."""
    id: UUID
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class NetworkTest(BaseModel):
    """Network test database model."""
    id: UUID
    user_id: UUID
    test_timestamp: datetime
    ping_results: Dict[str, Any]
    jitter_results: Dict[str, Any]
    packet_loss_results: Dict[str, Any]
    speed_results: Dict[str, Any]
    dns_results: Dict[str, Any]
    status: TestStatus
    created_at: datetime


class OptimizationHistory(BaseModel):
    """Optimization history database model."""
    id: UUID
    user_id: UUID
    recommendation_id: UUID
    action_taken: str
    applied_at: datetime
    notes: Optional[str] = None


class Feedback(BaseModel):
    """Feedback database model."""
    id: UUID
    user_id: UUID
    test_id: Optional[UUID] = None
    recommendation_id: Optional[UUID] = None
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime


# ============================================================================
# Response Models
# ============================================================================

class TestInitiatedResponse(BaseModel):
    """Response when test is initiated."""
    test_id: UUID
    status: TestStatus
    message: str = "Network test initiated successfully"


class TestResultsResponse(BaseModel):
    """Response with test results and recommendations."""
    test_results: NetworkTestResult
    ai_recommendations: List[AIRecommendation]
    status: TestStatus


class OptimizationResponse(BaseModel):
    """Response after applying optimization."""
    optimization_id: UUID
    success: bool = True
    message: str = "Optimization recorded successfully"


class FeedbackResponse(BaseModel):
    """Response after submitting feedback."""
    feedback_id: UUID
    success: bool = True
    message: str = "Feedback submitted successfully"


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    database_connected: bool
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str
    code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Pagination Models
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
