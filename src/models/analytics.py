"""
Analytics models for dashboard insights
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class TimeRange(str, Enum):
    """Time range options for filtering"""

    LAST_7_DAYS = "L7D"
    MONTH_TO_DATE = "MTD"
    YEAR_TO_DATE = "YTD"
    CUSTOM = "custom"


# ==================== SYSTEM INSIGHTS ====================


class TokenUsage(BaseModel):
    """Token usage metrics"""

    date: str = Field(..., description="Date (YYYY-MM-DD)")
    hour: Optional[int] = Field(None, description="Hour of day (0-23)")
    input_tokens: int = Field(0, description="Input tokens used")
    output_tokens: int = Field(0, description="Output tokens used")
    total_tokens: int = Field(0, description="Total tokens used")
    estimated_cost: float = Field(0.0, description="Estimated cost in USD")


class SystemAccessMetrics(BaseModel):
    """System access metrics"""

    date: str = Field(..., description="Date (YYYY-MM-DD)")
    hour: Optional[int] = Field(None, description="Hour of day (0-23)")
    total_requests: int = Field(0, description="Total requests")
    unique_sessions: int = Field(0, description="Unique sessions")
    blocked_requests: int = Field(0, description="Blocked/rate-limited requests")


class SystemInsights(BaseModel):
    """System insights response model"""

    # Token usage
    token_usage_daily: List[TokenUsage] = Field(default_factory=list)
    token_usage_hourly: List[TokenUsage] = Field(default_factory=list)
    total_tokens: int = Field(0)
    total_estimated_cost: float = Field(0.0)

    # Access metrics
    access_daily: List[SystemAccessMetrics] = Field(default_factory=list)
    access_hourly: List[SystemAccessMetrics] = Field(default_factory=list)
    total_requests: int = Field(0)
    total_blocked: int = Field(0)

    # Period info
    period_start: str = Field(...)
    period_end: str = Field(...)


# ==================== USER INSIGHTS ====================


class UserFrequency(BaseModel):
    """User return frequency"""

    frequency: str = Field(..., description="1 lần, 2 lần, 5 lần, >5 lần")
    user_count: int = Field(0)
    percentage: float = Field(0.0)


class UserSegment(BaseModel):
    """User segmentation by question count"""

    segment: str = Field(..., description="Segment description")
    min_questions: int = Field(0)
    user_count: int = Field(0)
    percentage: float = Field(0.0)


class TopicInterest(BaseModel):
    """Topic user is interested in"""

    topic: str = Field(..., description="Topic name (tuyen sinh, hoc phi, etc.)")
    query_count: int = Field(0)
    percentage: float = Field(0.0)


class PopularQuestion(BaseModel):
    """Popular question"""

    question: str = Field(...)
    count: int = Field(0)
    last_asked: Optional[str] = Field(None)


class UserFunnelStage(BaseModel):
    """User funnel stage"""

    stage: str = Field(...)
    count: int = Field(0)
    percentage: float = Field(0.0)
    conversion_rate: Optional[float] = Field(None)


class DailyUsers(BaseModel):
    """Daily unique users"""

    date: str = Field(...)
    unique_users: int = Field(0)
    new_users: int = Field(0)
    returning_users: int = Field(0)


class UserInsights(BaseModel):
    """User insights response model"""

    # Daily unique users
    daily_users: List[DailyUsers] = Field(default_factory=list)
    total_unique_users: int = Field(0)

    # Return frequency
    return_frequency: List[UserFrequency] = Field(default_factory=list)

    # User segmentation
    user_segments: List[UserSegment] = Field(default_factory=list)

    # New vs Retain users
    new_users_ytd: int = Field(0)
    retain_users_ytd: int = Field(0)

    # Topics interest
    topics: List[TopicInterest] = Field(default_factory=list)

    # Popular questions
    popular_questions: List[PopularQuestion] = Field(default_factory=list)

    # User funnel
    funnel: List[UserFunnelStage] = Field(default_factory=list)

    # Period info
    period_start: str = Field(...)
    period_end: str = Field(...)


# ==================== CHAT INSIGHTS ====================


class ChatMetrics(BaseModel):
    """Daily chat metrics"""

    date: str = Field(...)
    user_messages: int = Field(0)
    ai_responses: int = Field(0)
    likes: int = Field(0)
    dislikes: int = Field(0)
    avg_messages_per_conversation: float = Field(0.0)
    avg_conversation_duration_seconds: float = Field(0.0)


class UnansweredQuestion(BaseModel):
    """Unanswered/fallback question"""

    question: str = Field(...)
    count: int = Field(0)
    last_occurrence: str = Field(...)


class LowRatedResponse(BaseModel):
    """Low rated response for improvement"""

    query: str = Field(...)
    answer: str = Field(...)
    dislike_count: int = Field(0)
    source_files: List[str] = Field(default_factory=list)


class ChatInsights(BaseModel):
    """Chat insights response model"""

    # Daily metrics
    daily_metrics: List[ChatMetrics] = Field(default_factory=list)

    # Totals
    total_user_messages: int = Field(0)
    total_ai_responses: int = Field(0)

    # Feedback rates
    like_rate: float = Field(0.0)
    dislike_rate: float = Field(0.0)

    # Averages
    avg_messages_per_conversation: float = Field(0.0)
    avg_conversation_duration_seconds: float = Field(0.0)

    # Problems
    unanswered_questions: List[UnansweredQuestion] = Field(default_factory=list)
    low_rated_responses: List[LowRatedResponse] = Field(default_factory=list)

    # Period info
    period_start: str = Field(...)
    period_end: str = Field(...)


# ==================== DOCUMENT INSIGHTS ====================


class CategoryStats(BaseModel):
    """Document statistics by category"""

    category: str = Field(...)
    document_count: int = Field(0)
    total_size_bytes: int = Field(0)
    active_count: int = Field(0)
    inactive_count: int = Field(0)


class TopDocument(BaseModel):
    """Top retrieved document"""

    filename: str = Field(...)
    retrieval_count: int = Field(0)
    positive_feedback: int = Field(0)
    negative_feedback: int = Field(0)
    effectiveness_score: float = Field(0.0)


class DocumentGrowth(BaseModel):
    """Document growth trend"""

    month: str = Field(..., description="YYYY-MM")
    new_documents: int = Field(0)
    total_documents: int = Field(0)
    total_size_bytes: int = Field(0)


class DocumentInsights(BaseModel):
    """Document insights response model"""

    # Overview
    total_documents: int = Field(0)
    total_size_bytes: int = Field(0)
    active_documents: int = Field(0)
    inactive_documents: int = Field(0)

    # By category
    category_stats: List[CategoryStats] = Field(default_factory=list)

    # Top documents
    top_retrieved_documents: List[TopDocument] = Field(default_factory=list)

    # Growth trend
    growth_trend: List[DocumentGrowth] = Field(default_factory=list)

    # Period info
    period_start: str = Field(...)
    period_end: str = Field(...)


# ==================== BUSINESS INSIGHTS ====================


class ContentGap(BaseModel):
    """Content gap analysis"""

    topic: str = Field(...)
    query_count: int = Field(0)
    document_coverage: float = Field(0.0, description="0-1 score of document coverage")
    suggested_action: str = Field(...)


class QualityScore(BaseModel):
    """Quality score breakdown"""

    category: str = Field(...)
    score: float = Field(0.0, description="0-100 score")
    weight: float = Field(0.0)


class BusinessInsights(BaseModel):
    """Business insights response model"""

    # Business impact
    estimated_hours_saved: float = Field(0.0)
    estimated_queries_handled: int = Field(0)
    avg_response_time_seconds: float = Field(0.0)

    # Content gap analysis
    content_gaps: List[ContentGap] = Field(default_factory=list)

    # Quality score
    overall_quality_score: float = Field(0.0)
    quality_breakdown: List[QualityScore] = Field(default_factory=list)

    # Period info
    period_start: str = Field(...)
    period_end: str = Field(...)


# ==================== DASHBOARD OVERVIEW ====================


class DashboardOverview(BaseModel):
    """Dashboard overview with key metrics"""

    # Quick stats
    total_conversations: int = Field(0)
    total_messages: int = Field(0)
    total_documents: int = Field(0)
    total_users: int = Field(0)

    # Changes (percentage)
    conversations_change: float = Field(0.0)
    messages_change: float = Field(0.0)
    documents_change: float = Field(0.0)
    users_change: float = Field(0.0)

    # Performance
    avg_response_time_ms: float = Field(0.0)
    response_time_change: float = Field(0.0)

    # Satisfaction
    satisfaction_rate: float = Field(0.0)
    satisfaction_change: float = Field(0.0)

    # Today's activity
    today_conversations: int = Field(0)
    today_messages: int = Field(0)
    today_new_users: int = Field(0)
