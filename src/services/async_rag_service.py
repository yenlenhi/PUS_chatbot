"""
Async RAG Service - High-performance async version of the RAG pipeline.

Key optimizations:
1. All LLM calls are async (using async_gemini_service)
2. Normalization is DISABLED by default (saves 3-5s)
3. Retrieval runs efficiently with existing sync code wrapped in thread pool
4. True async streaming that doesn't block workers
"""

import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, AsyncGenerator

from src.utils.logger import log
from src.services.async_gemini_service import (
    generate_response_async,
    generate_response_stream_async,
    generate_vision_response_async,
    normalize_question_async,
)
from src.services.gemini_service import get_grounding_instruction
from config.settings import (
    TOP_K_RESULTS,
    LLM_PROVIDER,
    ENABLE_GEMINI_NORMALIZATION,
)

# Thread pool for CPU-bound operations (embeddings, reranking)
_executor = ThreadPoolExecutor(max_workers=4)


class AsyncRAGService:
    """
    Async wrapper for RAG operations.
    
    This service wraps the existing RAGService to provide truly async operations
    where the LLM calls don't block the event loop.
    """

    def __init__(self):
        """Initialize with lazy loading of the underlying RAG service."""
        self._rag_service = None
        
    @property
    def rag_service(self):
        """Lazy load the RAG service to avoid import issues."""
        if self._rag_service is None:
            from src.services.rag_service import RAGService
            self._rag_service = RAGService()
        return self._rag_service

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run a sync function in thread pool to avoid blocking."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor,
            lambda: func(*args, **kwargs)
        )

    async def generate_answer_async(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
        images: Optional[List[Any]] = None,
        language: str = "vi",
        skip_normalization: bool = False,  # Enable normalization by default
    ) -> Dict[str, Any]:
        """
        Async version of generate_answer with optimized pipeline.
        
        Key optimizations:
        - LLM calls are async (non-blocking)
        - Normalization is skipped by default (saves 3-5s)
        - Retrieval runs in thread pool
        """
        try:
            # Handle image-based queries using async Gemini Vision
            if images and len(images) > 0:
                return await self._generate_vision_answer_async(
                    query=query,
                    images=images,
                    conversation_id=conversation_id,
                    language=language,
                )

            # Create new conversation if needed
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                self.rag_service.conversations[conversation_id] = []
            elif conversation_id not in self.rag_service.conversations:
                self.rag_service.conversations[conversation_id] = []

            # Use conversation history if provided
            if conversation_history and not self.rag_service.conversations[conversation_id]:
                for message in conversation_history:
                    if isinstance(message, dict) and "role" in message and "content" in message:
                        if message["role"] in ["user", "assistant"]:
                            self.rag_service.conversations[conversation_id].append(
                                {"role": message["role"], "content": message["content"]}
                            )

            # OPTIMIZATION: Skip normalization by default
            normalization_applied = False
            normalized_query = query
            
            if not skip_normalization and ENABLE_GEMINI_NORMALIZATION:
                log.info(f"[ASYNC] Normalizing query: {query[:50]}...")
                normalized_query = await normalize_question_async(query)
                normalization_applied = normalized_query != query
                log.info(f"[ASYNC] Normalized query: {normalized_query[:50]}...")
            else:
                log.info("[ASYNC] Skipping normalization step for faster response")

            # Get memory context (run in thread pool as it's sync)
            memory_context = ""
            try:
                conv_context = await self._run_in_executor(
                    self.rag_service.memory_service.get_conversation_context,
                    conversation_id,
                    normalized_query,
                    True,  # include_memory_search
                )
                if conv_context.has_long_term_memory or conv_context.recent_messages:
                    memory_context = self.rag_service.memory_service.format_context_for_prompt(conv_context)
                    log.info(f"🧠 [ASYNC] Loaded memory context")
            except Exception as mem_error:
                log.warning(f"Could not load memory context: {mem_error}")

            # Retrieve relevant chunks (CPU-bound, run in thread pool)
            log.info("[ASYNC] Running retrieval in thread pool...")
            relevant_chunks = await self._run_in_executor(
                self.rag_service.retrieve_relevant_chunks,
                normalized_query,
            )

            # Create context and sources
            context = self.rag_service.create_context(relevant_chunks)
            
            sources = []
            for chunk in relevant_chunks:
                source = chunk.get("source_file", "") or chunk.get("source", "")
                if source and source not in sources:
                    sources.append(source)

            # Build source references
            source_references = self._build_source_references(relevant_chunks)

            # Get attachments
            attachments = await self._run_in_executor(
                self.rag_service._retrieve_attachments_for_context,
                query,
                relevant_chunks,
            )
            
            if attachments:
                attachment_context = "\n\n*** TÀI LIỆU ĐÍNH KÈM CÓ SẴN ***:\n"
                for att in attachments:
                    attachment_context += f"- {att['file_name']}: {att['description']}\n"
                context += attachment_context

            # Create prompts
            system_prompt = self.rag_service.create_system_prompt(language=language)
            user_prompt = self.rag_service.create_user_prompt(
                query, context, memory_context, language=language
            )
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Generate answer using ASYNC Gemini call (the key optimization!)
            log.info("[ASYNC] Calling Gemini API asynchronously...")
            answer = await generate_response_async(prompt=full_prompt)

            # Calculate confidence
            confidence = self._calculate_confidence(relevant_chunks)

            # Handle empty response
            if not answer or not answer.strip():
                log.error("LLM returned empty response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau."
                confidence = 0.0
            else:
                # Add engagement prompt
                answer = self.rag_service._add_engagement_prompt(answer, query, language)

            # Update conversation history
            self.rag_service.conversations[conversation_id].append({"role": "user", "content": query})
            self.rag_service.conversations[conversation_id].append({"role": "assistant", "content": answer})

            # Limit conversation history
            if len(self.rag_service.conversations[conversation_id]) > 10:
                self.rag_service.conversations[conversation_id] = self.rag_service.conversations[conversation_id][-10:]

            # Save to memory and DB (async background tasks)
            asyncio.create_task(self._save_conversation_async(
                conversation_id, query, answer, sources, confidence, normalization_applied, normalized_query
            ))

            # Detect chart data
            chart_data = self.rag_service._detect_chart_request(query, answer)

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
                "chart_data": chart_data,
                "images": [],
            }

        except Exception as e:
            log.error(f"[ASYNC] Error generating answer: {e}")
            return {
                "answer": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
                "sources": [],
                "source_references": [],
                "attachments": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "chart_data": [],
                "images": [],
            }

    async def generate_answer_stream_async(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
        language: str = "vi",
        skip_normalization: bool = False,  # Enable normalization by default
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Async streaming version of generate_answer.
        Yields chunks as they arrive from the LLM.
        """
        try:
            # Create conversation ID
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                self.rag_service.conversations[conversation_id] = []
            elif conversation_id not in self.rag_service.conversations:
                self.rag_service.conversations[conversation_id] = []

            # Initial metadata
            yield {
                "type": "metadata",
                "conversation_id": conversation_id,
                "status": "processing",
            }

            # Skip normalization for faster response
            normalized_query = query
            normalization_applied = False
            
            log.info(f"[DEBUG] skip_normalization={skip_normalization}, ENABLE_GEMINI_NORMALIZATION={ENABLE_GEMINI_NORMALIZATION}")
            
            if not skip_normalization and ENABLE_GEMINI_NORMALIZATION:
                log.info(f"[ASYNC STREAM] Normalizing query: {query[:50]}...")
                normalized_query = await normalize_question_async(query)
                normalization_applied = normalized_query != query
                log.info(f"[ASYNC STREAM] Normalized: '{query[:30]}' -> '{normalized_query[:30]}'")
            else:
                log.info(f"[ASYNC STREAM] Skipping normalization (skip={skip_normalization}, enabled={ENABLE_GEMINI_NORMALIZATION})")

            # Get memory context
            memory_context = ""
            try:
                conv_context = await self._run_in_executor(
                    self.rag_service.memory_service.get_conversation_context,
                    conversation_id,
                    normalized_query,
                    True,
                )
                if conv_context.has_long_term_memory or conv_context.recent_messages:
                    memory_context = self.rag_service.memory_service.format_context_for_prompt(conv_context)
            except Exception as mem_error:
                log.warning(f"Memory context error: {mem_error}")

            # Retrieval (thread pool)
            yield {"type": "status", "message": "Đang tìm kiếm tài liệu..."}
            
            relevant_chunks = await self._run_in_executor(
                self.rag_service.retrieve_relevant_chunks,
                normalized_query,
            )

            context = self.rag_service.create_context(relevant_chunks)
            
            # Get sources
            sources = []
            for chunk in relevant_chunks:
                source = chunk.get("source_file", "") or chunk.get("source", "")
                if source and source not in sources:
                    sources.append(source)

            source_references = self._build_source_references(relevant_chunks)
            confidence = self._calculate_confidence(relevant_chunks)

            # Get attachments
            attachments = await self._run_in_executor(
                self.rag_service._retrieve_attachments_for_context,
                query,
                relevant_chunks,
            )

            # Inject attachments into context for the LLM
            if attachments:
                attachment_context = "\n\n*** TÀI LIỆU ĐÍNH KÈM CÓ SẴN (HỆ THỐNG ĐÃ TÌM THẤY) ***:\n"
                if language == 'en':
                    attachment_context = "\n\n*** AVAILABLE ATTACHMENTS (SYSTEM FOUND) ***:\n"
                
                for att in attachments:
                    attachment_context += f"- Tên file: {att['file_name']}\n  Mô tả: {att['description']}\n"
                
                attachment_context += "\n(Hãy nhắc người dùng xem và tải xuống các tài liệu này ở phần đính kèm bên dưới)\n"
                context += attachment_context

            # Send sources
            yield {
                "type": "sources",
                "sources": sources,
                "source_references": source_references,
                "confidence": confidence,
            }

            # Generate streaming answer
            yield {"type": "status", "message": "Đang tạo câu trả lời..."}

            system_prompt = self.rag_service.create_system_prompt(language=language)
            user_prompt = self.rag_service.create_user_prompt(
                query, context, memory_context, language=language
            )
            
            # NEW: Add grounding instruction for real-time queries
            grounding_instruction = get_grounding_instruction(query, language)
            if grounding_instruction:
                log.info("[ASYNC STREAM] Adding grounding instruction to prompt")
                full_prompt = f"{grounding_instruction}\n\n{system_prompt}\n\n{user_prompt}"
            else:
                full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # TRUE ASYNC STREAMING from Gemini
            full_answer = ""
            async for text_chunk in generate_response_stream_async(prompt=full_prompt):
                full_answer += text_chunk
                yield {"type": "answer_chunk", "content": text_chunk}

            # Add engagement prompt
            if full_answer:
                original_length = len(full_answer)
                enhanced_answer = self.rag_service._add_engagement_prompt(full_answer, query, language)
                if len(enhanced_answer) > original_length:
                    engagement_part = enhanced_answer[original_length:]
                    yield {"type": "answer_chunk", "content": engagement_part}
                    full_answer = enhanced_answer

            # Detect charts
            chart_data = self.rag_service._detect_chart_request(query, full_answer)

            # Final metadata
            yield {
                "type": "complete",
                "attachments": attachments,
                "chart_data": chart_data,
                "normalization_applied": normalization_applied,
                "original_query": query if normalization_applied else None,
                "normalized_query": normalized_query if normalization_applied else None,
            }

            # Save conversation (background)
            asyncio.create_task(self._save_conversation_async(
                conversation_id, query, full_answer, sources, confidence, normalization_applied, normalized_query
            ))

            # Update in-memory history
            self.rag_service.conversations[conversation_id].append({"role": "user", "content": query})
            self.rag_service.conversations[conversation_id].append({"role": "assistant", "content": full_answer})

        except Exception as e:
            log.error(f"[ASYNC STREAM] Error: {e}")
            yield {
                "type": "error",
                "message": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
            }

    async def _generate_vision_answer_async(
        self,
        query: str,
        images: List[Any],
        conversation_id: Optional[str] = None,
        language: str = "vi",
    ) -> Dict[str, Any]:
        """Async vision answer generation."""
        try:
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            # Build vision prompt
            if language == "en":
                vision_prompt = f"""You are an AI assistant for People's Security University.
Analyze the image(s) and answer: {query if query else "Describe this image."}
Respond in ENGLISH."""
            else:
                vision_prompt = f"""Bạn là trợ lý AI của Trường Đại học An ninh Nhân dân.
Phân tích hình ảnh và trả lời: {query if query else "Mô tả hình ảnh này."}
Trả lời bằng tiếng Việt."""

            # Prepare images
            image_parts = []
            for img in images:
                try:
                    base64_data = img.base64
                    if "," in base64_data:
                        base64_data = base64_data.split(",")[1]
                    mime_type = getattr(img, "mime_type", "image/jpeg") or "image/jpeg"
                    image_parts.append({"mime_type": mime_type, "data": base64_data})
                except Exception as img_error:
                    log.warning(f"Image processing error: {img_error}")

            if not image_parts:
                return {
                    "answer": "Không thể xử lý hình ảnh. Vui lòng thử lại.",
                    "sources": [],
                    "source_references": [],
                    "confidence": 0.0,
                    "conversation_id": conversation_id,
                }

            # Async vision call
            answer = await generate_vision_response_async(
                prompt=vision_prompt,
                images=image_parts,
            )

            if not answer:
                answer = "Xin lỗi, tôi không thể phân tích hình ảnh này."

            return {
                "answer": answer,
                "sources": [],
                "source_references": [],
                "confidence": 0.85,
                "conversation_id": conversation_id,
                "chart_data": [],
                "images": [],
            }

        except Exception as e:
            log.error(f"[ASYNC VISION] Error: {e}")
            return {
                "answer": f"Lỗi phân tích hình ảnh: {str(e)}",
                "sources": [],
                "source_references": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4()),
            }

    def _build_source_references(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build source references from chunks."""
        source_references = []
        for chunk in chunks:
            content = chunk.get("content", "")
            snippet = content[:200] + "..." if len(content) > 200 else content
            
            relevance_score = (
                chunk.get("rerank_score") or
                chunk.get("combined_score") or
                chunk.get("dense_score") or
                0.0
            )
            if relevance_score > 1.0:
                relevance_score = min(1.0, (relevance_score + 10) / 20)
            elif relevance_score < 0:
                relevance_score = max(0.0, (relevance_score + 10) / 20)

            source_references.append({
                "chunk_id": str(chunk.get("chunk_id", "")),
                "filename": chunk.get("source_file", "") or chunk.get("source", ""),
                "page_number": chunk.get("page_number"),
                "heading": chunk.get("heading_text"),
                "content_snippet": snippet,
                "full_content": content,
                "relevance_score": relevance_score,
            })
        return source_references

    def _calculate_confidence(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score from chunk relevance."""
        if not chunks:
            return 0.0
        
        scores = []
        for chunk in chunks:
            score = (
                chunk.get("rerank_score") or
                chunk.get("combined_score") or
                chunk.get("dense_score") or
                0.0
            )
            if score > 1.0:
                score = min(1.0, (score + 10) / 20)
            elif score < 0:
                score = max(0.0, (score + 10) / 20)
            scores.append(score)
        
        return min(max(sum(scores) / len(scores), 0.0), 1.0)

    async def _save_conversation_async(
        self,
        conversation_id: str,
        query: str,
        answer: str,
        sources: List[str],
        confidence: float,
        normalization_applied: bool,
        normalized_query: str,
    ):
        """Save conversation to memory and database (async background task)."""
        try:
            # Save to memory service
            await self._run_in_executor(
                self.rag_service.memory_service.add_exchange,
                conversation_id,
                query,
                answer,
                {
                    "confidence": confidence,
                    "sources": sources,
                    "normalized_query": normalized_query if normalization_applied else None,
                },
            )
        except Exception as e:
            log.warning(f"[ASYNC] Could not save to memory: {e}")

        try:
            # Save to database
            await self._run_in_executor(
                self.rag_service.db_service.save_conversation,
                conversation_id,
                query,
                answer,
                sources,
                confidence,
                0.0,
            )
        except Exception as e:
            log.warning(f"[ASYNC] Could not save to DB: {e}")


# Singleton instance
_async_rag_service: Optional[AsyncRAGService] = None


def get_async_rag_service() -> AsyncRAGService:
    """Get or create the async RAG service singleton."""
    global _async_rag_service
    if _async_rag_service is None:
        _async_rag_service = AsyncRAGService()
    return _async_rag_service
