"""
RAG (Retrieval-Augmented Generation) service
"""

import uuid
import re
import time
import hashlib
import unicodedata
from typing import List, Dict, Any, Optional
from src.services.embedding_service import EmbeddingService
from src.services.postgres_database_service import PostgresDatabaseService
from src.services.hybrid_retrieval_service import HybridRetrievalService
from src.services.ingestion_service import IngestionService
from src.services.pdf_processor import PDFProcessor
from src.services import gemini_service
from src.services.gemini_service import normalize_question
from src.services.memory_service import ConversationMemoryService
from src.services.attachment_service import AttachmentService
from sentence_transformers import CrossEncoder
from src.utils.logger import log
from src.utils.admission_document_priority import compute_priority_adjustment

from config.settings import (
    TOP_K_RESULTS,
    LLM_PROVIDER,
    ENABLE_GEMINI_NORMALIZATION,
    ADMISSION_ONLY_MODE,
    RETRIEVAL_INITIAL_K_MULTIPLIER,
    RETRIEVAL_INITIAL_K_CAP,
    RERANK_MAX_CANDIDATES,
    ENABLE_CONTEXT_EXPANSION,
    CONTEXT_EXPANSION_MAX_NEIGHBORS,
    CONTEXT_EXPANSION_SKIP_TOP_SCORE,
    CONTEXT_EXPANSION_SKIP_SECONDARY_SCORE,
)


class RAGService:
    """Service for Retrieval-Augmented Generation"""

    def __init__(self, analytics_service=None):
        """Initialize RAG service with PostgreSQL + Hybrid Retrieval"""
        self.embedding_service = EmbeddingService()
        self.db_service = PostgresDatabaseService()
        self.retrieval_service = HybridRetrievalService(
            self.db_service, self.embedding_service
        )
        self.pdf_processor = PDFProcessor()

        # Import analytics service lazily to avoid circular imports
        if analytics_service is None:
            try:
                from src.services.analytics_service import AnalyticsService

                analytics_service = AnalyticsService(self.db_service)
            except Exception as e:
                log.warning(f"Could not initialize analytics service: {e}")
                analytics_service = None

        self.analytics_service = analytics_service

        self.ingestion_service = IngestionService(
            self.db_service,
            self.embedding_service,
            self.pdf_processor,
            self.retrieval_service,
            analytics_service,  # Pass analytics service for document tracking
        )
        # Initialize Memory Service for persistent conversational memory
        self.memory_service = ConversationMemoryService(
            self.db_service, self.embedding_service
        )

        # Initialize Attachment Service
        self.attachment_service = AttachmentService(self.db_service)

        # Conversation memory (in-memory cache, backed by persistent storage)
        self.conversations = {}

        # Initialize Reranker
        try:
            log.info("Initializing Reranker model...")
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            log.info("Reranker model initialized successfully.")
        except Exception as e:
            log.error(f"Error initializing Reranker model: {e}")
            self.reranker = None

        # Ingestion service is available but watchdog is disabled
        # PDF processing now happens via background tasks in routes.py
        log.info(
            "Ingestion service initialized (watchdog disabled - using background tasks)"
        )

        # Reranking cache for common queries (LRU with max 500 entries)
        self._rerank_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._rerank_cache_max_size = 500

    def _rerank_chunks(
        self, query: str, chunks: List[Dict[str, Any]], max_rerank: int = 6
    ) -> List[Dict[str, Any]]:
        """Smart reranking: skip when top results are already confident."""
        if not self.reranker or not chunks:
            return chunks

        try:
            # Cache check
            chunk_ids = "_".join([str(c.get("chunk_id", ""))[:8] for c in chunks[:10]])
            cache_key = hashlib.md5(f"{query}_{chunk_ids}".encode()).hexdigest()
            if cache_key in self._rerank_cache:
                log.info("⚡ Reranking cache hit")
                return self._rerank_cache[cache_key]

            # Smart skip: if top 3 results are confident, skip reranking entirely (saves 9-12s)
            SMART_SKIP_THRESHOLD = 0.6
            top_scores = [
                c.get("dense_score", 0) or c.get("score", 0) for c in chunks[:3]
            ]
            if len(top_scores) >= 3 and all(
                s >= SMART_SKIP_THRESHOLD for s in top_scores
            ):
                log.info(
                    f"⚡ Smart skip reranking: top 3 scores {[f'{s:.2f}' for s in top_scores]} >= {SMART_SKIP_THRESHOLD}"
                )
                for chunk in chunks:
                    chunk["rerank_score"] = chunk.get("dense_score", 0) or chunk.get(
                        "score", 0
                    )
                chunks.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
                self._rerank_cache[cache_key] = chunks
                return chunks

            # Separate high-score chunks (skip individual reranking)
            high_score_chunks = []
            low_score_chunks = []
            for chunk in chunks:
                dense_score = chunk.get("dense_score", 0) or chunk.get("score", 0)
                if dense_score >= 0.85:
                    chunk["rerank_score"] = dense_score
                    high_score_chunks.append(chunk)
                else:
                    low_score_chunks.append(chunk)

            log.info(
                f"⚡ Skip reranking for {len(high_score_chunks)} high-score chunks (>0.85)"
            )

            # Limit and rerank remaining chunks
            chunks_to_rerank = low_score_chunks[:max_rerank]
            if chunks_to_rerank:
                pairs = [[query, chunk["content"]] for chunk in chunks_to_rerank]
                scores = self.reranker.predict(pairs, show_progress_bar=False)
                for chunk, score in zip(chunks_to_rerank, scores):
                    chunk["rerank_score"] = float(score)
                log.info(
                    f"Reranked {len(chunks_to_rerank)} chunks (skipped {len(chunks) - len(chunks_to_rerank) - len(high_score_chunks)})"
                )

            all_chunks = high_score_chunks + chunks_to_rerank
            all_chunks.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)

            # Cache
            if len(self._rerank_cache) >= self._rerank_cache_max_size:
                oldest_key = next(iter(self._rerank_cache))
                del self._rerank_cache[oldest_key]
            self._rerank_cache[cache_key] = all_chunks
            return all_chunks

        except Exception as e:
            log.error(f"Error during chunk reranking: {e}")
            return chunks

    def _detect_chart_request(self, query: str, answer: str) -> List[Dict[str, Any]]:
        """
        Detect if the query/answer contains statistical data that can be visualized as charts.
        Returns chart data if applicable.
        Only generates charts when user EXPLICITLY asks for statistics or charts.
        """
        chart_data = []
        query_lower = query.lower()

        # Keywords that EXPLICITLY suggest chart visualization request
        # Removed common keywords that appear in most questions
        explicit_chart_keywords = [
            "thống kê",
            "biểu đồ",
            "so sánh số liệu",
            "vẽ biểu đồ",
            "hiển thị biểu đồ",
            "chart",
            "graph",
            "statistics",
            "visualize",
            "visualization",
        ]

        # Check if query EXPLICITLY asks for statistics/charts
        should_generate_chart = any(
            keyword in query_lower for keyword in explicit_chart_keywords
        )

        if should_generate_chart:
            # Example: Admission statistics by year
            if any(word in query_lower for word in ["tuyển sinh", "chỉ tiêu"]):
                chart_data.append(
                    {
                        "type": "bar",
                        "title": "Chỉ tiêu tuyển sinh qua các năm",
                        "data": [
                            {"name": "2021", "Chỉ tiêu": 450, "Trúng tuyển": 420},
                            {"name": "2022", "Chỉ tiêu": 500, "Trúng tuyển": 480},
                            {"name": "2023", "Chỉ tiêu": 550, "Trúng tuyển": 530},
                            {"name": "2024", "Chỉ tiêu": 600, "Trúng tuyển": 580},
                            {"name": "2025", "Chỉ tiêu": 650, "Trúng tuyển": 0},
                        ],
                        "xKey": "name",
                        "yKeys": ["Chỉ tiêu", "Trúng tuyển"],
                        "description": "Biểu đồ thống kê chỉ tiêu tuyển sinh (Dữ liệu minh họa)",
                    }
                )

            # Example: Score distribution by major
            if any(
                word in query_lower
                for word in ["điểm chuẩn", "điểm trúng tuyển", "ngành"]
            ):
                chart_data.append(
                    {
                        "type": "bar",
                        "title": "Điểm chuẩn các ngành năm 2024",
                        "data": [
                            {"name": "An ninh chính trị", "Điểm chuẩn": 24.5},
                            {"name": "An ninh kinh tế", "Điểm chuẩn": 25.0},
                            {"name": "An ninh mạng", "Điểm chuẩn": 26.5},
                            {"name": "Điều tra hình sự", "Điểm chuẩn": 25.5},
                            {"name": "Kỹ thuật hình sự", "Điểm chuẩn": 24.0},
                        ],
                        "xKey": "name",
                        "yKeys": ["Điểm chuẩn"],
                        "description": "Biểu đồ điểm chuẩn các ngành (Dữ liệu minh họa)",
                    }
                )

            # Example: Student distribution by major (pie chart)
            if any(word in query_lower for word in ["tỷ lệ", "phân bố", "cơ cấu"]):
                chart_data.append(
                    {
                        "type": "pie",
                        "title": "Tỷ lệ học viên theo ngành đào tạo",
                        "data": [
                            {"name": "An ninh chính trị", "value": 25},
                            {"name": "An ninh kinh tế", "value": 20},
                            {"name": "An ninh mạng", "value": 30},
                            {"name": "Điều tra hình sự", "value": 15},
                            {"name": "Kỹ thuật hình sự", "value": 10},
                        ],
                        "xKey": "name",
                        "yKeys": ["value"],
                        "description": "Biểu đồ tỷ lệ học viên theo ngành (Dữ liệu minh họa)",
                    }
                )

            # Example: Trend over time (line chart)
            if any(
                word in query_lower
                for word in ["xu hướng", "trend", "biến động", "qua các năm"]
            ):
                chart_data.append(
                    {
                        "type": "line",
                        "title": "Xu hướng số lượng hồ sơ đăng ký qua các năm",
                        "data": [
                            {"name": "2020", "Hồ sơ": 1200},
                            {"name": "2021", "Hồ sơ": 1450},
                            {"name": "2022", "Hồ sơ": 1680},
                            {"name": "2023", "Hồ sơ": 1920},
                            {"name": "2024", "Hồ sơ": 2150},
                        ],
                        "xKey": "name",
                        "yKeys": ["Hồ sơ"],
                        "description": "Biểu đồ xu hướng số lượng hồ sơ (Dữ liệu minh họa)",
                    }
                )

        return chart_data

    def _should_expand_context(self, chunks: List[Dict[str, Any]], query: str) -> bool:
        """Decide whether context expansion is worth the extra DB lookups."""
        if not ENABLE_CONTEXT_EXPANSION or len(chunks) <= 1:
            return False

        query_lower = (query or "").lower().strip()
        detail_keywords = (
            "chi tiết",
            "cụ thể",
            "giải thích",
            "so sánh",
            "khác nhau",
            "bao gồm",
            "toàn bộ",
            "đầy đủ",
            "quy định",
            "thủ tục",
            "hồ sơ",
            "documents",
            "details",
            "compare",
            "procedure",
        )
        if any(keyword in query_lower for keyword in detail_keywords):
            return True

        query_token_count = len(query_lower.split())
        primary_scores = [
            chunk.get("rerank_score")
            or chunk.get("combined_score")
            or chunk.get("dense_score")
            or chunk.get("score", 0.0)
            for chunk in chunks[:2]
        ]

        if (
            query_token_count <= 8
            and len(primary_scores) >= 2
            and primary_scores[0] >= CONTEXT_EXPANSION_SKIP_TOP_SCORE
            and primary_scores[1] >= CONTEXT_EXPANSION_SKIP_SECONDARY_SCORE
        ):
            log.info(
                "⚡ Skip context expansion: short direct query already has strong top hits"
            )
            return False

        return True

    def retrieve_relevant_chunks(
        self, query: str, top_k: int = TOP_K_RESULTS
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks using hybrid retrieval (dense + sparse search)."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.create_embedding(query)

            initial_k = min(
                top_k * max(RETRIEVAL_INITIAL_K_MULTIPLIER, 1),
                max(RETRIEVAL_INITIAL_K_CAP, top_k),
            )
            hybrid_results = self.retrieval_service.hybrid_search(
                query=query, query_embedding=query_embedding, top_k=initial_k
            )

            if not hybrid_results:
                log.warning(f"No chunks found for query: {query}")
                return []

            log.info(f"Hybrid search found {len(hybrid_results)} chunks.")

            # Optimized rerank: only cross-encode the top-6 low-confidence candidates
            # (high-score chunks are bypassed inside _rerank_chunks automatically)
            reranked_chunks = self._rerank_chunks(
                query, hybrid_results, max_rerank=RERANK_MAX_CANDIDATES
            )

            # Context expansion
            if self._should_expand_context(reranked_chunks[:top_k], query):
                expanded_chunks = self._expand_context(reranked_chunks[:top_k], query)
            else:
                expanded_chunks = reranked_chunks[:top_k]

            # Final ranking
            final_chunks = self._final_ranking(expanded_chunks, query)
            return final_chunks[:top_k]

        except Exception as e:
            log.error(f"Error during retrieve_relevant_chunks: {e}")
            return []

    def _extract_heading_from_content(self, content: str) -> Optional[str]:
        """
        Extract heading from chunk content

        Args:
            content: Chunk content

        Returns:
            Heading if found, None otherwise
        """
        # Try to extract heading from first line
        lines = content.strip().split("\n")
        if not lines:
            return None

        first_line = lines[0].strip()

        # Check if first line matches heading pattern
        heading_patterns = [
            r"^\s*(\d+)\.\s+(.+)$",
            r"^\s*(\d+\.\d+)\.\s+(.+)$",
            r"^\s*(\d+\.\d+\.\d+)\.\s+(.+)$",
        ]

        for pattern in heading_patterns:
            match = re.match(pattern, first_line)
            if match:
                return first_line

        return None

    def _expand_context(
        self, chunks: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Expand context by adding related chunks from the same document/section

        Args:
            chunks: Initial retrieved chunks
            query: User query for relevance checking

        Returns:
            Expanded list of chunks with additional context
        """
        if not chunks:
            return chunks

        expanded_chunks = chunks.copy()
        expanded_ids = {
            chunk.get("id", chunk.get("chunk_id"))
            for chunk in expanded_chunks
            if chunk.get("id", chunk.get("chunk_id")) is not None
        }

        try:
            # Group chunks by source file
            chunks_by_source = {}
            for chunk in chunks:
                source = chunk.get("source_file", "")
                if source not in chunks_by_source:
                    chunks_by_source[source] = []
                chunks_by_source[source].append(chunk)

            # For each source file, try to find adjacent chunks
            for source_file, source_chunks in chunks_by_source.items():
                for chunk in source_chunks:
                    chunk_index = chunk.get("chunk_index", -1)
                    page_number = chunk.get("page_number", -1)

                    if chunk_index >= 0:
                        added_neighbors = 0
                        # Look for adjacent chunks (before and after)
                        for offset in (-1, 1):
                            if added_neighbors >= max(
                                CONTEXT_EXPANSION_MAX_NEIGHBORS, 0
                            ):
                                break
                            adjacent_chunk = self._get_adjacent_chunk(
                                source_file, chunk_index + offset, page_number
                            )
                            adjacent_id = (
                                adjacent_chunk.get("id") if adjacent_chunk else None
                            )
                            if adjacent_chunk and adjacent_id not in expanded_ids:
                                # Check if adjacent chunk is somewhat relevant
                                if self._is_chunk_relevant(adjacent_chunk, query):
                                    adjacent_chunk["context_expansion"] = True
                                    adjacent_chunk["hybrid_score"] = (
                                        chunk.get("hybrid_score", 0.0) * 0.7
                                    )  # Lower score for context
                                    expanded_chunks.append(adjacent_chunk)
                                    if adjacent_id is not None:
                                        expanded_ids.add(adjacent_id)
                                    added_neighbors += 1

            log.info(
                f"Context expansion added {len(expanded_chunks) - len(chunks)} additional chunks"
            )
            return expanded_chunks

        except Exception as e:
            log.error(f"Error during context expansion: {e}")
            return chunks

    def _get_adjacent_chunk(
        self, source_file: str, chunk_index: int, page_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get adjacent chunk by source file and chunk index using PostgreSQL"""
        try:
            chunk = self.db_service.get_chunk_by_source_and_index(
                source_file, chunk_index
            )
            return chunk
        except Exception as e:
            log.error(f"Error getting adjacent chunk: {e}")
            return None

    def _is_chunk_relevant(self, chunk: Dict[str, Any], query: str) -> bool:
        """Check if a chunk is relevant to the query using simple keyword matching"""
        try:
            content = chunk.get("content", "").lower()
            query_lower = query.lower()

            # Simple keyword overlap check
            query_words = set(query_lower.split())
            content_words = set(content.split())

            # Calculate overlap ratio
            overlap = len(query_words.intersection(content_words))
            overlap_ratio = overlap / len(query_words) if query_words else 0

            # Consider relevant if there's at least 20% keyword overlap
            return overlap_ratio >= 0.2

        except Exception as e:
            log.error(f"Error checking chunk relevance: {e}")
            return False

    def _final_ranking(
        self, chunks: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Final ranking of chunks considering multiple factors

        Args:
            chunks: List of chunks to rank
            query: User query

        Returns:
            Ranked list of chunks
        """
        try:
            # Sort by multiple criteria
            def ranking_score(chunk):
                # Primary: rerank_score if available, otherwise hybrid_score
                primary_score = chunk.get(
                    "rerank_score", chunk.get("hybrid_score", 0.0)
                )

                # Prefer current-cycle official admission documents when relevant.
                priority_adjustment = compute_priority_adjustment(query, chunk)

                # Bonus for chunks with headings (likely more structured content)
                heading_bonus = 0.1 if chunk.get("heading_text") else 0.0

                # Bonus for chunks that are not context expansions (original results)
                original_bonus = (
                    0.05 if not chunk.get("context_expansion", False) else 0.0
                )

                # Penalty for very short chunks (likely less informative)
                content_length = len(chunk.get("content", ""))
                length_penalty = -0.1 if content_length < 100 else 0.0

                return (
                    primary_score
                    + priority_adjustment
                    + heading_bonus
                    + original_bonus
                    + length_penalty
                )

            ranked_chunks = sorted(chunks, key=ranking_score, reverse=True)

            log.info(f"Final ranking completed for {len(ranked_chunks)} chunks")
            return ranked_chunks

        except Exception as e:
            log.error(f"Error during final ranking: {e}")
            return chunks

    def _generate_vision_answer(
        self,
        query: str,
        images: List[Any],
        conversation_id: Optional[str] = None,
        language: str = "vi",  # Add language parameter
    ) -> Dict[str, Any]:
        """
        Generate answer for image-based queries using Gemini Vision.

        Args:
            query: User's question about the image(s)
            images: List of ImageInput objects with base64 encoded images
            conversation_id: Optional conversation ID
            language: Response language - 'vi' for Vietnamese (default) or 'en' for English

        Returns:
            Dictionary with answer, confidence, and conversation_id
        """
        try:
            log.info(
                f"Processing vision query with {len(images)} images, language={language}"
            )

            # Create conversation ID if needed
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            # Build the vision prompt based on language
            if language == "en":
                vision_prompt = f"""You are an AI assistant specializing in supporting information about People's Security University (PSU).
Please analyze the provided image(s) and answer the user's question in ENGLISH.

User's question: {query if query else "Please describe the content of this image."}

Instructions:
- Analyze the image content carefully
- Respond ENTIRELY in ENGLISH
- If the image contains documents or text (which may be in Vietnamese), translate and explain the content in English
- If it's a data table, summarize the important information in English
- Provide a detailed, easy-to-understand answer in English"""
            else:
                vision_prompt = f"""Bạn là một trợ lý AI chuyên hỗ trợ về Trường Đại học An ninh Nhân dân.
Hãy phân tích hình ảnh được cung cấp và trả lời câu hỏi của người dùng.

Câu hỏi của người dùng: {query if query else "Hãy mô tả nội dung trong hình ảnh này."}

Hướng dẫn:
- Phân tích kỹ nội dung trong hình ảnh
- Trả lời bằng tiếng Việt
- Nếu hình ảnh liên quan đến tài liệu, văn bản, hãy trích dẫn và giải thích nội dung
- Nếu là bảng số liệu, hãy tóm tắt thông tin quan trọng
- Đưa ra câu trả lời chi tiết, dễ hiểu"""

            # Prepare image data for Gemini
            image_parts = []
            for img in images:
                try:
                    # Get base64 data (remove data:image/xxx;base64, prefix if present)
                    base64_data = img.base64
                    if "," in base64_data:
                        base64_data = base64_data.split(",")[1]

                    # Determine mime type
                    mime_type = getattr(img, "mime_type", "image/jpeg")
                    if not mime_type:
                        mime_type = "image/jpeg"

                    image_parts.append({"mime_type": mime_type, "data": base64_data})
                    log.info(
                        f"Processed image: {getattr(img, 'name', 'unknown')} ({mime_type})"
                    )
                except Exception as img_error:
                    log.error(f"Error processing image: {img_error}")
                    continue

            if not image_parts:
                error_msg = (
                    "Sorry, unable to process the image. Please try again with a different format (PNG, JPG, WebP)."
                    if language == "en"
                    else "Xin lỗi, không thể xử lý hình ảnh. Vui lòng thử lại với định dạng ảnh khác (PNG, JPG, WebP)."
                )
                return {
                    "answer": error_msg,
                    "sources": [],
                    "source_references": [],
                    "confidence": 0.0,
                    "conversation_id": conversation_id,
                }

            # Call Gemini Vision
            answer = gemini_service.generate_vision_response(
                prompt=vision_prompt, images=image_parts
            )

            if not answer:
                answer = (
                    "Sorry, I couldn't analyze this image. Please try again or describe more about what you want to ask."
                    if language == "en"
                    else "Xin lỗi, tôi không thể phân tích hình ảnh này. Vui lòng thử lại hoặc mô tả thêm về nội dung bạn muốn hỏi."
                )
            else:
                # Add engagement prompt
                answer = self._add_engagement_prompt(answer, query, language)

            log.info("Vision response generated successfully")

            # Upload images to Supabase Storage and save conversation
            image_urls = []
            if images:
                try:
                    from src.utils.chat_image_storage import upload_chat_images

                    # Convert ImageInput objects to base64 strings
                    base64_images = []
                    for img in images:
                        try:
                            # Get the full base64 data with prefix
                            base64_data = getattr(img, "base64", None)
                            mime_type = getattr(img, "mime_type", "image/png")
                            if base64_data:
                                # Ensure proper data URI format
                                if not base64_data.startswith("data:"):
                                    base64_data = (
                                        f"data:{mime_type};base64,{base64_data}"
                                    )
                                base64_images.append(base64_data)
                        except Exception as conv_err:
                            log.warning(f"Could not convert image: {conv_err}")

                    if base64_images:
                        image_urls = upload_chat_images(base64_images, conversation_id)
                        log.info(
                            f"📸 Uploaded {len(image_urls)} images to Supabase Storage"
                        )
                except Exception as img_error:
                    log.warning(f"Could not upload images: {img_error}")

            # Save conversation to PostgreSQL
            try:
                self.db_service.save_conversation(
                    conversation_id=conversation_id,
                    user_message=query,
                    assistant_response=answer,
                    sources=[],
                    confidence=0.85,
                    processing_time=0.0,
                    images=image_urls if image_urls else None,
                )
                log.info(f"💾 Saved vision conversation with {len(image_urls)} images")
            except Exception as save_error:
                log.warning(f"Could not save vision conversation to DB: {save_error}")

            return {
                "answer": answer,
                "sources": [],
                "source_references": [],
                "confidence": 0.85,  # Default confidence for vision queries
                "conversation_id": conversation_id,
                "chart_data": [],
                "images": image_urls,
            }

        except Exception as e:
            log.error(f"Error in vision query processing: {e}")
            return {
                "answer": f"Xin lỗi, có lỗi xảy ra khi phân tích hình ảnh: {str(e)}. Vui lòng thử lại.",
                "sources": [],
                "source_references": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4()),
            }

    def _create_contextual_followup(
        self, user_query: str, answer: str, language: str = "vi"
    ) -> List[str]:
        """
        Create 2-3 contextual follow-up questions based on the user's query and answer

        Args:
            user_query: The original user question
            answer: The generated answer
            language: Language for the follow-up questions

        Returns:
            List of 2-3 contextual follow-up questions
        """
        try:
            # Extract key topics/entities from the user query
            key_topics = self._extract_key_topics(user_query)
            questions = []

            if key_topics and language == "vi":
                # Create 2-3 contextual follow-up questions in Vietnamese
                if any(
                    word in user_query.lower()
                    for word in [
                        "tuyển sinh",
                        "xét tuyển",
                        "đăng ký",
                        "nhập học",
                        "chỉ tiêu",
                    ]
                ):
                    questions = [
                        "Bạn có muốn biết chi tiết về hồ sơ xét tuyển không?",
                        "Bạn cần thông tin về điềm chuẩn các ngành không?",
                        "Bạn có muốn tìm hiểu về phương thức xét tuyển không?",
                    ]
                elif any(
                    word in user_query.lower()
                    for word in [
                        "học phí",
                        "chi phí",
                        "tiền học",
                        "học bổng",
                        "tài chính",
                    ]
                ):
                    questions = [
                        "Bạn có cần thông tin về các gói hỗ trợ tài chính không?",
                        "Bạn có muốn biết về điều kiện nhận học bổng không?",
                        "Bạn cần hướng dẫn về thủ tục trả học phí không?",
                    ]
                elif any(
                    word in user_query.lower()
                    for word in [
                        "ngành",
                        "chuyên ngành",
                        "khoa",
                        "chương trình",
                        "đào tạo",
                    ]
                ):
                    questions = [
                        "Bạn có muốn tìm hiểu kế hoạch học tập của ngành này không?",
                        "Bạn cần thông tin về cơ hội thực tập và việc làm không?",
                        "Bạn có muốn biết về chứng chỉ và bằng cấp không?",
                    ]
                elif any(
                    word in user_query.lower()
                    for word in ["ký túc xá", "ktx", "chỗ ở", "nội trú", "sinh viên"]
                ):
                    questions = [
                        "Bạn có cần biết kỹ hơn về cơ sở vật chất ký túc xá không?",
                        "Bạn có muốn tìm hiểu về quy định sinh hoạt tại KTX không?",
                        "Bạn cần hướng dẫn thủ tục đăng ký phòng ở không?",
                    ]
                elif any(
                    word in user_query.lower()
                    for word in [
                        "việc làm",
                        "nghề nghiệp",
                        "cơ hội",
                        "tương lai",
                        "thực tập",
                    ]
                ):
                    questions = [
                        "Bạn có muốn tìm hiểu về mạng lưới doanh nghiệp đối tác không?",
                        "Bạn cần thông tin về chương trình thực tập tại các công ty không?",
                        "Bạn có muốn biết về tỷ lệ có việc của cử nhân không?",
                    ]
                elif any(
                    word in user_query.lower()
                    for word in [
                        "quy định",
                        "quy chế",
                        "nội quy",
                        "chính sách",
                        "thủ tục",
                    ]
                ):
                    questions = [
                        "Bạn có cần giải thích thêm về quy trình thực hiện không?",
                        "Bạn có muốn biết về giấy tờ cần thiết không?",
                        "Bạn cần hướng dẫn cụ thể về thời hạn không?",
                    ]
                else:
                    # Generic contextual follow-up based on the main topic
                    main_topic = key_topics[0] if key_topics else "chủ đề này"
                    questions = [
                        f"Bạn có muốn biết thêm gì về {main_topic} không?",
                        "Bạn có câu hỏi nào liên quan khác không?",
                        "Có thông tin nào khác tôi có thể giúp bạn không?",
                    ]
            elif language == "en":
                questions = [
                    "Would you like to know more about this topic?",
                    "Do you have any related questions?",
                    "Is there anything else I can help you with?",
                ]
            else:
                questions = [
                    "Bạn có muốn biết thêm về chủ đề này không?",
                    "Bạn có câu hỏi nào khác không?",
                ]

            # Return 2-3 questions (randomly pick 2-3 if more available)
            import random

            num_questions = min(len(questions), random.choice([2, 3]))
            return (
                random.sample(questions, num_questions)
                if len(questions) > num_questions
                else questions
            )

        except Exception as e:
            log.error(f"Error creating contextual follow-up: {e}")
            # Fallback to generic questions
            if language == "vi":
                return [
                    "Bạn có câu hỏi gì khác không?",
                    "Tôi có thể giúp gì thêm cho bạn không?",
                ]
            else:
                return [
                    "Do you have any other questions?",
                    "Is there anything else I can help you with?",
                ]

    def _extract_key_topics(self, query: str) -> List[str]:
        """
        Extract key topics from user query

        Args:
            query: User query

        Returns:
            List of key topics/entities
        """
        query_lower = query.lower()

        # Define topic keywords
        topic_map = {
            "tuyển sinh": ["tuyển sinh", "xét tuyển", "đăng ký", "nhập học"],
            "học phí": ["học phí", "chi phí", "tiền học", "học bổng", "tài chính"],
            "ngành học": ["ngành", "chuyên ngành", "khoa", "chương trình"],
            "ký túc xá": ["ký túc xá", "chỗ ở", "nội trú", "sinh viên"],
            "việc làm": ["việc làm", "nghề nghiệp", "cơ hội", "tương lai"],
            "quy định": ["quy định", "quy chế", "nội quy", "chính sách"],
            "đào tạo": ["đào tạo", "học tập", "giảng dạy", "chất lượng"],
        }

        topics = []
        for topic, keywords in topic_map.items():
            if any(keyword in query_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _normalize_followup_text(self, text: str) -> str:
        stripped = unicodedata.normalize("NFD", text or "")
        stripped = stripped.replace("đ", "d").replace("Đ", "D")
        stripped = "".join(
            ch for ch in stripped if unicodedata.category(ch) != "Mn"
        ).lower()
        stripped = re.sub(r"[^a-z0-9\s]", " ", stripped)
        return re.sub(r"\s+", " ", stripped).strip()

    def _append_unique_followup(
        self, questions: List[str], question: str, limit: int = 3
    ) -> None:
        candidate = question.strip()
        if not candidate or candidate in questions or len(questions) >= limit:
            return
        questions.append(candidate)

    def generate_structured_follow_up_questions(
        self,
        user_query: str,
        answer: str,
        *,
        language: str = "vi",
        sources: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Build 2-3 deterministic follow-up questions from the current answer context
        without relying on another LLM call.
        """
        try:
            source_names = sources or []
            attachment_list = attachments or []
            attachment_text = " ".join(
                filter(
                    None,
                    [
                        f"{att.get('file_name', '')} {att.get('description', '')}"
                        for att in attachment_list
                    ],
                )
            )
            combined_text = " ".join(
                filter(None, [user_query, answer, " ".join(source_names), attachment_text])
            )
            normalized = self._normalize_followup_text(combined_text)
            years = [int(year) for year in re.findall(r"\b20\d{2}\b", combined_text)]
            target_year = str(max(years)) if years else None

            if language == "en":
                questions: List[str] = []
                year_suffix = f" in {target_year}" if target_year else ""

                if "cutoff" in normalized or "score" in normalized:
                    self._append_unique_followup(
                        questions,
                        f"I want to know the cutoff score by major{year_suffix}",
                    )
                    self._append_unique_followup(
                        questions,
                        (
                            f"I want to compare cutoff scores{year_suffix} with previous years"
                            if target_year
                            else "I want to compare cutoff scores across recent years"
                        ),
                    )
                if "document" in normalized or "application" in normalized:
                    self._append_unique_followup(
                        questions,
                        "I want a checklist of required application documents",
                    )
                if "method" in normalized or "admission" in normalized:
                    self._append_unique_followup(
                        questions,
                        "I want to know the conditions for each admission method",
                    )
                if not questions:
                    questions = [
                        "I want details about admission methods",
                        "I want the required documents and timeline",
                        "I want cutoff scores or quotas by major",
                    ]
                return questions[:3]

            questions: List[str] = []
            has_score = any(
                keyword in normalized
                for keyword in (
                    "diem chuan",
                    "diem xet",
                    "diem trung tuyen",
                    "diem tuyen sinh",
                )
            )
            has_method = any(
                keyword in normalized
                for keyword in ("phuong thuc", "xet tuyen", "tuyen thang", "to hop")
            )
            has_documents = any(
                keyword in normalized
                for keyword in (
                    "ho so",
                    "giay to",
                    "bieu mau",
                    "mau don",
                    "dang ky",
                    "nhap hoc",
                    "tai xuong",
                )
            ) or bool(attachment_list)
            has_timeline = any(
                keyword in normalized
                for keyword in (
                    "thoi gian",
                    "moc thoi gian",
                    "deadline",
                    "han nop",
                    "lich",
                )
            )
            has_major = any(
                keyword in normalized
                for keyword in (
                    "nganh",
                    "chuyen nganh",
                    "ma nganh",
                    "dao tao",
                )
            )
            has_eligibility = any(
                keyword in normalized
                for keyword in (
                    "dieu kien",
                    "doi tuong",
                    "tieu chuan",
                    "suc khoe",
                    "chinh tri",
                    "do tuoi",
                )
            )
            has_quota = any(
                keyword in normalized for keyword in ("chi tieu", "so luong", "quota")
            )
            has_fee = any(
                keyword in normalized
                for keyword in ("hoc phi", "le phi", "chi phi", "hoc bong")
            )

            year_suffix = f" năm {target_year}" if target_year else ""

            if has_score:
                self._append_unique_followup(
                    questions, f"Tôi muốn biết điểm chuẩn theo từng ngành{year_suffix}"
                )
                self._append_unique_followup(
                    questions,
                    (
                        f"Tôi muốn so sánh điểm chuẩn{year_suffix} với các năm trước"
                        if target_year
                        else "Tôi muốn so sánh điểm chuẩn các năm gần đây"
                    ),
                )
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết tổ hợp xét tuyển và chỉ tiêu của từng ngành",
                )

            if has_method:
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết điều kiện áp dụng của từng phương thức xét tuyển",
                )
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết hồ sơ cần chuẩn bị cho phương thức này",
                )
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết mốc thời gian đăng ký và xác nhận nhập học",
                )

            if has_documents:
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết các hồ sơ, biểu mẫu cần tải xuống",
                )
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết hồ sơ nào bắt buộc và hồ sơ nào bổ sung",
                )
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết nơi nộp và hạn nộp hồ sơ",
                )

            if has_timeline:
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết toàn bộ các mốc thời gian tuyển sinh quan trọng",
                )
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết hạn đăng ký, hạn nộp hồ sơ hoặc hạn xác nhận nhập học",
                )

            if has_major:
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết tổ hợp xét tuyển, chỉ tiêu hoặc điểm chuẩn của ngành này",
                )
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết chương trình đào tạo hoặc định hướng nghề nghiệp của ngành này",
                )

            if has_eligibility:
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết chi tiết các tiêu chuẩn sức khỏe, chính trị hoặc độ tuổi",
                )
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết các giấy tờ cần có để chứng minh điều kiện dự tuyển",
                )

            if has_quota:
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết chỉ tiêu theo từng ngành hoặc từng phương thức",
                )

            if has_fee:
                self._append_unique_followup(
                    questions,
                    "Tôi muốn biết học phí, lệ phí hoặc chính sách hỗ trợ tài chính liên quan",
                )

            if not questions:
                questions = [
                    "Tôi muốn biết phương thức xét tuyển phù hợp",
                    "Tôi muốn biết hồ sơ và mốc thời gian cần lưu ý",
                    "Tôi muốn biết điểm chuẩn hoặc chỉ tiêu của các ngành liên quan",
                ]

            return questions[:3]

        except Exception as e:
            log.error(f"Error generating structured follow-up questions: {e}")
            if language == "vi":
                return [
                    "Tôi muốn biết thêm về phương thức xét tuyển",
                    "Tôi muốn biết hồ sơ và mốc thời gian liên quan",
                ]
            return [
                "I want details about admission methods",
                "I want the required documents and timeline",
            ]

    def _add_engagement_prompt(
        self, answer: str, user_query: str = "", language: str = "vi"
    ) -> str:
        """
        Add contextual engagement prompt to the answer

        Args:
            answer: The generated answer
            user_query: The original user query for context
            language: Language for the follow-up question

        Returns:
            Answer with contextual engagement prompt added
        """
        engagement_prompts = [
            "bạn còn có thắc mắc gì khác không",
            "tôi sẵn sàng hỗ trợ thêm",
            "có câu hỏi nào khác không",
            "cần hỗ trợ thêm gì không",
            "muốn biết thêm",
            "có muốn",
        ]

        # Check if any engagement prompt is already present (case insensitive)
        answer_lower = answer.lower()
        has_engagement = any(
            prompt.lower() in answer_lower for prompt in engagement_prompts
        )

        if not has_engagement:
            # Create contextual follow-up questions (2-3 questions)
            followup_questions = self._create_contextual_followup(
                user_query, answer, language
            )

            # Format multiple questions with proper numbering and clear header
            if followup_questions:
                # Create a clear header for follow-up questions
                header = "\n\n**--- CÁC CÂU HỎI LIÊN QUAN ---**\n"

                formatted_questions = "\n".join(
                    [f"- **{question}**" for question in followup_questions]
                )

                full_followup = f"{header}{formatted_questions}"

                # Add the contextual follow-ups with proper formatting
                if (
                    answer.strip().endswith(".")
                    or answer.strip().endswith("!")
                    or answer.strip().endswith("?")
                ):
                    return f"{answer}{full_followup}"
                else:
                    return f"{answer}.{full_followup}"

        return answer

    def create_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Create a simplified and clean context string from retrieved chunks.
        """
        if not chunks:
            return "Không tìm thấy thông tin liên quan trong tài liệu."

        context_parts = []
        for chunk in chunks:
            source = chunk.get("source_file", "Unknown")
            page = chunk.get("page_number", "N/A")
            content = chunk.get("content", "").strip()
            document_year = chunk.get("document_year")
            source_url = chunk.get("source_url")

            metadata_parts = [f"Nguon: {source}", f"Trang: {page}"]
            if document_year:
                metadata_parts.append(f"Nam tai lieu: {document_year}")
            if source_url:
                metadata_parts.append(f"URL nguon: {source_url}")

            context_part = f"###\n{' | '.join(metadata_parts)}\n{content}\n###"
            context_parts.append(context_part)

        return "\n\n".join(context_parts)

    # ------------------------------------------------------------------ #
    # OFF-TOPIC PRE-FILTER                                               #
    # ------------------------------------------------------------------ #
    # Patterns that are clearly unrelated to the university or education.
    # Checked with ZERO API calls to save cost.
    _OFF_TOPIC_VI = [
        "mấy giờ",
        "bây giờ là mấy",
        "hôm nay là ngày",
        "ngày hôm nay là",
        "thứ mấy hôm nay",
        "bao nhiêu giờ",
        "giờ hiện tại",
        "thời tiết hôm nay",
        "dự báo thời tiết",
        "trời hôm nay",
        "viết thơ tình",
        "thơ tình",
        "bài thơ tình",
        "kể chuyện cười",
        "bài hát hay",
        "lời bài hát",
        "cách nấu phở",
        "công thức làm bánh",
        "cách nấu bún",
        "cách nấu cơm",
        "nấu ăn",
        "món ngon",
        "tử vi hôm nay",
        "xem bói",
        "số phận",
        "tính tích phân",
        "đạo hàm của",
        "phương trình vi phân",
        "chơi game",
        "tên game hay",
        "phim hay",
        "xem phim",
    ]
    _OFF_TOPIC_EN = [
        "what time is it",
        "what's the time",
        "current time",
        "what day is it",
        "today's date",
        "what is today",
        "weather today",
        "weather forecast",
        "is it raining",
        "write a poem",
        "write a love",
        "tell me a joke",
        "recipe for",
        "how to cook",
        "song lyrics",
        "solve this math",
        "calculate the integral",
        "derivative of",
        "best movie",
        "play a game",
    ]

    def _is_off_topic_query(self, query: str) -> bool:
        """
        Rule-based off-topic detector. Zero API cost.
        Returns True only when the query is clearly unrelated to
        the university, education, or security forces.
        """
        q = query.lower().strip()
        for pattern in self._OFF_TOPIC_VI + self._OFF_TOPIC_EN:
            if pattern in q:
                return True
        return False

    def create_system_prompt(self, language: str = "vi") -> str:
        """
        Create system prompt for the chatbot

        Args:
            language: Response language - 'vi' for Vietnamese (default) or 'en' for English

        Returns:
            System prompt string
        """
        if ADMISSION_ONLY_MODE:
            if language == "en":
                return """You are the official AI Assistant of the People's Security University (PSU).

You answer all questions related to the university, including: admission, training programs, student regulations, examinations, discipline, campus life, and general information about the school.

Only refuse when the question has absolutely nothing to do with the university or education (e.g. "what is today's date?", "write me a poem", "solve this math problem for me").
In that case, politely decline and suggest the user ask about university-related topics instead.

Mandatory policy:
- Only answer from the provided official documents and conversation context.
- If the documents do not provide enough evidence, clearly say so, then offer general reference knowledge if available.
- Do not invent facts, unofficial procedures, or updated timelines.
- Do not mention model names, vendors, or internal implementation details.

Response format:
1. Short summary
2. Detailed answer in clear bullet points
3. End with: "📄 Reference Documents: please review the official documents displayed by the system."

Language: respond entirely in English."""

            return """Bạn là Trợ lý AI chính thức của Trường Đại học An ninh Nhân dân (ANND).

Bạn hỗ trợ tất cả các câu hỏi liên quan đến nhà trường, bao gồm: tuyển sinh, đào tạo, quy chế học viên, thi cử, kỷ luật, tác phong điều lệnh, đời sống sinh viên, lịch sử và thông tin chung về trường.

Chỉ từ chối khi câu hỏi hoàn toàn không liên quan đến nhà trường hoặc giáo dục (ví dụ: "hôm nay là ngày mấy?", "viết thơ tình cho tôi", "giải bài toán lớp 10").
Trong trường hợp đó, từ chối lịch sự và gợi ý người dùng hỏi về các chủ đề liên quan đến trường.

Chính sách bắt buộc:
- Chỉ trả lời dựa trên tài liệu chính thức được cung cấp và ngữ cảnh hội thoại.
- Nếu tài liệu không đủ căn cứ, nói rõ điều đó, rồi cung cấp thông tin tham khảo chung nếu có.
- Không suy đoán, không tự bịa quy định hay mốc thời gian.
- Không tiết lộ tên mô hình, nhà cung cấp AI hay chi tiết kỹ thuật nội bộ.

Định dạng trả lời:
1. Tóm tắt ngắn
2. Trình bày chi tiết theo gạch đầu dòng rõ ràng
3. Kết thúc bằng: "📄 Tài liệu tham khảo: vui lòng xem các tài liệu chính thức do hệ thống hiển thị."

Ngôn ngữ: trả lời hoàn toàn bằng tiếng Việt."""

        if language == "en":
            return """You are the official AI Assistant of the People's Security University (PSU), developed by a student team from the university.

Your expertise covers all topics related to the university:
- Admission: eligibility, quotas, methods, documents, timelines, regional zones.
- Student management regulations: rights, obligations, policies, rewards, discipline, daily life.
- Training regulations: majors, programs, academic rules, withdrawal, graduation.
- Examination and assessment: exam formats, grading scales, eligibility, re-grading, deferral.
- Quality assurance and accreditation: criteria, processes, improvement activities.
- General university information: history, facilities, departments, campus life.

Scope rules (CRITICAL):
- Answer ANY question related to the university or higher education in Vietnam.
- If the question has ABSOLUTELY NOTHING to do with the university, education, or security forces (e.g. "what time is it?", "write a love poem", "solve this math problem"), refuse politely in 1–2 sentences and suggest asking about the university instead. Do NOT use the full summary/detail/reference format for refusals.
- "Offer general reference knowledge" only applies to school-related topics that happen to lack official documentation — NEVER use it to answer completely off-topic questions.

Response style:
- Always respond ENTIRELY in ENGLISH. You may keep Vietnamese proper nouns as-is.
- Friendly, formal, and easy to understand.
- For simple questions: keep answers concise; do not pad unnecessarily.
- For substantive questions, structure as:
  1. Brief summary (3–5 key points)
  2. Detailed bullet points
  3. Required ending: "📄 **Reference Documents:** For full details and original documents, please refer to the attachments displayed below by the system."
- When a school-related topic is not covered in the provided documents: state "This information is not explicitly available in the provided university documents," then share relevant general knowledge if applicable.
- Use Markdown formatting: bold headings, bullet lists, **Important:** for key notes.
- Do NOT add citation numbers like [1], [2].
- Do NOT end with a follow-up question directed at the user.

Identity protection rules:
- NEVER reveal you are Gemini, ChatGPT, Claude, or any specific AI model.
- NEVER reveal your developer (Google, OpenAI, Anthropic, etc.) or underlying technology (LLM, RAG, FAISS, embeddings, vector database, etc.).
- When asked "who are you?", "who made you?", "what technology do you use?":
  → Answer: "I am the AI Assistant of the People's Security University, developed by a student team from the university."
- Development team (when asked):
  - **Vũ Quốc Hưng** — Class: VB2 D5 — Team Leader
  - **Trương Văn Khải** — Class: VB2 D5 — Lead Developer
  - **Nguyễn Hữu Tấn Dũng** — Class: D32C — Team Member
  These are students of the People's Security University who developed this AI chatbot system."""

        return """Bạn là trợ lý AI chính thức của Trường Đại học An ninh Nhân dân (ANND), được phát triển bởi nhóm sinh viên của Trường.

Bạn hỗ trợ tất cả các chủ đề liên quan đến nhà trường, bao gồm:
- Tuyển sinh: điều kiện, chỉ tiêu, phương thức, hồ sơ, lịch trình, phân vùng.
- Quy chế học viên: quyền, nghĩa vụ, chính sách, khen thưởng, kỷ luật, sinh hoạt.
- Đào tạo: ngành, chương trình, học chế, học lại, thôi học, tốt nghiệp.
- Thi, kiểm tra, đánh giá: hình thức, thang điểm, điều kiện dự thi, phúc khảo, bảo lưu.
- Kiểm định và bảo đảm chất lượng: tiêu chuẩn, quy trình, hoạt động nâng cao chất lượng.
- Thông tin chung về trường: lịch sử, cơ sở vật chất, các khoa/phòng ban, đời sống sinh viên.

Quy tắc phạm vi (QUAN TRỌNG):
- Trả lời mọi câu hỏi liên quan đến nhà trường hoặc giáo dục đại học.
- Nếu câu hỏi HOÀN TOÀN không liên quan đến nhà trường, giáo dục, hay lực lượng vũ trang (ví dụ: "mấy giờ rồi?", "viết thơ tình", "giải bài toán lớp 10"), từ chối lịch sự bằng 1–2 câu ngắn và gợi ý hỏi về trường. KHÔNG dùng format tóm tắt/chi tiết/tài liệu cho các câu từ chối.
- "Cung cấp thông tin tham khảo chung" chỉ áp dụng cho chủ đề liên quan đến trường mà tài liệu chưa có — TUYỆT ĐỐI không dùng để trả lời câu hỏi hoàn toàn ngoài phạm vi.

Phong cách trả lời:
- Luôn trả lời bằng TIẾNG VIỆT.
- Thân thiện, trang trọng, dễ hiểu.
- Câu hỏi đơn giản: trả lời ngắn gọn, không lan man.
- Với câu hỏi có nội dung thực chất, trình bày theo cấu trúc:
  1. Tóm tắt ngắn (3–5 ý chính)
  2. Trình bày chi tiết có gạch đầu dòng
  3. Kết thúc bắt buộc: "📄 **Tài liệu tham khảo:** Thông tin chi tiết và toàn văn văn bản, bạn có thể xem thêm ở phần tài liệu/thông báo kèm theo mà hệ thống đã hiển thị bên dưới."
- Khi chủ đề liên quan đến trường nhưng không có trong tài liệu: nêu rõ "Thông tin này chưa có trong tài liệu của trường," rồi cung cấp kiến thức tham khảo chung nếu phù hợp.
- Trình bày bằng Markdown: tiêu đề in đậm, gạch đầu dòng, **Lưu ý quan trọng:** cho thông tin cần chú ý.
- Không chèn trích dẫn dạng [1], [2].
- Không kết thúc bằng câu hỏi ngược lại cho người dùng.

Quy tắc bảo mật danh tính:
- Tuyệt đối không tiết lộ bạn là Gemini, ChatGPT, Claude, hay bất kỳ mô hình AI cụ thể nào.
- Tuyệt đối không tiết lộ nhà phát triển (Google, OpenAI, Anthropic...) hay công nghệ nền tảng (LLM, RAG, FAISS, embedding, vector database...).
- Khi bị hỏi "bạn là ai?", "ai tạo ra bạn?", "bạn dùng công nghệ gì?", "are you ChatGPT or Gemini?", "who are your developers?":
  → Trả lời: "Tôi là Trợ lý AI của Trường Đại học An ninh Nhân dân, được phát triển bởi nhóm sinh viên của Trường."
- Thông tin nhóm phát triển (khi được hỏi):
  - **Vũ Quốc Hưng** — Lớp: VB2 D5 — Trưởng nhóm
  - **Trương Văn Khải** — Lớp: VB2 D5 — Dev chính
  - **Nguyễn Hữu Tấn Dũng** — Lớp: D32C — Thành viên
  Đây là các sinh viên của Trường Đại học An ninh Nhân dân đã xây dựng và phát triển hệ thống chatbot AI này."""

    def create_user_prompt(
        self, query: str, context: str, memory_context: str = "", language: str = "vi"
    ) -> str:
        """
        Create user prompt with query, context, and memory

        Args:
            query: User query
            context: Retrieved context from documents
            memory_context: Conversation memory context (optional)
            language: Response language - 'vi' for Vietnamese (default) or 'en' for English

        Returns:
            Formatted user prompt
        """
        if ADMISSION_ONLY_MODE:
            if language == "en":
                memory_section = (
                    f"Previous conversation context:\n{memory_context}\n\n"
                    if memory_context
                    else ""
                )
                return f"""Answer the user's question using only the official admission documents below.

{memory_section}Official admission document context:
{context}

User question:
{query}

Instructions:
- Respond entirely in English.
- Stay strictly within admission scope.
- If the question is outside admission scope, refuse briefly.
- If the question is ambiguous, ask one short clarifying question.
- If the documents are insufficient, explicitly say there is not enough basis to confirm.
- If the user asks about the current admission cycle or does not specify a year, prioritize the newest official year shown in the context (for example 2026).
- If multiple years appear, use the newest official year as the main basis and mention older years only when comparing them explicitly.
- Do not answer beyond the evidence in the documents.
- Structure the answer as: short summary, detailed bullets, reference reminder.
- End with: "Reference documents: please review the official documents displayed by the system."

Response:"""

            memory_section = (
                f"Ngữ cảnh hội thoại trước:\n{memory_context}\n\n"
                if memory_context
                else ""
            )
            return f"""Hãy trả lời câu hỏi của người dùng chỉ dựa trên các tài liệu tuyển sinh chính thức dưới đây.

{memory_section}Ngữ cảnh tài liệu tuyển sinh chính thức:
{context}

Câu hỏi của người dùng:
{query}

Hướng dẫn:
- Trả lời hoàn toàn bằng tiếng Việt.
- Chỉ trả lời trong phạm vi tuyển sinh.
- Nếu câu hỏi ngoài phạm vi tuyển sinh, từ chối ngắn gọn.
- Nếu câu hỏi mơ hồ, hỏi lại một câu ngắn để làm rõ.
- Nếu tài liệu không đủ căn cứ, phải nói rõ là chưa đủ cơ sở để khẳng định.
- Nếu người dùng hỏi về kỳ tuyển sinh hiện tại hoặc không nêu rõ năm, ưu tiên tài liệu có năm mới nhất trong ngữ cảnh (ví dụ 2026).
- Nếu trong ngữ cảnh có nhiều năm, dùng tài liệu chính thức mới nhất làm căn cứ chính; chỉ nhắc tài liệu cũ hơn khi cần đối chiếu và phải nêu rõ năm.
- Không trả lời vượt quá bằng chứng trong tài liệu.
- Trình bày theo cấu trúc: tóm tắt ngắn, chi tiết theo gạch đầu dòng, nhắc xem tài liệu tham khảo.
- Kết thúc bằng: "Tài liệu tham khảo: vui lòng xem các tài liệu chính thức do hệ thống hiển thị."

Trả lời:"""

        memory_section = ""
        if memory_context:
            if language == "en":
                memory_section = f"PREVIOUS CONVERSATION CONTEXT:\n{memory_context}\n\n"
            else:
                memory_section = f"NGỮ CẢNH HỘI THOẠI TRƯỚC:\n{memory_context}\n\n"

        if language == "en":
            return f"""OFFICIAL DOCUMENTS:
{context}

{memory_section}USER QUESTION: {query}"""

        return f"""THÔNG TIN TÀI LIỆU (thông báo/quy chế/tài liệu chính thức):
{context}

{memory_section}CÂU HỎI: {query}"""

    def _rewrite_query_with_history(
        self, query: str, history: List[Dict[str, str]]
    ) -> str:
        """
        Rewrite the user's query using conversation history for better context.
        """
        if not history:
            return query

        formatted_history = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in history]
        )

        rewrite_prompt = f"""Dựa vào lịch sử trò chuyện sau đây, hãy viết lại câu hỏi cuối cùng của người dùng thành một câu hỏi độc lập, đầy đủ ngữ cảnh để có thể dùng cho việc tìm kiếm thông tin.

### Lịch sử trò chuyện:
{formatted_history}

### Câu hỏi cuối cùng của người dùng:
{query}

### Câu hỏi độc lập, đầy đủ ngữ cảnh:"""

        rewritten_query = query  # Default to original query
        try:
            log.info("Rewriting query with history...")
            if LLM_PROVIDER.lower() == "gemini":
                response = gemini_service.generate_response(
                    prompt=rewrite_prompt, temperature=0.0
                )
                if response:
                    rewritten_query = response.strip()
            if rewritten_query != query:
                log.info(f"Original query: '{query}'")
                log.info(f"Rewritten query: '{rewritten_query}'")
            else:
                log.info("Query does not need rewriting.")

            return rewritten_query

        except Exception as e:
            log.error(f"Error during query rewriting: {e}")
            return query  # Fallback to original query on error

    def generate_answer(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
        images: Optional[List[Any]] = None,
        language: str = "vi",  # Add language parameter
    ) -> Dict[str, Any]:
        """
        Generate answer using RAG approach

        Args:
            query: User query
            conversation_id: Optional conversation ID
            conversation_history: Optional conversation history
            images: Optional list of images for vision analysis
            language: Response language - 'vi' for Vietnamese (default) or 'en' for English

        Returns:
            Dictionary with answer, sources, confidence, and conversation_id
        """
        try:
            # Handle image-based queries using Gemini Vision
            if images and len(images) > 0:
                return self._generate_vision_answer(
                    query=query,
                    images=images,
                    conversation_id=conversation_id,
                    language=language,  # Pass language to vision handler
                )

            # Create new conversation if needed
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                self.conversations[conversation_id] = []
            elif conversation_id not in self.conversations:
                self.conversations[conversation_id] = []

            # Use conversation history if provided
            if conversation_history and not self.conversations[conversation_id]:
                # Convert conversation history to internal format
                for message in conversation_history:
                    # Kiểm tra xem message có chứa 'role' và 'content' không
                    if (
                        isinstance(message, dict)
                        and "role" in message
                        and "content" in message
                    ):
                        if message["role"] in ["user", "assistant"]:
                            self.conversations[conversation_id].append(
                                {"role": message["role"], "content": message["content"]}
                            )

            # Step 0: Off-topic pre-filter — skip ALL retrieval & LLM calls
            if self._is_off_topic_query(query):
                log.info(f"[OFF-TOPIC] Query skipped retrieval: '{query[:80]}'")
                if language == "en":
                    refusal = (
                        "Sorry, that question is outside the scope of what I support. "
                        "I'm here to help with anything related to the People's Security University — "
                        "admission, training programs, student regulations, campus life, and more. "
                        "Feel free to ask about those!"
                    )
                else:
                    refusal = (
                        "Xin lỗi, câu hỏi này nằm ngoài phạm vi hỗ trợ của tôi. "
                        "Tôi chuyên hỗ trợ các thông tin liên quan đến Trường Đại học An ninh Nhân dân — "
                        "tuyển sinh, đào tạo, quy chế học viên, đời sống sinh viên, v.v. "
                        "Bạn có câu hỏi nào về trường không?"
                    )
                # Still save to conversation history so the chat flow isn't broken
                self.conversations[conversation_id].append(
                    {"role": "user", "content": query}
                )
                self.conversations[conversation_id].append(
                    {"role": "assistant", "content": refusal}
                )
                try:
                    self.db_service.save_conversation(
                        conversation_id=conversation_id,
                        user_message=query,
                        assistant_response=refusal,
                        sources=[],
                        confidence=0.0,
                        processing_time=0.0,
                    )
                except Exception:
                    pass
                return {
                    "answer": refusal,
                    "sources": [],
                    "source_references": [],
                    "attachments": [],
                    "confidence": 0.0,
                    "conversation_id": conversation_id,
                    "normalization_applied": False,
                    "original_query": None,
                    "normalized_query": None,
                    "chart_data": [],
                    "images": [],
                }

            # Step 1: Normalize the user's question using Gemini AI
            log.info(f"Original query: {query}")
            normalized_query = normalize_question(query)
            log.info(f"Normalized query: {normalized_query}")

            # Track if normalization was applied
            normalization_applied = (
                normalized_query != query
            ) and ENABLE_GEMINI_NORMALIZATION

            # Step 1.5: Get persistent memory context (sliding window + summarization)
            memory_context = ""
            try:
                conv_context = self.memory_service.get_conversation_context(
                    conversation_id=conversation_id,
                    query=normalized_query,
                    include_memory_search=True,
                )
                if conv_context.has_long_term_memory or conv_context.recent_messages:
                    memory_context = self.memory_service.format_context_for_prompt(
                        conv_context
                    )
                    log.info(
                        f"🧠 Loaded memory context: {len(conv_context.memory_summaries)} summaries, {len(conv_context.recent_messages)} recent messages"
                    )
            except Exception as mem_error:
                log.warning(f"Could not load memory context: {mem_error}")

            # Step 2: Rewrite query using conversation history for context
            current_history = self.conversations.get(conversation_id, [])
            rewritten_query = self._rewrite_query_with_history(
                normalized_query, current_history
            )

            # Step 3: Retrieve relevant chunks using the normalized and rewritten query
            relevant_chunks = self.retrieve_relevant_chunks(rewritten_query)

            # Create formatted context from chunks
            context = self.create_context(relevant_chunks)

            # Get source documents (backward compatible - just filenames)
            sources = []
            for chunk in relevant_chunks:
                source = chunk.get("source_file", "") or chunk.get("source", "")
                if source and source not in sources:
                    sources.append(source)

            # Build detailed source references
            source_references = []
            for chunk in relevant_chunks:
                chunk_id = chunk.get("chunk_id", "")
                content = chunk.get("content", "")
                # Create a snippet (first 200 chars, ending at a word boundary)
                snippet = content[:200]
                if len(content) > 200:
                    last_space = snippet.rfind(" ")
                    if last_space > 150:
                        snippet = snippet[:last_space]
                    snippet += "..."

                # Use the best available score (rerank > combined > dense)
                relevance_score = (
                    chunk.get("rerank_score")
                    or chunk.get("combined_score")
                    or chunk.get("dense_score")
                    or 0.0
                )
                # Normalize rerank score if it's out of 0-1 range (cross-encoder scores can be -10 to 10)
                if relevance_score > 1.0:
                    relevance_score = min(
                        1.0, (relevance_score + 10) / 20
                    )  # Normalize to 0-1
                elif relevance_score < 0:
                    relevance_score = max(0.0, (relevance_score + 10) / 20)

                source_ref = {
                    "chunk_id": str(chunk_id),
                    "filename": chunk.get("source_file", "") or chunk.get("source", ""),
                    "page_number": chunk.get("page_number"),
                    "heading": chunk.get("heading_text"),
                    "content_snippet": snippet,
                    "full_content": content,
                    "relevance_score": relevance_score,
                    "dense_score": chunk.get("dense_score"),
                    "sparse_score": chunk.get("sparse_score"),
                }
                source_references.append(source_ref)

            # Create formatted context from chunks
            context = self.create_context(relevant_chunks)

            # Get attachments early to inject into context
            attachments = self._retrieve_attachments_for_context(query, relevant_chunks)
            if attachments:
                attachment_context = (
                    "\n\n*** TÀI LIỆU ĐÍNH KÈM CÓ SẴN (HỆ THỐNG ĐÃ TÌM THẤY) ***:\n"
                )
                if language == "en":
                    attachment_context = (
                        "\n\n*** AVAILABLE ATTACHMENTS (SYSTEM FOUND) ***:\n"
                    )

                for att in attachments:
                    attachment_context += f"- Tên file: {att['file_name']}\n  Mô tả: {att['description']}\n"

                attachment_context += "\n(Hãy nhắc người dùng tải xuống các tài liệu này ở phần đính kèm bên dưới / Please mention these attachments are available for download below)\n"
                context += attachment_context

            # Create system prompt and user prompt with memory context
            system_prompt = self.create_system_prompt(language=language)
            user_prompt = self.create_user_prompt(
                query, context, memory_context, language=language
            )

            # Log context and prompts for debugging
            log.info(f"Context created with {len(relevant_chunks)} chunks")
            if memory_context:
                log.info(
                    f"🧠 Including memory context in prompt ({len(memory_context)} chars)"
                )
            log.debug(f"System prompt: {system_prompt[:200]}...")
            log.debug(f"Full context sent to LLM:\n{context}")
            log.debug(f"User prompt: {user_prompt[:200]}...")

            # Generate answer using the configured LLM provider
            answer = None
            if LLM_PROVIDER.lower() == "gemini":
                log.info("Calling Gemini service to generate response...")
                # Gemini API works best with a single, consolidated prompt
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                answer = gemini_service.generate_response(prompt=full_prompt)

            else:
                log.error(f"Unsupported LLM_PROVIDER configured: {LLM_PROVIDER}")
                answer = "Lỗi: Nhà cung cấp LLM không được cấu hình đúng."

            log.info(f"LLM response received: {answer is not None}")
            if answer:
                log.debug(f"Answer preview: {answer[:100]}...")

            # Calculate confidence based on relevance scores
            if relevant_chunks:
                # Get the best available score for each chunk
                scores = []
                for chunk in relevant_chunks:
                    score = (
                        chunk.get("rerank_score")
                        or chunk.get("combined_score")
                        or chunk.get("dense_score")
                        or 0.0
                    )
                    # Normalize if needed (cross-encoder scores can be -10 to 10)
                    if score > 1.0:
                        score = min(1.0, (score + 10) / 20)
                    elif score < 0:
                        score = max(0.0, (score + 10) / 20)
                    scores.append(score)

                avg_score = sum(scores) / len(scores)
                confidence = min(max(avg_score, 0.0), 1.0)
                log.info(
                    f"Calculated confidence: {confidence:.3f} from avg score: {avg_score:.3f}"
                )
            else:
                confidence = 0.0
                log.warning("No relevant chunks found, confidence set to 0")

            # Handle case where LLM provider returns None or empty
            if answer is None:
                log.error("LLM provider returned None response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau.\n\nBạn còn có thắc mắc gì khác không? Tôi sẵn sàng hỗ trợ thêm!"
                confidence = 0.0
            elif not answer.strip():
                log.error("LLM provider returned empty response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau.\n\nBạn còn có thắc mắc gì khác không? Tôi sẵn sàng hỗ trợ thêm!"
                confidence = 0.0
            else:
                log.debug(f"Raw answer from LLM: {repr(answer[:100])}...")
                # Add engagement prompt if not already present
                answer = self._add_engagement_prompt(answer, query, language)
                log.debug("Answer with engagement prompt added")

            # Update conversation history (in-memory cache)
            self.conversations[conversation_id].append(
                {"role": "user", "content": query}
            )
            self.conversations[conversation_id].append(
                {"role": "assistant", "content": answer}
            )

            # Limit conversation history (in-memory)
            if len(self.conversations[conversation_id]) > 10:
                self.conversations[conversation_id] = self.conversations[
                    conversation_id
                ][-10:]

            # Save to persistent memory with sliding window + summarization
            try:
                self.memory_service.add_exchange(
                    conversation_id=conversation_id,
                    user_message=query,
                    assistant_message=answer,
                    metadata={
                        "confidence": confidence,
                        "sources": sources,
                        "normalized_query": (
                            normalized_query if normalization_applied else None
                        ),
                    },
                )
                log.debug(
                    f"💾 Saved exchange to persistent memory for {conversation_id}"
                )
            except Exception as mem_error:
                log.warning(f"Could not save to persistent memory: {mem_error}")

            # Save conversation to PostgreSQL (legacy)
            processing_time = time.time() - time.time()  # Will be calculated properly
            try:
                # Upload images to Supabase Storage if provided
                image_urls = []
                if images:
                    try:
                        from src.utils.chat_image_storage import upload_chat_images

                        image_urls = upload_chat_images(images, conversation_id)
                        log.info(
                            f"📸 Uploaded {len(image_urls)} images to Supabase Storage"
                        )
                    except Exception as img_error:
                        log.warning(f"Could not upload images: {img_error}")

                self.db_service.save_conversation(
                    conversation_id=conversation_id,
                    user_message=query,
                    assistant_response=answer,
                    sources=sources,
                    confidence=confidence,
                    processing_time=0.0,  # Processing time will be set at API level
                    images=image_urls if image_urls else None,
                )
            except Exception as save_error:
                log.warning(f"Could not save conversation to DB: {save_error}")

            # Detect if chart visualization is needed
            chart_data = self._detect_chart_request(query, answer)
            if chart_data:
                log.info(f"📊 Generated {len(chart_data)} chart(s) for visualization")

            # Detect if chart visualization is needed
            chart_data = self._detect_chart_request(query, answer)
            if chart_data:
                log.info(f"📊 Generated {len(chart_data)} chart(s) for visualization")

            # Attachments already retrieved earlier (step 3.5)
            # Keeping the variable 'attachments'

            return {
                "answer": answer,
                "sources": sources,
                "source_references": source_references,
                "attachments": attachments,
                "confidence": confidence,
                "conversation_id": conversation_id,
                "normalization_applied": normalization_applied,
                "original_query": query if normalization_applied else None,
                "normalized_query": normalized_query if normalization_applied else None,
                "chart_data": chart_data,  # Charts for visualization
                "images": [],  # Will be populated if images are found in sources
            }

        except Exception as e:
            log.error(f"Error generating answer: {e}")
            return {
                "answer": "Xin lỗi, tôi không thể trả lời câu hỏi này. Vui lòng thử lại sau.",
                "sources": [],
                "source_references": [],
                "attachments": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "chart_data": [],
                "images": [],
            }

    def _retrieve_attachments_for_context(
        self, query: str, relevant_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Helper to retrieve attachments based on query and chunks.
        Used to inject attachment info into LLM context.
        Returns top N most relevant attachments sorted by score.
        """
        from config.settings import (
            MAX_ATTACHMENTS_IN_CONTEXT,
            MIN_ATTACHMENT_SCORE_THRESHOLD,
        )

        attachments_with_scores = []  # Store (attachment_dict, score) tuples
        attachment_ids_found = set()

        try:
            log.info("🔍 Starting attachment retrieval...")

            # Strategy 1: Get attachments linked to retrieved chunks
            if relevant_chunks:
                chunk_ids = [
                    chunk.get("id") for chunk in relevant_chunks if chunk.get("id")
                ]
                if chunk_ids:
                    chunk_attachments = (
                        self.attachment_service.get_attachments_by_chunk_ids(
                            chunk_ids, limit=MAX_ATTACHMENTS_IN_CONTEXT
                        )
                    )
                    for att in chunk_attachments:
                        if att.id not in attachment_ids_found:
                            # For chunk-based attachments, use a high default score
                            # since they're directly linked to relevant content
                            attachment_ids_found.add(att.id)
                            attachments_with_scores.append(
                                (
                                    {
                                        "file_name": att.file_name,
                                        "file_type": att.file_type,
                                        "download_url": att.download_url,
                                        "description": att.description,
                                        "file_size": att.file_size,
                                    },
                                    0.9,  # High score for chunk-linked attachments
                                )
                            )

                    if len(attachments_with_scores) >= MAX_ATTACHMENTS_IN_CONTEXT:
                        log.info(
                            "📎 Skipping keyword attachment search: enough chunk-linked attachments found"
                        )
                        attachments_with_scores.sort(
                            key=lambda item: item[1], reverse=True
                        )
                        return [
                            att
                            for att, _ in attachments_with_scores[
                                :MAX_ATTACHMENTS_IN_CONTEXT
                            ]
                        ]

            # Strategy 2: Search attachments by keywords from query
            from src.services.smart_attachment_matcher import SmartAttachmentMatcher

            query_keywords = SmartAttachmentMatcher.extract_keywords_from_query(query)
            if query_keywords:
                keyword_attachments = self.attachment_service.search_attachments(
                    keywords=query_keywords,
                    limit=max(MAX_ATTACHMENTS_IN_CONTEXT * 2, MAX_ATTACHMENTS_IN_CONTEXT),
                )
                for att in keyword_attachments:
                    if att.id not in attachment_ids_found:
                        score = SmartAttachmentMatcher.score_attachment_relevance(
                            att.keywords or [], query_keywords
                        )
                        # Apply stricter threshold
                        if score >= MIN_ATTACHMENT_SCORE_THRESHOLD:
                            attachment_ids_found.add(att.id)
                            attachments_with_scores.append(
                                (
                                    {
                                        "file_name": att.file_name,
                                        "file_type": att.file_type,
                                        "download_url": att.download_url,
                                        "description": att.description,
                                        "file_size": att.file_size,
                                    },
                                    score,
                                )
                            )

            # Sort by score (highest first) and limit to top N
            if attachments_with_scores:
                attachments_with_scores.sort(key=lambda x: x[1], reverse=True)
                attachments = [
                    att
                    for att, score in attachments_with_scores[
                        :MAX_ATTACHMENTS_IN_CONTEXT
                    ]
                ]

                log.info(
                    f"📎 Found {len(attachments_with_scores)} attachment(s), returning top {len(attachments)} most relevant"
                )
                if len(attachments) > 0:
                    log.debug(
                        f"Top attachment scores: {[round(score, 3) for _, score in attachments_with_scores[:MAX_ATTACHMENTS_IN_CONTEXT]]}"
                    )
            else:
                attachments = []
                log.info("📎 No attachments met the minimum relevance threshold")

        except Exception as att_error:
            log.warning(f"Could not retrieve attachments: {att_error}")
            attachments = []

        return attachments

    def generate_answer_stream(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
        language: str = "vi",
    ):
        """
        Generate answer using RAG approach with streaming response.
        Yields chunks of data as they become available.

        Args:
            query: User query
            conversation_id: Optional conversation ID
            conversation_history: Optional conversation history
            language: Response language - 'vi' for Vietnamese (default) or 'en' for English

        Yields:
            Dict with chunks of data (answer, metadata, etc.)
        """
        try:
            from src.services.gemini_service import (
                generate_response_stream as gemini_stream,
            )

            # Create new conversation if needed
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                self.conversations[conversation_id] = []
            elif conversation_id not in self.conversations:
                self.conversations[conversation_id] = []

            # Use conversation history if provided
            if conversation_history and not self.conversations[conversation_id]:
                for message in conversation_history:
                    if (
                        isinstance(message, dict)
                        and "role" in message
                        and "content" in message
                    ):
                        if message["role"] in ["user", "assistant"]:
                            self.conversations[conversation_id].append(
                                {"role": message["role"], "content": message["content"]}
                            )

            # Step 1: Send initial metadata
            yield {
                "type": "metadata",
                "conversation_id": conversation_id,
                "status": "processing",
            }

            # Step 2: Normalize query
            log.info(f"Original query: {query}")
            from src.services.gemini_service import normalize_question

            normalized_query = normalize_question(query)
            log.info(f"Normalized query: {normalized_query}")

            normalization_applied = (
                normalized_query != query
            ) and ENABLE_GEMINI_NORMALIZATION

            # Step 3: Get memory context
            memory_context = ""
            try:
                conv_context = self.memory_service.get_conversation_context(
                    conversation_id=conversation_id,
                    query=normalized_query,
                    include_memory_search=True,
                )
                if conv_context.has_long_term_memory or conv_context.recent_messages:
                    memory_context = self.memory_service.format_context_for_prompt(
                        conv_context
                    )
                    log.info(
                        f"🧠 Loaded memory context: {len(conv_context.memory_summaries)} summaries, {len(conv_context.recent_messages)} recent messages"
                    )
            except Exception as mem_error:
                log.warning(f"Could not load memory context: {mem_error}")

            # Step 4: Rewrite query with history
            current_history = self.conversations.get(conversation_id, [])
            rewritten_query = self._rewrite_query_with_history(
                normalized_query, current_history
            )

            # Step 5: Retrieve relevant chunks
            yield {"type": "status", "message": "Đang tìm kiếm tài liệu liên quan..."}

            relevant_chunks = self.retrieve_relevant_chunks(rewritten_query)
            context = self.create_context(relevant_chunks)

            # Get sources
            sources = []
            for chunk in relevant_chunks:
                source = chunk.get("source_file", "") or chunk.get("source", "")
                if source and source not in sources:
                    sources.append(source)

            # Build source references
            source_references = []
            for chunk in relevant_chunks:
                chunk_id = chunk.get("chunk_id", "")
                content = chunk.get("content", "")
                snippet = content[:200]
                if len(content) > 200:
                    last_space = snippet.rfind(" ")
                    if last_space > 150:
                        snippet = snippet[:last_space]
                    snippet += "..."

                relevance_score = (
                    chunk.get("rerank_score")
                    or chunk.get("combined_score")
                    or chunk.get("dense_score")
                    or 0.0
                )
                if relevance_score > 1.0:
                    relevance_score = min(1.0, (relevance_score + 10) / 20)
                elif relevance_score < 0:
                    relevance_score = max(0.0, (relevance_score + 10) / 20)

                source_ref = {
                    "chunk_id": str(chunk_id),
                    "filename": chunk.get("source_file", "") or chunk.get("source", ""),
                    "page_number": chunk.get("page_number"),
                    "heading": chunk.get("heading_text"),
                    "content_snippet": snippet,
                    "full_content": content,
                    "relevance_score": relevance_score,
                }
                source_references.append(source_ref)

            # Calculate confidence
            if relevant_chunks:
                scores = []
                for chunk in relevant_chunks:
                    score = (
                        chunk.get("rerank_score")
                        or chunk.get("combined_score")
                        or chunk.get("dense_score")
                        or 0.0
                    )
                    if score > 1.0:
                        score = min(1.0, (score + 10) / 20)
                    elif score < 0:
                        score = max(0.0, (score + 10) / 20)
                    scores.append(score)

                avg_score = sum(scores) / len(scores)
                confidence = min(max(avg_score, 0.0), 1.0)
            else:
                confidence = 0.0

            # Step 5.5: Get attachments (Before LLM)
            attachments = self._retrieve_attachments_for_context(query, relevant_chunks)

            # Inject attachment info into context
            if attachments:
                attachment_context = (
                    "\n\n*** TÀI LIỆU ĐÍNH KÈM CÓ SẴN (HỆ THỐNG ĐÃ TÌM THẤY) ***:\n"
                )
                if language == "en":
                    attachment_context = (
                        "\n\n*** AVAILABLE ATTACHMENTS (SYSTEM FOUND) ***:\n"
                    )

                for att in attachments:
                    attachment_context += f"- Tên file: {att['file_name']}\n  Mô tả: {att['description']}\n"

                attachment_context += "\n(Hãy nhắc người dùng tải xuống các tài liệu này ở phần đính kèm bên dưới / Please mention these attachments are available for download below)\n"
                context += attachment_context

            # Send sources before streaming answer

            yield {
                "type": "sources",
                "sources": sources,
                "source_references": source_references,
                "confidence": confidence,
            }

            # Step 6: Generate streaming answer
            yield {"type": "status", "message": "Đang tạo câu trả lời..."}

            system_prompt = self.create_system_prompt(language=language)
            user_prompt = self.create_user_prompt(
                query, context, memory_context, language=language
            )

            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Stream answer from Gemini
            full_answer = ""
            for text_chunk in gemini_stream(prompt=full_prompt):
                full_answer += text_chunk
                yield {"type": "answer_chunk", "content": text_chunk}

            # Add engagement prompt if needed
            if full_answer:
                # Store original length before adding engagement
                original_length = len(full_answer)
                enhanced_answer = self._add_engagement_prompt(
                    full_answer, query, language
                )

                # If engagement was added, stream the additional part
                if len(enhanced_answer) > original_length:
                    engagement_part = enhanced_answer[original_length:]
                    yield {"type": "answer_chunk", "content": engagement_part}
                    full_answer = enhanced_answer

                    full_answer = enhanced_answer

            # Step 7: (Attachments already retrieved in Step 5.5)
            # Just keeping the variable 'attachments'

            # Step 8: Detect charts
            chart_data = self._detect_chart_request(query, full_answer)

            # Step 9: Send final metadata
            yield {
                "type": "complete",
                "attachments": attachments,
                "chart_data": chart_data,
                "normalization_applied": normalization_applied,
                "original_query": query if normalization_applied else None,
                "normalized_query": normalized_query if normalization_applied else None,
            }

            # Step 10: Save to memory and database
            self.conversations[conversation_id].append(
                {"role": "user", "content": query}
            )
            self.conversations[conversation_id].append(
                {"role": "assistant", "content": full_answer}
            )

            if len(self.conversations[conversation_id]) > 10:
                self.conversations[conversation_id] = self.conversations[
                    conversation_id
                ][-10:]

            try:
                self.memory_service.add_exchange(
                    conversation_id=conversation_id,
                    user_message=query,
                    assistant_message=full_answer,
                    metadata={
                        "confidence": confidence,
                        "sources": sources,
                        "normalized_query": (
                            normalized_query if normalization_applied else None
                        ),
                    },
                )
            except Exception as mem_error:
                log.warning(f"Could not save to persistent memory: {mem_error}")

            try:
                self.db_service.save_conversation(
                    conversation_id=conversation_id,
                    user_message=query,
                    assistant_response=full_answer,
                    sources=sources,
                    confidence=confidence,
                    processing_time=0.0,
                )
            except Exception as save_error:
                log.warning(f"Could not save conversation to DB: {save_error}")

        except Exception as e:
            log.error(f"Error in streaming answer generation: {e}")
            yield {
                "type": "error",
                "message": "Xin lỗi, tôi không thể trả lời câu hỏi này. Vui lòng thử lại sau.",
            }

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history

        Args:
            conversation_id: Conversation ID

        Returns:
            List of conversation exchanges
        """
        return self.conversations.get(conversation_id, [])

    def check_system_health(self) -> Dict[str, Any]:
        """
        Check health of all RAG components

        Returns:
            Health status dictionary
        """
        health_status = {"overall_status": "healthy", "components": {}}

        # Check PostgreSQL + pgvector
        try:
            db_stats = self.db_service.get_database_stats()
            health_status["components"]["database"] = {
                "status": "healthy",
                "stats": db_stats,
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check Hybrid Retrieval Service (BM25 + pgvector)
        try:
            health_status["components"]["hybrid_retrieval"] = {
                "status": "healthy",
                "type": "BM25 + pgvector",
            }
        except Exception as e:
            health_status["components"]["hybrid_retrieval"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check embedding service
        try:
            embedding_dim = self.embedding_service.get_embedding_dimension()
            health_status["components"]["embedding"] = {
                "status": "healthy",
                "dimension": embedding_dim,
            }
        except Exception as e:
            health_status["components"]["embedding"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check ingestion service
        try:
            health_status["components"]["ingestion"] = {
                "status": "healthy",
                "type": "PDF file watcher",
            }
        except Exception as e:
            health_status["components"]["ingestion"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Determine overall status
        component_statuses = [
            comp.get("status", "unknown")
            for comp in health_status["components"].values()
        ]
        if any(status == "unhealthy" for status in component_statuses):
            health_status["overall_status"] = "unhealthy"
        elif any(status == "unknown" for status in component_statuses):
            health_status["overall_status"] = "degraded"

        return health_status

    def cleanup(self):
        """Cleanup resources - stop ingestion service"""
        try:
            if hasattr(self, "ingestion_service"):
                log.info("Stopping ingestion service...")
                self.ingestion_service.stop_watching()
                log.info("Ingestion service stopped successfully.")
        except Exception as e:
            log.error(f"Error during cleanup: {e}")
