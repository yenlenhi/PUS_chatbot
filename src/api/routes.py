"""
FastAPI routes for the chatbot API
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    Query,
    Request,
)
from fastapi.responses import JSONResponse, FileResponse
import time
import datetime
from pathlib import Path
from typing import Optional, List
from src.models.schemas import (
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SearchResponse,
    HealthResponse,
    SearchResult,
    DocumentAttachment,
)
from src.models.feedback import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackStats,
    DashboardMetrics,
)
from src.models.analytics import (
    TimeRange,
    SystemInsights,
    UserInsights,
    ChatInsights,
    DocumentInsights,
    BusinessInsights,
    DashboardOverview,
)
from src.services.rag_service import RAGService
from src.services.feedback_service import FeedbackService
from src.services.analytics_service import AnalyticsService
from src.services.attachment_service import AttachmentService
from src.services.postgres_database_service import PostgresDatabaseService
from src.services.supabase_storage_service import get_supabase_storage_service
from src.utils.logger import log

# Create router
router = APIRouter()

# Global service instances
rag_service = None
feedback_service = None
analytics_service = None
attachment_service = None

# Cache for suggested questions (simple in-memory cache)
_suggested_questions_cache = {
    "questions": None,
    "timestamp": None,
    "ttl": 3600,  # 1 hour in seconds
}


def get_rag_service() -> RAGService:
    """Dependency to get RAG service instance"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service


def get_feedback_service() -> FeedbackService:
    """Dependency to get Feedback service instance"""
    global feedback_service
    if feedback_service is None:
        feedback_service = FeedbackService()
    return feedback_service


def get_analytics_service() -> AnalyticsService:
    """Dependency to get Analytics service instance"""
    global analytics_service
    if analytics_service is None:
        analytics_service = AnalyticsService()
    return analytics_service


def get_attachment_service() -> AttachmentService:
    """Dependency to get Attachment service instance"""
    global attachment_service
    if attachment_service is None:
        db_service = PostgresDatabaseService()
        attachment_service = AttachmentService(db_service)
    return attachment_service


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    fastapi_request: Request,
    background_tasks: BackgroundTasks,
    rag: RAGService = Depends(get_rag_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    start_time = time.time()
    try:
        log.info(
            f"Received chat request: {request.message[:50] if request.message else '[Image only]'}..."
        )
        log.info(f"Images count: {len(request.images) if request.images else 0}")

        # Get RAG response (with images if provided)
        rag_response = rag.generate_answer(
            query=request.message,
            conversation_id=request.conversation_id,
            conversation_history=request.conversation_history,
            images=request.images,
            language=request.language or "vi",  # Pass language preference
        )

        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)
        processing_time_ms = processing_time * 1000

        # Create response object
        response = ChatResponse(
            answer=rag_response.get(
                "answer", "Xin lỗi, tôi không thể trả lời câu hỏi này."
            ),
            sources=rag_response.get("sources", []),
            source_references=rag_response.get("source_references", []),
            confidence=rag_response.get("confidence", 0.0),
            conversation_id=rag_response.get(
                "conversation_id", request.conversation_id or "default"
            ),
            processing_time=processing_time,
            normalization_applied=rag_response.get("normalization_applied", False),
            original_query=rag_response.get("original_query"),
            normalized_query=rag_response.get("normalized_query"),
        )

        # Track analytics in background (non-blocking)
        session_id = request.conversation_id or rag_response.get(
            "conversation_id", "default"
        )
        ip_address = fastapi_request.client.host if fastapi_request.client else None
        user_agent = fastapi_request.headers.get("user-agent", "")

        # Get retrieved documents and scores from rag_response
        retrieved_docs = rag_response.get("sources", [])
        relevance_scores = rag_response.get("relevance_scores", [])
        if not relevance_scores and retrieved_docs:
            # Default scores if not provided
            relevance_scores = [rag_response.get("confidence", 0.5)] * len(
                retrieved_docs
            )

        # Estimate token counts (rough estimation based on text length)
        input_tokens = len(request.message.split()) * 2 if request.message else 0
        output_tokens = len(response.answer.split()) * 2 if response.answer else 0

        # Schedule background tracking
        background_tasks.add_task(
            analytics.track_chat_interaction,
            session_id=session_id,
            conversation_id=response.conversation_id,
            query=request.message or "",
            response=response.answer,
            confidence=response.confidence,
            retrieved_documents=retrieved_docs,
            relevance_scores=relevance_scores,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time_ms=processing_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Log access
        background_tasks.add_task(
            analytics.log_access,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint="/api/v1/chat",
            method="POST",
            status_code=200,
            response_time_ms=processing_time_ms,
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


# ==================== PDF Document Endpoints ====================


@router.get("/documents")
async def list_documents():
    """
    List all available PDF documents
    """
    from pathlib import Path
    from config.settings import PROCESSED_PDF_DIR

    try:
        pdf_dir = Path(PROCESSED_PDF_DIR)
        if not pdf_dir.exists():
            return {"documents": [], "total": 0}

        documents = []
        for pdf_file in pdf_dir.glob("*.pdf"):
            stat = pdf_file.stat()
            documents.append(
                {
                    "filename": pdf_file.name,
                    "size_bytes": stat.st_size,
                    "modified_at": stat.st_mtime,
                }
            )

        return {
            "documents": sorted(documents, key=lambda x: x["filename"]),
            "total": len(documents),
        }

    except Exception as e:
        log.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail="Error listing documents")


@router.get("/documents/{filename}")
async def get_document(filename: str, page: int = None):
    """
    Get a PDF document by filename

    Args:
        filename: PDF filename
        page: Optional page number for reference (client-side navigation)

    Returns:
        PDF file response
    """
    from pathlib import Path
    from fastapi.responses import FileResponse
    from config.settings import DATA_DIR
    import urllib.parse

    try:
        # Decode URL-encoded filename
        decoded_filename = urllib.parse.unquote(filename)

        # Sanitize filename to prevent directory traversal
        safe_filename = Path(decoded_filename).name

        # Search for the file in DATA_DIR and subdirectories
        data_dir = Path(DATA_DIR)
        file_path = None

        for pdf_file in data_dir.rglob("*.pdf"):
            if pdf_file.name == safe_filename:
                # Skip backup folders
                if "backup" in str(pdf_file.parent).lower():
                    continue
                file_path = pdf_file
                break

        if not file_path or not file_path.exists():
            log.warning(f"Document not found: {safe_filename}")
            raise HTTPException(
                status_code=404, detail=f"Document not found: {safe_filename}"
            )

        # Security check: ensure the resolved path is within DATA_DIR
        if not file_path.resolve().is_relative_to(data_dir.resolve()):
            log.warning(f"Directory traversal attempt: {filename}")
            raise HTTPException(status_code=403, detail="Access denied")

        if not file_path.suffix.lower() == ".pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        log.info(
            f"Serving document: {safe_filename}" + (f" (page {page})" if page else "")
        )

        # Encode filename for Content-Disposition header (handle Unicode)
        from urllib.parse import quote

        encoded_filename = quote(safe_filename)

        # Return the PDF file
        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=safe_filename,
            headers={
                "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}",
                "X-Page-Number": str(page) if page else "1",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error serving document {filename}: {e}")
        raise HTTPException(status_code=500, detail="Error serving document")


@router.get("/documents/{filename}/info")
async def get_document_info(filename: str):
    """
    Get metadata about a PDF document
    """
    from pathlib import Path
    from config.settings import DATA_DIR
    import urllib.parse

    try:
        decoded_filename = urllib.parse.unquote(filename)
        safe_filename = Path(decoded_filename).name

        # Search for the file in DATA_DIR and subdirectories
        data_dir = Path(DATA_DIR)
        file_path = None

        for pdf_file in data_dir.rglob("*.pdf"):
            if pdf_file.name == safe_filename:
                # Skip backup folders
                if "backup" in str(pdf_file.parent).lower():
                    continue
                file_path = pdf_file
                break

        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")

        stat = file_path.stat()

        # Try to get page count using PyMuPDF if available
        page_count = None
        try:
            import fitz  # PyMuPDF

            with fitz.open(str(file_path)) as doc:
                page_count = len(doc)
        except ImportError:
            log.debug("PyMuPDF not available for page count")
        except Exception as e:
            log.warning(f"Could not get page count: {e}")

        return {
            "filename": safe_filename,
            "size_bytes": stat.st_size,
            "modified_at": stat.st_mtime,
            "page_count": page_count,
            "download_url": f"/api/v1/documents/{filename}",
        }

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting document info: {e}")
        raise HTTPException(status_code=500, detail="Error getting document info")


# ==================== Admin Endpoints ====================


@router.get("/admin/documents")
async def admin_list_documents(rag: RAGService = Depends(get_rag_service)):
    """
    Admin endpoint: List all documents with full metadata and statistics
    Gets documents from database (chunks table) - works with both local and Supabase Storage
    """
    import datetime

    try:
        documents = []

        # Get document info from database - source files with chunk counts and status
        try:
            from sqlalchemy import text

            session = rag.db_service.SessionLocal()

            # Get unique source files with their chunk counts, active status, and created_at
            result = session.execute(
                text(
                    """
                    SELECT 
                        source_file,
                        COUNT(*) as chunk_count,
                        COALESCE(bool_and(is_active), true) as is_active,
                        MIN(created_at) as first_created,
                        MAX(created_at) as last_updated
                    FROM chunks 
                    GROUP BY source_file
                    ORDER BY MAX(created_at) DESC
                    """
                )
            )

            for row in result.fetchall():
                source_file = row[0]
                chunk_count = row[1]
                is_active = row[2] if row[2] is not None else True
                created_at = row[3]

                # Calculate category based on filename patterns
                category = "Khác"
                filename_lower = source_file.lower()
                if (
                    "tuyen sinh" in filename_lower
                    or "tuyển sinh" in filename_lower
                    or "tuyen_sinh" in filename_lower
                ):
                    category = "Tuyển sinh"
                elif (
                    "dao tao" in filename_lower
                    or "đào tạo" in filename_lower
                    or "dao_tao" in filename_lower
                ):
                    category = "Đào tạo"
                elif "hoc phi" in filename_lower or "học phí" in filename_lower:
                    category = "Tài chính"
                elif "ky tuc xa" in filename_lower or "ký túc xá" in filename_lower:
                    category = "Sinh viên"
                elif "quy che" in filename_lower or "quy_che" in filename_lower:
                    category = "Quy chế"
                elif "thong bao" in filename_lower or "thong_bao" in filename_lower:
                    category = "Thông báo"

                # Determine status
                if chunk_count == 0:
                    status = "pending"
                elif is_active:
                    status = "active"
                else:
                    status = "inactive"

                # Format date
                upload_date = created_at.strftime("%Y-%m-%d") if created_at else "N/A"
                upload_datetime = (
                    created_at.isoformat()
                    if created_at
                    else datetime.datetime.now().isoformat()
                )

                documents.append(
                    {
                        "id": source_file.replace(".pdf", "").replace(" ", "_"),
                        "name": source_file,
                        "category": category,
                        "size": 0,  # Size not available from DB
                        "size_formatted": "N/A",
                        "uploadDate": upload_date,
                        "uploadDateTime": upload_datetime,
                        "status": status,
                        "is_active": is_active,
                        "downloads": 0,
                        "format": "PDF",
                        "chunks": chunk_count,
                        "path": source_file,
                    }
                )

            session.close()

        except Exception as e:
            log.error(f"Error getting documents from database: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error getting documents: {str(e)}"
            )

        return {
            "documents": documents,
            "total": len(documents),
            "categories": [
                "Tất cả",
                "Đào tạo",
                "Tuyển sinh",
                "Tài chính",
                "Sinh viên",
                "Quy chế",
                "Thông báo",
                "Khác",
            ],
        }

    except Exception as e:
        log.error(f"Error listing admin documents: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error listing documents: {str(e)}"
        )


@router.delete("/admin/documents/{filename}")
async def admin_delete_document(
    filename: str, rag: RAGService = Depends(get_rag_service)
):
    """
    Admin endpoint: Delete a document and its associated data from Supabase Storage
    """
    from pathlib import Path
    from config.settings import PDF_DIR, SUPABASE_URL, SUPABASE_SERVICE_KEY
    import urllib.parse

    try:
        decoded_filename = urllib.parse.unquote(filename)
        safe_filename = Path(decoded_filename).name

        # Delete from database first
        success = rag.db_service.delete_chunks_by_file(safe_filename)

        if success:
            # Try to delete from Supabase Storage
            try:
                from supabase import create_client

                if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
                    # Delete from 'documents' bucket
                    result = supabase.storage.from_("documents").remove([safe_filename])
                    log.info(f"Deleted from Supabase Storage: {safe_filename}")
            except Exception as storage_error:
                log.warning(f"Could not delete from Supabase Storage: {storage_error}")

            # Also try to delete local file if exists
            pdf_dir = Path(PDF_DIR)
            file_path = pdf_dir / safe_filename
            if file_path.exists():
                file_path.unlink()
                log.info(f"Deleted local file: {safe_filename}")

            # Rebuild BM25 index after deletion
            if hasattr(rag, "retrieval_service") and rag.retrieval_service:
                try:
                    rag.retrieval_service.rebuild_bm25_index()
                    log.info("BM25 index rebuilt after document deletion")
                except Exception as e:
                    log.warning(f"Could not rebuild BM25 index: {e}")

            return {
                "success": True,
                "message": f"Document '{safe_filename}' deleted successfully",
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to delete document from database"
            )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting document: {str(e)}"
        )


@router.patch("/admin/documents/{filename}/toggle-active")
async def admin_toggle_document_active(
    filename: str, rag: RAGService = Depends(get_rag_service)
):
    """
    Admin endpoint: Toggle active status of a document.
    When is_active=false, chunks from this document won't be retrieved by LLM.
    """
    from sqlalchemy import text
    import urllib.parse

    try:
        decoded_filename = urllib.parse.unquote(filename)

        # Get current status and toggle it
        session = rag.db_service.SessionLocal()

        # First check if document exists in chunks
        result = session.execute(
            text(
                "SELECT COUNT(*), bool_and(is_active) FROM chunks WHERE source_file = :source_file"
            ),
            {"source_file": decoded_filename},
        )
        row = result.fetchone()
        chunk_count = row[0]
        current_status = row[1] if row[1] is not None else True

        if chunk_count == 0:
            session.close()
            raise HTTPException(
                status_code=404,
                detail=f"No chunks found for document: {decoded_filename}",
            )

        # Toggle the status
        new_status = not current_status
        session.execute(
            text(
                "UPDATE chunks SET is_active = :is_active WHERE source_file = :source_file"
            ),
            {"is_active": new_status, "source_file": decoded_filename},
        )
        session.commit()
        session.close()

        # Rebuild BM25 index to reflect changes
        if hasattr(rag, "retrieval_service") and rag.retrieval_service:
            try:
                rag.retrieval_service.rebuild_bm25_index()
                log.info(
                    f"BM25 index rebuilt after toggling document: {decoded_filename}"
                )
            except Exception as e:
                log.warning(f"Could not rebuild BM25 index: {e}")

        status_text = "activated" if new_status else "deactivated"
        log.info(f"Document {decoded_filename} {status_text} ({chunk_count} chunks)")

        return {
            "success": True,
            "message": f"Document '{decoded_filename}' has been {status_text}",
            "filename": decoded_filename,
            "is_active": new_status,
            "chunks_affected": chunk_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error toggling document active status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error toggling document status: {str(e)}"
        )


@router.post("/admin/upload")
async def admin_upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = Form("Khác"),
    use_gemini: bool = Form(True),
    rag: RAGService = Depends(get_rag_service),
):
    """
    Admin endpoint: Upload and process a PDF document

    This endpoint:
    1. Validates the uploaded file (PDF only, max 50MB)
    2. Uploads the file to Supabase Storage
    3. Saves a local copy for processing
    4. Processes the PDF (extract text, chunk, create embeddings)
    5. Stores chunks and embeddings in Supabase PostgreSQL

    Args:
        file: PDF file to upload
        category: Document category (Đào tạo, Tuyển sinh, etc.)
        use_gemini: Whether to use Gemini Vision API for OCR (recommended for scanned PDFs)

    Returns:
        Processing result with chunk count and status
    """
    from config.settings import PDF_DIR

    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Chỉ chấp nhận file PDF. Vui lòng chọn file có đuôi .pdf",
            )

        # Check file size (max 50MB)
        file_content = await file.read()
        file_size = len(file_content)
        max_size = 50 * 1024 * 1024  # 50MB

        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File quá lớn. Kích thước tối đa là 50MB, file của bạn là {file_size / (1024*1024):.1f}MB",
            )

        if file_size == 0:
            raise HTTPException(status_code=400, detail="File rỗng")

        # Get original filename
        original_filename = Path(file.filename).name

        # Upload to Supabase Storage
        storage_service = get_supabase_storage_service()
        supabase_url = None
        safe_filename = storage_service.normalize_filename(original_filename)

        if storage_service.is_configured():
            log.info(f"📤 Uploading to Supabase Storage: {original_filename}")
            success, message, supabase_url = storage_service.upload_file(
                file_content=file_content,
                filename=original_filename,
                content_type="application/pdf",
            )
            if success:
                log.info(f"✅ Supabase upload successful: {supabase_url}")
            else:
                log.warning(
                    f"⚠️ Supabase upload failed: {message} - will save locally only"
                )
        else:
            log.warning("⚠️ Supabase Storage not configured - saving locally only")

        # Save a local copy for processing (using temp file or PDF_DIR)
        pdf_dir = Path(PDF_DIR)
        pdf_dir.mkdir(parents=True, exist_ok=True)

        file_path = pdf_dir / safe_filename

        # If file exists, add timestamp to filename
        if file_path.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name_without_ext = file_path.stem
            safe_filename = f"{name_without_ext}_{timestamp}.pdf"
            file_path = pdf_dir / safe_filename

        # Save file to disk for processing
        log.info(
            f"📤 Saving uploaded file locally: {safe_filename} ({file_size / 1024:.1f} KB)"
        )
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        log.info(f"✅ File saved to: {file_path}")

        # Process the PDF
        try:
            log.info(f"🔄 Starting PDF processing: {safe_filename}")

            # Initialize PDF processor with Gemini setting
            from src.services.pdf_processor import PDFProcessor

            pdf_processor = PDFProcessor(use_gemini=use_gemini)

            # Extract text and create chunks
            log.info(f"📖 Extracting text from {safe_filename}...")
            chunks = pdf_processor.process_pdf_with_headings(file_path)

            if not chunks:
                log.warning(f"⚠️ No chunks extracted from {safe_filename}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": f"File '{safe_filename}' đã được lưu nhưng không trích xuất được nội dung. File có thể là PDF scan hoặc rỗng.",
                        "filename": safe_filename,
                        "original_filename": original_filename,
                        "file_size": file_size,
                        "chunks_created": 0,
                        "supabase_url": supabase_url,
                        "status": "warning",
                    },
                )

            log.info(f"✂️ Created {len(chunks)} chunks from {safe_filename}")

            # Insert chunks into database (Supabase PostgreSQL)
            log.info(f"💾 Inserting {len(chunks)} chunks into Supabase database...")
            chunk_ids = rag.db_service.insert_chunks(chunks)

            # Generate embeddings
            log.info(f"🧠 Generating embeddings for {len(chunks)} chunks...")
            embeddings = rag.embedding_service.create_embeddings_batch(
                [chunk.content for chunk in chunks], batch_size=16, show_progress=False
            )

            # Insert embeddings into database (Supabase PostgreSQL)
            log.info("💾 Inserting embeddings into Supabase database...")
            rag.db_service.insert_embeddings(chunk_ids, embeddings)

            # Rebuild BM25 index for hybrid retrieval
            if hasattr(rag, "retrieval_service") and rag.retrieval_service:
                try:
                    log.info("🔨 Rebuilding BM25 index...")
                    rag.retrieval_service.rebuild_bm25_index()
                    log.info("✅ BM25 index rebuilt successfully")
                except Exception as e:
                    log.warning(f"⚠️ Could not rebuild BM25 index: {e}")

            log.info(
                f"🎉 Successfully processed {safe_filename}: {len(chunks)} chunks, {len(embeddings)} embeddings"
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"File '{original_filename}' đã được xử lý và lưu vào Supabase thành công!",
                    "filename": safe_filename,
                    "original_filename": original_filename,
                    "file_size": file_size,
                    "chunks_created": len(chunks),
                    "embeddings_created": len(embeddings),
                    "category": category,
                    "use_gemini": use_gemini,
                    "supabase_url": supabase_url,
                    "status": "success",
                },
            )

        except Exception as e:
            log.error(f"❌ Error processing PDF {safe_filename}: {e}")
            # File was saved but processing failed
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Lỗi khi xử lý file: {str(e)}",
                    "filename": safe_filename,
                    "original_filename": original_filename,
                    "file_size": file_size,
                    "supabase_url": supabase_url,
                    "status": "error",
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi upload file: {str(e)}")


@router.get("/admin/stats")
async def admin_get_stats(rag: RAGService = Depends(get_rag_service)):
    """
    Admin endpoint: Get dashboard statistics
    """
    try:
        # Get database stats
        db_stats = rag.db_service.get_database_stats()

        # Count documents
        from pathlib import Path
        from config.settings import PROCESSED_PDF_DIR

        pdf_dir = Path(PROCESSED_PDF_DIR)
        document_count = len(list(pdf_dir.glob("*.pdf"))) if pdf_dir.exists() else 0

        # Get conversation count
        conversation_count = len(rag.conversations)

        return {
            "conversations": {
                "total": conversation_count,
                "active": conversation_count,  # All in memory are considered active
                "change": "+12.5%",
            },
            "users": {
                "total": conversation_count * 2,  # Rough estimate
                "active": conversation_count,
                "change": "+8.2%",
            },
            "documents": {
                "total": document_count,
                "active": document_count,
                "change": "+3.1%",
            },
            "chunks": {
                "total": db_stats.get("total_chunks", 0),
                "with_embeddings": db_stats.get("chunks_with_embeddings", 0),
            },
            "response_time": {"average": "1.2s", "change": "-15.3%"},
        }

    except Exception as e:
        log.error(f"Error getting admin stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting statistics: {str(e)}"
        )


# ==================== Chat History Endpoints ====================


@router.get("/admin/chat-history")
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    search: str = None,
    status: str = None,
    rag: RAGService = Depends(get_rag_service),
):
    """
    Get all chat conversations with pagination and filtering

    Args:
        limit: Maximum number of results (default: 50)
        offset: Number of results to skip (default: 0)
        search: Optional search term
        status: Optional status filter ('active', 'completed', 'all')
    """
    try:
        conversations = rag.db_service.get_all_conversations(
            limit=limit, offset=offset, search_term=search, status_filter=status
        )

        # Get total count for pagination
        stats = rag.db_service.get_conversation_stats()

        return {
            "conversations": conversations,
            "total": stats.get("total_conversations", 0),
            "limit": limit,
            "offset": offset,
            "stats": {
                "total_conversations": stats.get("total_conversations", 0),
                "active_conversations": stats.get("active_conversations", 0),
                "today_conversations": stats.get("today_conversations", 0),
                "total_messages": stats.get("total_messages", 0),
            },
        }

    except Exception as e:
        log.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting chat history: {str(e)}"
        )


@router.get("/admin/chat-history/{conversation_id}")
async def get_conversation_detail(
    conversation_id: str, rag: RAGService = Depends(get_rag_service)
):
    """
    Get detailed conversation by ID

    Args:
        conversation_id: The conversation ID
    """
    try:
        conversation = rag.db_service.get_conversation_detail(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=404, detail=f"Conversation not found: {conversation_id}"
            )

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting conversation detail: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting conversation: {str(e)}"
        )


@router.delete("/admin/chat-history/{conversation_id}")
async def delete_conversation(
    conversation_id: str, rag: RAGService = Depends(get_rag_service)
):
    """
    Delete a conversation by ID

    Args:
        conversation_id: The conversation ID to delete
    """
    try:
        success = rag.db_service.delete_conversation(conversation_id)

        if not success:
            raise HTTPException(
                status_code=404, detail=f"Conversation not found: {conversation_id}"
            )

        return {
            "success": True,
            "message": f"Conversation {conversation_id} deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting conversation: {str(e)}"
        )


@router.get("/admin/chat-history/stats/overview")
async def get_chat_stats(rag: RAGService = Depends(get_rag_service)):
    """
    Get chat history statistics
    """
    try:
        stats = rag.db_service.get_conversation_stats()
        return stats

    except Exception as e:
        log.error(f"Error getting chat stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting statistics: {str(e)}"
        )


@router.get("/admin/chat-history/export")
async def export_chat_history(
    start_date: str = None,
    end_date: str = None,
    rag: RAGService = Depends(get_rag_service),
):
    """
    Export chat history as JSON

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    """
    try:
        conversations = rag.db_service.export_conversations(start_date, end_date)

        return {
            "export_date": datetime.datetime.now().isoformat(),
            "start_date": start_date,
            "end_date": end_date,
            "total_conversations": len(conversations),
            "conversations": conversations,
        }

    except Exception as e:
        log.error(f"Error exporting chat history: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error exporting chat history: {str(e)}"
        )


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    background_tasks: BackgroundTasks,
    feedback_svc: FeedbackService = Depends(get_feedback_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Submit user feedback for a response

    This endpoint allows users to rate responses with 👍 (positive),
    👎 (negative), or neutral feedback.
    """
    try:
        log.info(
            f"📝 Received feedback: {request.rating.value} for conversation {request.conversation_id}"
        )

        response = feedback_svc.submit_feedback(request)

        # Track user feedback in analytics (background)
        is_positive = request.rating.value == "positive"
        session_id = request.conversation_id or "unknown"
        background_tasks.add_task(
            analytics.update_user_feedback,
            session_id=session_id,
            is_positive=is_positive,
        )

        return response

    except Exception as e:
        log.error(f"❌ Error submitting feedback: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/feedback/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    days: int = 30,
    feedback_svc: FeedbackService = Depends(get_feedback_service),
):
    """
    Get feedback statistics for the specified period

    Args:
        days: Number of days to look back (default: 30)
    """
    try:
        stats = feedback_svc.get_feedback_stats(days=days)
        return stats

    except Exception as e:
        log.error(f"❌ Error getting feedback stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting feedback statistics: {str(e)}"
        )


@router.get("/feedback/dashboard", response_model=DashboardMetrics)
async def get_feedback_dashboard(
    feedback_svc: FeedbackService = Depends(get_feedback_service),
):
    """
    Get comprehensive dashboard metrics including:
    - Overall feedback statistics
    - Daily breakdown
    - Top/worst performing chunks
    - Recent negative feedback for review
    """
    try:
        dashboard = feedback_svc.get_dashboard_metrics()
        return dashboard

    except Exception as e:
        log.error(f"❌ Error getting dashboard metrics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting dashboard metrics: {str(e)}"
        )


@router.get("/feedback/daily")
async def get_daily_feedback_stats(
    days: int = 7,
    feedback_svc: FeedbackService = Depends(get_feedback_service),
):
    """
    Get daily feedback statistics

    Args:
        days: Number of days to look back (default: 7)
    """
    try:
        daily_stats = feedback_svc.get_daily_stats(days=days)
        return {"daily_stats": [stat.model_dump() for stat in daily_stats]}

    except Exception as e:
        log.error(f"❌ Error getting daily stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting daily statistics: {str(e)}"
        )


@router.get("/feedback/chunks/performance")
async def get_chunk_performance(
    top_n: int = 10,
    worst: bool = False,
    feedback_svc: FeedbackService = Depends(get_feedback_service),
):
    """
    Get top or worst performing chunks based on feedback

    Args:
        top_n: Number of chunks to return (default: 10)
        worst: If True, return worst performing chunks
    """
    try:
        chunks = feedback_svc.get_chunk_performance(top_n=top_n, worst=worst)
        return {
            "type": "worst" if worst else "top",
            "chunks": [chunk.model_dump() for chunk in chunks],
        }

    except Exception as e:
        log.error(f"❌ Error getting chunk performance: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting chunk performance: {str(e)}"
        )


@router.get("/feedback/negative/recent")
async def get_recent_negative_feedback(
    limit: int = 10,
    feedback_svc: FeedbackService = Depends(get_feedback_service),
):
    """
    Get recent negative feedback for review

    Args:
        limit: Maximum number of records to return (default: 10)
    """
    try:
        records = feedback_svc.get_recent_negative_feedback(limit=limit)
        return {
            "total": len(records),
            "records": [record.model_dump() for record in records],
        }

    except Exception as e:
        log.error(f"❌ Error getting negative feedback: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting negative feedback: {str(e)}"
        )


@router.get("/feedback/export")
async def export_feedback_report(
    days: int = 30,
    feedback_svc: FeedbackService = Depends(get_feedback_service),
):
    """
    Export comprehensive feedback report

    Args:
        days: Number of days to include in report (default: 30)
    """
    try:
        report = feedback_svc.export_feedback_report(days=days)
        return report

    except Exception as e:
        log.error(f"❌ Error exporting feedback report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error exporting feedback report: {str(e)}"
        )


@router.get("/feedback/retrieval-weights")
async def get_retrieval_weights(
    feedback_svc: FeedbackService = Depends(get_feedback_service),
):
    """
    Get current retrieval weights based on feedback

    These weights can be used to adjust search ranking based on historical feedback.
    """
    try:
        weights = feedback_svc.get_retrieval_weights()
        return {"total_chunks_with_weights": len(weights), "weights": weights}

    except Exception as e:
        log.error(f"❌ Error getting retrieval weights: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting retrieval weights: {str(e)}"
        )


@router.get("/feedback/training-data")
async def get_training_data(
    min_samples: int = 100,
    feedback_svc: FeedbackService = Depends(get_feedback_service),
):
    """
    Get feedback data for potential model fine-tuning

    Args:
        min_samples: Minimum number of samples required (default: 100)
    """
    try:
        samples = feedback_svc.get_feedback_for_training(min_samples=min_samples)
        return {
            "total_samples": len(samples),
            "min_samples_required": min_samples,
            "ready_for_training": len(samples) >= min_samples,
            "samples": samples[:50],  # Return first 50 as preview
        }

    except Exception as e:
        log.error(f"❌ Error getting training data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting training data: {str(e)}"
        )


# ============================================================================
# ANALYTICS ENDPOINTS - Dashboard Insights
# ============================================================================


@router.get("/analytics/overview", response_model=DashboardOverview)
async def get_analytics_overview(
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get dashboard overview with key metrics

    Returns quick stats for total conversations, messages, documents, users,
    along with percentage changes and today's activity.
    """
    try:
        overview = analytics_svc.get_dashboard_overview()
        return overview

    except Exception as e:
        log.error(f"❌ Error getting analytics overview: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting analytics overview: {str(e)}"
        )


@router.get("/analytics/system", response_model=SystemInsights)
async def get_system_insights(
    time_range: TimeRange = Query(
        TimeRange.LAST_7_DAYS, description="Time range filter"
    ),
    start_date: Optional[str] = Query(
        None, description="Start date for custom range (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date for custom range (YYYY-MM-DD)"
    ),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get system insights including:
    - Token usage (daily/hourly)
    - Estimated cost consumption
    - System access metrics (daily/hourly)
    - Blocked access count
    """
    try:
        insights = analytics_svc.get_system_insights(
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
        )
        return insights

    except Exception as e:
        log.error(f"❌ Error getting system insights: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting system insights: {str(e)}"
        )


@router.get("/analytics/users", response_model=UserInsights)
async def get_user_insights(
    time_range: TimeRange = Query(
        TimeRange.LAST_7_DAYS, description="Time range filter"
    ),
    start_date: Optional[str] = Query(
        None, description="Start date for custom range (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date for custom range (YYYY-MM-DD)"
    ),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get user insights including:
    - Daily unique users
    - Return frequency
    - User segmentation by question count
    - New vs Retain users
    - Topics of interest
    - Popular questions
    - User funnel
    """
    try:
        insights = analytics_svc.get_user_insights(
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
        )
        return insights

    except Exception as e:
        log.error(f"❌ Error getting user insights: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting user insights: {str(e)}"
        )


@router.get("/analytics/chat", response_model=ChatInsights)
async def get_chat_insights(
    time_range: TimeRange = Query(
        TimeRange.LAST_7_DAYS, description="Time range filter"
    ),
    start_date: Optional[str] = Query(
        None, description="Start date for custom range (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date for custom range (YYYY-MM-DD)"
    ),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get chat insights including:
    - Total user messages and AI responses
    - Like/dislike rates
    - Average messages per conversation
    - Average conversation duration
    - Top unanswered questions
    - Low-rated responses for improvement
    """
    try:
        insights = analytics_svc.get_chat_insights(
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
        )
        return insights

    except Exception as e:
        log.error(f"❌ Error getting chat insights: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting chat insights: {str(e)}"
        )


@router.get("/analytics/documents", response_model=DocumentInsights)
async def get_document_insights(
    time_range: TimeRange = Query(
        TimeRange.LAST_7_DAYS, description="Time range filter"
    ),
    start_date: Optional[str] = Query(
        None, description="Start date for custom range (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date for custom range (YYYY-MM-DD)"
    ),
    category: Optional[str] = Query(None, description="Filter by category"),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get document insights including:
    - Total documents and size
    - Active/inactive document counts
    - Statistics by category
    - Top retrieved documents
    - Document growth trend
    """
    try:
        insights = analytics_svc.get_document_insights(
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
            category=category,
        )
        return insights

    except Exception as e:
        log.error(f"❌ Error getting document insights: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting document insights: {str(e)}"
        )


@router.get("/analytics/business", response_model=BusinessInsights)
async def get_business_insights(
    time_range: TimeRange = Query(
        TimeRange.LAST_7_DAYS, description="Time range filter"
    ),
    start_date: Optional[str] = Query(
        None, description="Start date for custom range (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date for custom range (YYYY-MM-DD)"
    ),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get business insights including:
    - Estimated hours saved
    - Content gap analysis
    - Quality score breakdown
    """
    try:
        insights = analytics_svc.get_business_insights(
            time_range=time_range,
            start_date=start_date,
            end_date=end_date,
        )
        return insights

    except Exception as e:
        log.error(f"❌ Error getting business insights: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting business insights: {str(e)}"
        )


@router.get("/analytics/popular-questions")
async def get_popular_questions(
    time_range: TimeRange = Query(
        TimeRange.LAST_7_DAYS, description="Time range filter"
    ),
    limit: int = Query(10, ge=1, le=20, description="Number of questions to return"),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get popular questions from real conversation data

    This endpoint analyzes actual conversation data to find
    the most frequently asked questions.

    - **time_range**: Time period to analyze (L7D, MTD, YTD)
    - **limit**: Number of questions to return (1-20, default: 10)

    Returns a list of popular questions with:
    - question: The question text
    - count: How many times it was asked
    - last_asked: When it was last asked
    """
    try:
        questions = analytics_svc.get_real_popular_questions(
            time_range=time_range, limit=limit
        )

        return {
            "popular_questions": questions,
            "total_count": len(questions),
            "time_range": time_range.value,
            "data_source": "real" if questions else "sample",
        }

    except Exception as e:
        log.error(f"❌ Error getting popular questions: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting popular questions: {str(e)}"
        )


@router.get("/analytics/suggested-questions")
async def get_suggested_questions(
    limit: int = Query(5, ge=1, le=10, description="Number of questions to return"),
    force_refresh: bool = Query(False, description="Force refresh cache"),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get suggested questions based on trending topics

    This endpoint analyzes trending topics from the last 24 hours
    and returns popular questions from those topics.

    Results are cached for 1 hour to improve performance.

    - **limit**: Number of questions to return (1-10, default: 5)
    - **force_refresh**: Force refresh the cache (default: false)

    Returns a list of suggested questions with:
    - question: The question text
    - count: How many times it was asked
    - last_asked: When it was last asked
    """
    try:
        current_time = time.time()
        cache = _suggested_questions_cache

        # Check if cache is valid
        cache_valid = (
            not force_refresh
            and cache["questions"] is not None
            and cache["timestamp"] is not None
            and (current_time - cache["timestamp"]) < cache["ttl"]
        )

        if cache_valid:
            # Return cached results
            log.info("📦 Returning cached suggested questions")
            cached_questions = cache["questions"]
            # Limit the cached results if needed
            limited_questions = cached_questions[:limit]
            return {
                "success": True,
                "questions": limited_questions,
                "count": len(limited_questions),
                "cached": True,
                "cache_age_seconds": int(current_time - cache["timestamp"]),
            }

        # Fetch fresh data
        log.info("🔄 Fetching fresh suggested questions (cache miss or expired)")
        questions = analytics_svc.get_suggested_questions(
            limit=10
        )  # Fetch more for caching
        questions_data = [q.model_dump() for q in questions]

        # Update cache
        cache["questions"] = questions_data
        cache["timestamp"] = current_time

        # Return limited results
        limited_questions = questions_data[:limit]
        return {
            "success": True,
            "questions": limited_questions,
            "count": len(limited_questions),
            "cached": False,
            "cache_age_seconds": 0,
        }

    except Exception as e:
        log.error(f"❌ Error getting suggested questions: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting suggested questions: {str(e)}"
        )


# ==================== ATTACHMENT ENDPOINTS ====================


@router.post("/attachments/upload", response_model=DocumentAttachment)
async def upload_attachment(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),
    chunk_ids: Optional[str] = Form(None),
    attachment_svc: AttachmentService = Depends(get_attachment_service),
):
    """
    Upload a new attachment (form, template, etc.)

    - **file**: File to upload (doc, docx, xlsx, xls, pdf)
    - **description**: Description of the file
    - **keywords**: Comma-separated keywords for searching
    - **chunk_ids**: Comma-separated chunk IDs to link this attachment to
    """
    try:
        # Validate file type
        allowed_extensions = [".doc", ".docx", ".xlsx", ".xls", ".pdf"]
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}",
            )

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

        # Save file
        file_path = Path("data/forms") / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file_content)

        # Parse keywords
        keywords_list = []
        if keywords:
            keywords_list = [k.strip() for k in keywords.split(",") if k.strip()]

        # Create attachment record
        attachment_id = attachment_svc.create_attachment(
            file_name=file.filename,
            file_type=file_ext[1:],  # Remove the dot
            file_path=str(file_path),
            file_size=len(file_content),
            description=description,
            keywords=keywords_list,
        )

        # Link to chunks if provided
        if chunk_ids:
            chunk_id_list = [
                int(cid.strip()) for cid in chunk_ids.split(",") if cid.strip()
            ]
            if chunk_id_list:
                attachment_svc.link_attachment_to_chunks(attachment_id, chunk_id_list)

        # Get the created attachment
        attachment = attachment_svc.get_attachment_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=500, detail="Failed to retrieve attachment")

        log.info(f"✅ Uploaded attachment: {file.filename} (ID: {attachment_id})")
        return attachment

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Error uploading attachment: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/attachments/download/{attachment_id}")
async def download_attachment(
    attachment_id: int,
    attachment_svc: AttachmentService = Depends(get_attachment_service),
):
    """
    Download an attachment by ID

    - **attachment_id**: ID of the attachment to download
    """
    try:
        attachment = attachment_svc.get_attachment_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")

        file_path = Path(attachment.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")

        return FileResponse(
            path=str(file_path),
            filename=attachment.file_name,
            media_type="application/octet-stream",
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Error downloading attachment: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/attachments", response_model=List[DocumentAttachment])
async def list_attachments(
    keywords: Optional[str] = Query(None, description="Comma-separated keywords"),
    file_name: Optional[str] = Query(None, description="File name to search"),
    attachment_svc: AttachmentService = Depends(get_attachment_service),
):
    """
    List all attachments or search by keywords/file name

    - **keywords**: Comma-separated keywords to search
    - **file_name**: File name to search (partial match)
    """
    try:
        if keywords or file_name:
            keywords_list = (
                [k.strip() for k in keywords.split(",") if k.strip()]
                if keywords
                else None
            )
            attachments = attachment_svc.search_attachments(
                keywords=keywords_list, file_name=file_name
            )
        else:
            attachments = attachment_svc.get_all_attachments()

        return attachments

    except Exception as e:
        log.error(f"❌ Error listing attachments: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list attachments: {str(e)}"
        )


@router.delete("/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    attachment_svc: AttachmentService = Depends(get_attachment_service),
):
    """
    Delete an attachment (soft delete)

    - **attachment_id**: ID of the attachment to delete
    """
    try:
        success = attachment_svc.delete_attachment(attachment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Attachment not found")

        return {"success": True, "message": "Attachment deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Error deleting attachment: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/attachments/{attachment_id}/link-chunks")
async def link_attachment_to_chunks(
    attachment_id: int,
    chunk_ids: List[int],
    relevance_score: float = 1.0,
    attachment_svc: AttachmentService = Depends(get_attachment_service),
):
    """
    Link an attachment to multiple chunks

    - **attachment_id**: ID of the attachment
    - **chunk_ids**: List of chunk IDs to link
    - **relevance_score**: Relevance score (0-1)
    """
    try:
        # Verify attachment exists
        attachment = attachment_svc.get_attachment_by_id(attachment_id)
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")

        attachment_svc.link_attachment_to_chunks(
            attachment_id, chunk_ids, relevance_score
        )

        return {
            "success": True,
            "message": f"Linked attachment to {len(chunk_ids)} chunks",
            "attachment_id": attachment_id,
            "chunk_ids": chunk_ids,
        }

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Error linking attachment to chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Link failed: {str(e)}")
