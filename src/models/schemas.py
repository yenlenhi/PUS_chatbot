"""
Pydantic models for request/response schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ImageInput(BaseModel):
    """Model for image input in chat"""

    base64: str = Field(..., description="Base64 encoded image data")
    mime_type: str = Field(
        ..., description="Image MIME type (e.g., image/jpeg, image/png)"
    )
    name: Optional[str] = Field(None, description="Original filename")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    message: str = Field(default="", max_length=1000, description="User's message")
    conversation_id: Optional[str] = Field(
        None, description="Optional conversation ID for context"
    )
    conversation_history: Optional[List[dict]] = Field(
        default_factory=list, description="Optional conversation history"
    )
    images: Optional[List[ImageInput]] = Field(
        default_factory=list, description="Optional images for vision analysis"
    )
    language: Optional[str] = Field(
        default="vi",
        description="Response language: 'vi' for Vietnamese (default) or 'en' for English",
    )


class SourceReference(BaseModel):
    """Detailed source reference model"""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    filename: str = Field(..., description="Source PDF filename")
    page_number: Optional[int] = Field(None, description="Page number in PDF")
    heading: Optional[str] = Field(None, description="Section heading")
    content_snippet: str = Field(
        ..., description="Brief preview of the content (max 200 chars)"
    )
    full_content: str = Field(..., description="Full chunk content")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    dense_score: Optional[float] = Field(None, description="Dense search score")
    sparse_score: Optional[float] = Field(None, description="Sparse search score")


class FileAttachment(BaseModel):
    """Model for file attachments in chat response"""

    file_name: str = Field(..., description="Name of the file")
    file_type: str = Field(..., description="File type (doc, docx, xlsx, pdf, etc.)")
    download_url: str = Field(..., description="URL to download the file")
    description: Optional[str] = Field(None, description="Description of the file")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class ChartData(BaseModel):
    """Model for chart payloads in chat responses."""

    type: str = Field(..., description="Chart type")
    title: Optional[str] = Field(None, description="Chart title")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Chart data")
    xKey: Optional[str] = Field(None, description="X-axis key")
    yKeys: List[str] = Field(default_factory=list, description="Y-axis keys")
    labels: List[str] = Field(default_factory=list, description="Label set")
    description: Optional[str] = Field(None, description="Chart description")


class ChatImage(BaseModel):
    """Model for images returned in chat responses."""

    src: str = Field(..., description="Image URL or base64 string")
    alt: Optional[str] = Field(None, description="Alt text")
    caption: Optional[str] = Field(None, description="Image caption")
    source_file: Optional[str] = Field(None, description="Source filename")
    page_number: Optional[int] = Field(None, description="Source page number")


class PerformanceMetrics(BaseModel):
    """Latency and execution metadata for chat responses."""

    total_ms: float = Field(..., description="Total pipeline time in milliseconds")
    stages: Dict[str, float] = Field(
        default_factory=dict, description="Stage-by-stage latency in milliseconds"
    )
    time_to_first_token_ms: Optional[float] = Field(
        None, description="Time to first streamed token in milliseconds"
    )
    retrieval_cache_hit: bool = Field(
        default=False, description="Whether retrieval was served from cache"
    )
    attachment_lookup_skipped: bool = Field(
        default=False,
        description="Whether attachment retrieval was skipped by heuristic",
    )
    needs_grounding: bool = Field(
        default=False, description="Whether web grounding/search was enabled"
    )
    normalization_applied: bool = Field(
        default=False, description="Whether query normalization changed the input"
    )
    rewrite_applied: bool = Field(
        default=False, description="Whether the query was rewritten using history"
    )
    memory_loaded: bool = Field(
        default=False, description="Whether conversation memory context was loaded"
    )
    retrieved_chunk_count: int = Field(
        default=0, description="Number of retrieved chunks used for answering"
    )
    response_path: str = Field(
        default="rag", description="Path used to answer: rag, policy, or vision"
    )
    policy_applied: Optional[str] = Field(
        default=None, description="Policy applied when the pipeline short-circuits"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""

    answer: str = Field(..., description="Generated answer")
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Suggested next questions derived from the current answer",
    )
    sources: List[str] = Field(
        default_factory=list, description="Source document names (backward compatible)"
    )
    source_references: List[SourceReference] = Field(
        default_factory=list, description="Detailed source references with metadata"
    )
    attachments: List[FileAttachment] = Field(
        default_factory=list, description="File attachments (forms, templates, etc.)"
    )
    chart_data: List[ChartData] = Field(
        default_factory=list, description="Chart data for frontend visualizations"
    )
    images: List[ChatImage] = Field(
        default_factory=list, description="Image payloads for frontend rendering"
    )
    confidence: float = Field(..., description="Confidence score")
    conversation_id: str = Field(..., description="Conversation ID")
    processing_time: float = Field(..., description="Processing time in seconds")
    normalization_applied: bool = Field(
        default=False, description="Whether Gemini normalization was applied"
    )
    original_query: Optional[str] = Field(
        default=None, description="Original user query before normalization"
    )
    normalized_query: Optional[str] = Field(
        default=None, description="Normalized query after Gemini processing"
    )
    performance: Optional[PerformanceMetrics] = Field(
        default=None, description="Optional performance breakdown for benchmarking"
    )


class SearchRequest(BaseModel):
    """Request model for search endpoint"""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")


class SearchResult(BaseModel):
    """Search result model"""

    content: str = Field(..., description="Content of the chunk")
    source: str = Field(..., description="Source document")
    score: float = Field(..., description="Similarity score")


class SearchResponse(BaseModel):
    """Response model for search endpoint"""

    results: List[SearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of results found")


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database_status: str = Field(..., description="Database status")


class DocumentChunk(BaseModel):
    """Model for document chunks"""

    id: Optional[int] = Field(None, description="Chunk ID")
    content: str = Field(..., description="Chunk content")
    source_file: str = Field(..., description="Source PDF file")
    page_number: Optional[int] = Field(None, description="Page number")
    chunk_index: int = Field(..., description="Index of chunk in document")

    # Enhanced metadata for heading-based chunking
    heading_text: Optional[str] = Field(
        None, description="Heading text if this chunk starts with a heading"
    )
    heading_level: Optional[int] = Field(
        None, description="Heading level (1, 2, 3, etc.)"
    )
    heading_number: Optional[str] = Field(
        None, description="Heading number (e.g., '7.3.1')"
    )
    parent_heading: Optional[str] = Field(
        None, description="Parent heading number (e.g., '7.3' for '7.3.1')"
    )
    is_sub_chunk: bool = Field(
        False, description="Whether this is a sub-chunk of a larger heading"
    )
    sub_chunk_index: Optional[int] = Field(
        None, description="Index of sub-chunk within the same heading"
    )
    total_sub_chunks: Optional[int] = Field(
        None, description="Total number of sub-chunks for this heading"
    )
    chunk_type: str = Field(
        "content", description="Type of chunk: 'intro', 'heading', 'content'"
    )
    word_count: Optional[int] = Field(None, description="Number of words in the chunk")
    char_count: Optional[int] = Field(
        None, description="Number of characters in the chunk"
    )


class EmbeddingData(BaseModel):
    """Model for embedding data"""

    chunk_id: int = Field(..., description="Associated chunk ID")
    embedding: List[float] = Field(..., description="Embedding vector")


class DocumentAttachment(BaseModel):
    """Model for document attachments (forms, templates, etc.)"""

    id: Optional[int] = Field(None, description="Attachment ID")
    file_name: str = Field(..., description="Name of the file")
    file_type: str = Field(..., description="File type (doc, docx, xlsx, pdf, etc.)")
    file_path: str = Field(..., description="Path to the file")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    description: Optional[str] = Field(
        None, description="Description of the attachment"
    )
    keywords: Optional[List[str]] = Field(
        default_factory=list, description="Keywords for searching"
    )
    download_url: Optional[str] = Field(None, description="URL to download the file")
    category: Optional[str] = Field(
        "Khác", description="Category of the attachment (e.g., Tuyển sinh, Đào tạo)"
    )
    public_url: Optional[str] = Field(
        None, description="Direct public URL to the file on Supabase"
    )
    is_active: bool = Field(True, description="Whether the attachment is active")


class PaginatedAttachmentResponse(BaseModel):
    """Response model for paginated attachments"""

    items: List[DocumentAttachment] = Field(..., description="List of attachments")
    total: int = Field(..., description="Total number of attachments")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
