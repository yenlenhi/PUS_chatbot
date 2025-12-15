"""
Pydantic models for conversation memory
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role types"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    """Model for a single conversation message"""

    id: Optional[int] = None
    conversation_id: str = Field(..., description="Conversation identifier")
    role: MessageRole = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class MemorySummary(BaseModel):
    """Model for conversation memory summary"""

    id: Optional[int] = None
    conversation_id: str = Field(..., description="Conversation identifier")
    summary: str = Field(..., description="Summarized conversation content")
    turn_start: int = Field(
        ..., description="Starting turn number of summarized content"
    )
    turn_end: int = Field(..., description="Ending turn number of summarized content")
    embedding: Optional[List[float]] = Field(
        None, description="Vector embedding of summary"
    )
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ConversationContext(BaseModel):
    """Model for conversation context with memory"""

    conversation_id: str
    recent_messages: List[ConversationMessage] = Field(default_factory=list)
    memory_summaries: List[str] = Field(default_factory=list)
    total_turns: int = 0
    has_long_term_memory: bool = False


class MemoryConfig(BaseModel):
    """Configuration for memory management"""

    # Sliding window settings
    max_recent_turns: int = Field(
        default=10, description="Max recent turns to keep in context"
    )
    summarize_threshold: int = Field(
        default=10, description="Turns before triggering summarization"
    )

    # Summary settings
    max_summary_length: int = Field(
        default=500, description="Max characters for summary"
    )
    overlap_turns: int = Field(
        default=2, description="Overlapping turns when summarizing"
    )

    # Vector search settings
    memory_search_top_k: int = Field(
        default=3, description="Top K memory summaries to retrieve"
    )
    memory_similarity_threshold: float = Field(
        default=0.5, description="Min similarity for memory retrieval"
    )


class MemoryStats(BaseModel):
    """Statistics about conversation memory"""

    conversation_id: str
    total_messages: int
    total_summaries: int
    total_turns: int
    oldest_message: Optional[datetime]
    newest_message: Optional[datetime]
    memory_size_bytes: int
