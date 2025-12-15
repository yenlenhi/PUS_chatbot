"""
Feedback models for user feedback tracking and evaluation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class FeedbackRating(str, Enum):
    """Feedback rating options"""

    POSITIVE = "positive"  # 👍
    NEGATIVE = "negative"  # 👎
    NEUTRAL = "neutral"


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback"""

    conversation_id: str = Field(..., description="Conversation ID")
    message_id: Optional[str] = Field(
        None, description="Specific message ID if applicable"
    )
    query: str = Field(..., description="The user's original query")
    answer: str = Field(..., description="The bot's answer")
    rating: FeedbackRating = Field(
        ..., description="User rating (positive/negative/neutral)"
    )
    comment: Optional[str] = Field(
        None, max_length=1000, description="Optional user comment"
    )
    chunk_ids: Optional[List[int]] = Field(
        default_factory=list, description="IDs of chunks used in the answer"
    )
    user_id: Optional[str] = Field(None, description="User identifier (optional)")
    session_id: Optional[str] = Field(None, description="Session identifier")


class FeedbackResponse(BaseModel):
    """Response model after submitting feedback"""

    id: int = Field(..., description="Feedback record ID")
    status: str = Field(..., description="Status of feedback submission")
    message: str = Field(..., description="Confirmation message")


class FeedbackRecord(BaseModel):
    """Model representing a feedback record"""

    id: int
    conversation_id: str
    message_id: Optional[str]
    query: str
    answer: str
    rating: FeedbackRating
    comment: Optional[str]
    chunk_ids: List[int]
    user_id: Optional[str]
    session_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackStats(BaseModel):
    """Statistics about feedback"""

    total_feedback: int = Field(..., description="Total number of feedback records")
    positive_count: int = Field(..., description="Number of positive ratings")
    negative_count: int = Field(..., description="Number of negative ratings")
    neutral_count: int = Field(..., description="Number of neutral ratings")
    positive_rate: float = Field(..., description="Percentage of positive feedback")
    negative_rate: float = Field(..., description="Percentage of negative feedback")
    avg_response_quality: float = Field(
        ..., description="Average response quality score (0-1)"
    )


class FeedbackTimeStats(BaseModel):
    """Time-based feedback statistics"""

    date: str = Field(..., description="Date (YYYY-MM-DD)")
    total: int = Field(..., description="Total feedback for the day")
    positive: int = Field(..., description="Positive feedback count")
    negative: int = Field(..., description="Negative feedback count")
    neutral: int = Field(..., description="Neutral feedback count")


class ChunkPerformance(BaseModel):
    """Performance metrics for a specific chunk"""

    chunk_id: int = Field(..., description="Chunk ID")
    source_file: str = Field(..., description="Source file name")
    times_used: int = Field(..., description="Number of times used in answers")
    positive_feedback: int = Field(..., description="Positive feedback count when used")
    negative_feedback: int = Field(..., description="Negative feedback count when used")
    effectiveness_score: float = Field(..., description="Effectiveness score (0-1)")


class DashboardMetrics(BaseModel):
    """Dashboard monitoring metrics"""

    # Overall stats
    overall_stats: FeedbackStats

    # Time-based stats
    daily_stats: List[FeedbackTimeStats] = Field(default_factory=list)

    # Performance metrics
    avg_response_time_ms: float = Field(
        ..., description="Average response time in milliseconds"
    )
    total_queries: int = Field(..., description="Total number of queries processed")
    queries_with_feedback: int = Field(
        ..., description="Queries that received feedback"
    )
    feedback_rate: float = Field(..., description="Percentage of queries with feedback")

    # Top performing chunks
    top_chunks: List[ChunkPerformance] = Field(default_factory=list)

    # Worst performing chunks (for improvement)
    worst_chunks: List[ChunkPerformance] = Field(default_factory=list)

    # Recent feedback
    recent_negative_feedback: List[FeedbackRecord] = Field(default_factory=list)


class RetrievalWeightUpdate(BaseModel):
    """Model for retrieval weight updates based on feedback"""

    chunk_id: int
    old_weight: float
    new_weight: float
    feedback_count: int
    positive_rate: float
