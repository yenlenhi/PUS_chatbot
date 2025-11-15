"""
FastAPI routes for the chatbot API
"""

from fastapi import APIRouter, HTTPException, Depends
import time
from src.models.schemas import (
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SearchResponse,
    HealthResponse,
    SearchResult,
)
from src.services.rag_service import RAGService
from src.utils.logger import log

# Create router
router = APIRouter()

# Global RAG service instance
rag_service = None


def get_rag_service() -> RAGService:
    """Dependency to get RAG service instance"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, rag: RAGService = Depends(get_rag_service)
):
    start_time = time.time()
    try:
        log.info(f"Received chat request: {request.message[:50]}...")

        # Get RAG response
        rag_response = rag.generate_answer(
            query=request.message,
            conversation_id=request.conversation_id,
            conversation_history=request.conversation_history,
        )

        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)

        # Create response object
        response = ChatResponse(
            answer=rag_response.get(
                "answer", "Xin lỗi, tôi không thể trả lời câu hỏi này."
            ),
            sources=rag_response.get("sources", []),
            confidence=rag_response.get("confidence", 0.0),
            conversation_id=rag_response.get(
                "conversation_id", request.conversation_id or "default"
            ),
            processing_time=processing_time,
            normalization_applied=rag_response.get("normalization_applied", False),
            original_query=rag_response.get("original_query"),
            normalized_query=rag_response.get("normalized_query"),
        )

        log.info(f"Chat request processed in {processing_time:.2f} seconds")
        return response
    except Exception as e:
        log.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}",
        )


@router.post("/search", response_model=SearchResponse)
async def search_endpoint(
    request: SearchRequest, rag: RAGService = Depends(get_rag_service)
):
    """
    Search endpoint for retrieving relevant chunks
    """
    try:
        # Đổi từ 'query' sang 'message' nếu cần
        query = request.query
        top_k = request.top_k

        # Retrieve relevant chunks
        results = rag.retrieve_relevant_chunks(query=query, top_k=top_k)

        return SearchResponse(
            results=[
                SearchResult(
                    content=result["content"],
                    source=result.get("source_file", "Unknown"),
                    score=result.get("similarity_score", 0.0),
                )
                for result in results
            ],
            total_found=len(results),
        )

    except Exception as e:
        log.error(f"Error in search endpoint: {e}")
        raise HTTPException(
            status_code=500, detail="Đã xảy ra lỗi khi tìm kiếm. Vui lòng thử lại sau."
        )


@router.get("/health", response_model=HealthResponse)
async def health_endpoint(rag: RAGService = Depends(get_rag_service)):
    """
    Health check endpoint
    """
    try:
        # Check system health
        health = rag.check_system_health()

        # Determine component statuses
        ollama_status = health["components"].get("ollama", {}).get("status", "unknown")
        database_status = (
            health["components"].get("database", {}).get("status", "unknown")
        )

        return HealthResponse(
            status=health["overall_status"],
            version="1.0.0",
            ollama_status=ollama_status,
            database_status=database_status,
        )

    except Exception as e:
        log.error(f"Error in health endpoint: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            ollama_status="unknown",
            database_status="unknown",
        )


@router.get("/conversation/{conversation_id}")
async def get_conversation_endpoint(
    conversation_id: str, rag: RAGService = Depends(get_rag_service)
):
    """
    Get conversation history
    """
    try:
        history = rag.get_conversation_history(conversation_id)
        return {"conversation_id": conversation_id, "history": history}

    except Exception as e:
        log.error(f"Error getting conversation: {e}")
        raise HTTPException(
            status_code=500, detail="Đã xảy ra lỗi khi lấy lịch sử hội thoại."
        )


@router.get("/stats")
async def stats_endpoint(rag: RAGService = Depends(get_rag_service)):
    """
    Get system statistics
    """
    try:
        # Get database stats
        db_stats = rag.db_service.get_database_stats()

        # Get embedding dimension
        embedding_dim = rag.embedding_service.get_embedding_dimension()

        # Get ingestion stats
        ingestion_stats = rag.ingestion_service.get_ingestion_stats()

        return {
            "database": db_stats,
            "embedding_dimension": embedding_dim,
            "ingestion": ingestion_stats,
            "active_conversations": len(rag.conversations),
        }

    except Exception as e:
        log.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500, detail="Đã xảy ra lỗi khi lấy thống kê hệ thống."
        )
