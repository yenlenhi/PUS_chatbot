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
from typing import List, Dict, Any, Optional, AsyncGenerator, Tuple

from src.utils.logger import log
from src.services.async_gemini_service import (
    generate_response_async,
    generate_response_stream_async,
    generate_vision_response_async,
    normalize_question_async,
)
from src.services.gemini_service import get_grounding_instruction
from src.services.admission_scope_service import AdmissionScopeService
from config.settings import (
    ENABLE_GEMINI_NORMALIZATION,
    ADMISSION_ONLY_MODE,
    STRICT_MODE,
    CONFIDENCE_THRESHOLD,
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
        self.scope_service = AdmissionScopeService()
        # Short-TTL retrieval cache: skips embedding+search+rerank for repeated queries.
        # Key: sha256(normalized_query), Value: (timestamp, chunks)
        self._retrieval_cache: dict = {}
        self._retrieval_cache_ttl: int = 300  # 5 minutes
        self._retrieval_cache_max: int = 200

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
        return await loop.run_in_executor(_executor, lambda: func(*args, **kwargs))

    async def _cached_retrieve_chunks(
        self, normalized_query: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks with a short-TTL in-memory cache.

        For repeated identical queries (common in chatbot environments) this
        skips embedding + pgvector search + BM25 + cross-encoder entirely,
        saving 1-3 seconds per request.

        Cache key: SHA-256 of lower-cased query (no chunk-ID dependency).
        TTL: 5 minutes.  Max size: 200 entries (evict oldest on overflow).
        """
        import hashlib as _hl
        import time as _time

        cache_key = _hl.sha256(normalized_query.lower().encode()).hexdigest()
        now = _time.monotonic()

        # Cache hit
        if cache_key in self._retrieval_cache:
            ts, chunks = self._retrieval_cache[cache_key]
            if now - ts < self._retrieval_cache_ttl:
                log.info(
                    f"⚡ [RETRIEVAL CACHE] Hit — skipping search+rerank for '{normalized_query[:50]}'"
                )
                return chunks
            else:
                del self._retrieval_cache[cache_key]  # expired

        # Cache miss — run retrieval
        log.info("[ASYNC] Running retrieval in thread pool...")
        chunks = await self._run_in_executor(
            self.rag_service.retrieve_relevant_chunks,
            normalized_query,
        )

        # Evict oldest entry if full
        if len(self._retrieval_cache) >= self._retrieval_cache_max:
            oldest_key = next(iter(self._retrieval_cache))
            del self._retrieval_cache[oldest_key]

        self._retrieval_cache[cache_key] = (_time.monotonic(), chunks)
        return chunks

    def _build_policy_payload(
        self,
        policy: str,
        conversation_id: str,
        language: str,
        *,
        source_references: Optional[List[Dict[str, Any]]] = None,
        sources: Optional[List[str]] = None,
        confidence: float = 0.0,
        normalization_applied: bool = False,
        original_query: Optional[str] = None,
        normalized_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "answer": self.scope_service.build_policy_answer(policy, language),
            "sources": sources or [],
            "source_references": source_references or [],
            "attachments": [],
            "confidence": confidence,
            "conversation_id": conversation_id,
            "normalization_applied": normalization_applied,
            "original_query": original_query if normalization_applied else None,
            "normalized_query": normalized_query if normalization_applied else None,
            "chart_data": [],
            "images": [],
        }

    def _update_conversation_history(
        self, conversation_id: str, query: str, answer: str
    ) -> None:
        self.rag_service.conversations.setdefault(conversation_id, [])
        self.rag_service.conversations[conversation_id].append(
            {"role": "user", "content": query}
        )
        self.rag_service.conversations[conversation_id].append(
            {"role": "assistant", "content": answer}
        )

        if len(self.rag_service.conversations[conversation_id]) > 10:
            self.rag_service.conversations[conversation_id] = (
                self.rag_service.conversations[conversation_id][-10:]
            )

    def _build_sources(self, relevant_chunks: List[Dict[str, Any]]) -> List[str]:
        sources: List[str] = []
        for chunk in relevant_chunks:
            source = chunk.get("source_file", "") or chunk.get("source", "")
            if source and source not in sources:
                sources.append(source)
        return sources

    def _build_generation_prompt(
        self, query: str, language: str, system_prompt: str, user_prompt: str
    ) -> Tuple[str, bool]:
        grounding_instruction = get_grounding_instruction(query, language)
        if grounding_instruction:
            full_prompt = f"{grounding_instruction}\n\n{system_prompt}\n\n{user_prompt}"
            return full_prompt, True

        return f"{system_prompt}\n\n{user_prompt}", False

    def _should_fetch_attachments(
        self, query: str, relevant_chunks: List[Dict[str, Any]]
    ) -> bool:
        query_lower = (query or "").lower()
        attachment_keywords = (
            "hồ sơ",
            "ho so",
            "sơ tuyển",
            "so tuyen",
            "đăng ký",
            "dang ky",
            "biểu mẫu",
            "bieu mau",
            "mẫu",
            "mau",
            "đơn",
            "don",
            "phiếu",
            "phieu",
            "tài liệu",
            "tai lieu",
            "file",
            "form",
            "pdf",
            "download",
            "tải xuống",
            "tai xuong",
            "attachment",
            "document",
            "documents",
            "template",
        )
        if any(keyword in query_lower for keyword in attachment_keywords):
            return True

        chunk_keywords = (
            "hồ sơ",
            "ho so",
            "mẫu",
            "mau",
            "đơn",
            "don",
            "phiếu",
            "phieu",
            "tài liệu",
            "tai lieu",
            "biểu mẫu",
            "bieu mau",
            "download",
            "tải xuống",
            "tai xuong",
            "file đính kèm",
            "tep dinh kem",
            "form",
            "document",
            "attachment",
        )
        for chunk in relevant_chunks[:3]:
            chunk_text = " ".join(
                str(chunk.get(field, "") or "")
                for field in ("content", "text", "title", "source", "source_file")
            ).lower()
            if any(keyword in chunk_text for keyword in chunk_keywords):
                return True

        return False

    async def _maybe_get_attachments(
        self,
        query: str,
        relevant_chunks: List[Dict[str, Any]],
        *,
        stream: bool = False,
    ) -> List[Dict[str, Any]]:
        if not relevant_chunks:
            return []

        if not self._should_fetch_attachments(query, relevant_chunks):
            log.info(
                "[ASYNC STREAM] Skip attachment retrieval (no attachment intent detected)"
                if stream
                else "[ASYNC] Skip attachment retrieval (no attachment intent detected)"
            )
            return []

        return await self._run_in_executor(
            self.rag_service._retrieve_attachments_for_context,
            query,
            relevant_chunks,
        )

    def _classify_query(self, query: str, conv_turn_count: int) -> dict:
        """
        Lightweight heuristic query router — zero latency, no LLM call.

        Decides which preprocessing steps are actually needed so we don't
        run all three stages blindly for every query.

        Rules:
        - needs_normalization : query has Vietnamese abbreviations or is very
          short/unclear  (and ENABLE_GEMINI_NORMALIZATION is on)
        - needs_rewrite       : query contains reference pronouns that depend
          on prior turns  (only relevant when conv_turn_count > 0)
        - needs_memory        : conversation is long AND query explicitly
          references something said earlier  (conv_turn_count > 4 as minimum)

        Returns:
            dict with bool flags: needs_normalization, needs_rewrite, needs_memory
        """
        import re

        query_lower = query.lower().strip()
        query_tokens = query_lower.split()

        # ── needs_normalization ─────────────────────────────────────────────
        # Common Vietnamese admission abbreviations / shorthand
        abbrev_patterns = [
            r"\bđh\b",
            r"\bthpt\b",
            r"\bđhsp\b",
            r"\bhhv\b",
            r"\bhvannd\b",
            r"\bđhan\b",
            r"\bbtan\b",
            r"\bdtts\b",
            r"\bnv\d?\b",
            r"\bkhtn\b",
            r"\bkhxh\b",
            r"\bktqt\b",
            r"\btccn\b",
            r"\bcand\b",
            r"\bcsa\b",
        ]
        has_abbrev = any(re.search(p, query_lower) for p in abbrev_patterns)
        # Very short unclear query (< 4 words, not a greeting)
        is_too_short = len(query_tokens) < 4 and not any(
            g in query_lower for g in ["xin chào", "hello", "hi", "chào"]
        )
        needs_normalization = (
            has_abbrev or is_too_short
        ) and ENABLE_GEMINI_NORMALIZATION

        # ── needs_rewrite ───────────────────────────────────────────────────
        # Query uses reference expressions that only make sense with prior context
        reference_patterns = [
            r"\b(đó|kia|vậy|nêu trên|như vậy|đã nêu)\b",
            r"ngành (này|đó|kia|trên|vừa|đã (nói|đề cập))",
            r"trường (này|đó|kia)",
            r"^(còn|thế còn|vậy thì|vậy còn|thế thì)\b",
            r"^(ngoài ra|bên cạnh đó)",
            r"\btại sao\b.+\b(vậy|thế)\b",
            r"(môn học|điểm chuẩn|học phí|chỉ tiêu).*(đó|kia|trên)",
        ]
        has_reference = any(re.search(p, query_lower) for p in reference_patterns)
        needs_rewrite = has_reference and conv_turn_count > 0

        # ── needs_memory ────────────────────────────────────────────────────
        # Only load long-term memory for older conversations that explicitly
        # refer back to earlier parts of the dialogue
        memory_back_ref_patterns = [
            r"\b(trước đó|hồi nãy|lúc nãy|vừa rồi)\b",
            r"\b(đã hỏi|đã nói|đã đề cập|như đã)\b",
            r"\b(nhớ lại|nhắc lại|giải thích lại|nói lại)\b",
        ]
        has_memory_ref = any(
            re.search(p, query_lower) for p in memory_back_ref_patterns
        )
        needs_memory = conv_turn_count > 4 and (has_memory_ref or has_reference)

        log.info(
            f"[ROUTER] normalize={needs_normalization} rewrite={needs_rewrite} "
            f"memory={needs_memory} | turns={conv_turn_count} | '{query[:60]}'"
        )
        return {
            "needs_normalization": needs_normalization,
            "needs_rewrite": needs_rewrite,
            "needs_memory": needs_memory,
        }

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
            # Create new conversation if needed
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                self.rag_service.conversations[conversation_id] = []
            elif conversation_id not in self.rag_service.conversations:
                self.rag_service.conversations[conversation_id] = []

            # Use conversation history if provided
            if (
                conversation_history
                and not self.rag_service.conversations[conversation_id]
            ):
                for message in conversation_history:
                    if (
                        isinstance(message, dict)
                        and "role" in message
                        and "content" in message
                    ):
                        if message["role"] in ["user", "assistant"]:
                            self.rag_service.conversations[conversation_id].append(
                                {"role": message["role"], "content": message["content"]}
                            )

            # ── Smart Query Router ──────────────────────────────────────────
            if ADMISSION_ONLY_MODE:
                scope_decision = self.scope_service.classify(
                    query, has_images=bool(images)
                )
                if scope_decision.scope != "admission":
                    log.info(
                        f"[POLICY] Short-circuit query as {scope_decision.scope}: {scope_decision.reason}"
                    )
                    response = self._build_policy_payload(
                        scope_decision.scope,
                        conversation_id,
                        language,
                    )
                    self._update_conversation_history(
                        conversation_id, query or "[image]", response["answer"]
                    )
                    asyncio.create_task(
                        self._save_conversation_async(
                            conversation_id,
                            query or "[image]",
                            response["answer"],
                            response["sources"],
                            response["confidence"],
                            False,
                            query or "",
                        )
                    )
                    return response

            if images and len(images) > 0:
                vision_response = await self._generate_vision_answer_async(
                    query=query,
                    images=images,
                    conversation_id=conversation_id,
                    language=language,
                )
                self._update_conversation_history(
                    conversation_id, query or "[image]", vision_response["answer"]
                )
                asyncio.create_task(
                    self._save_conversation_async(
                        conversation_id,
                        query or "[image]",
                        vision_response["answer"],
                        vision_response.get("sources", []),
                        vision_response.get("confidence", 0.0),
                        False,
                        query or "",
                    )
                )
                return vision_response

            normalization_applied = False
            normalized_query = query
            memory_context = ""
            current_history = self.rag_service.conversations.get(conversation_id, [])
            conv_turn_count = len(current_history)

            intent = self._classify_query(query, conv_turn_count)

            # Step 1: Normalize — only for queries with abbreviations / typos
            if not skip_normalization and intent["needs_normalization"]:
                log.info("[ASYNC] Normalizing query (abbreviations/typos detected)...")
                normalized_query = await normalize_question_async(query)
                normalization_applied = normalized_query != query
                log.info(
                    f"[ASYNC] Normalized: '{query[:40]}' -> '{normalized_query[:40]}'"
                )
            else:
                log.info("[ASYNC] Skip normalization (query is clear)")

            # Step 2: Rewrite — only for follow-up queries referencing prior turns
            if intent["needs_rewrite"] and current_history:
                try:
                    formatted_history = "\n".join(
                        [
                            f"{msg['role']}: {msg['content']}"
                            for msg in current_history[-6:]
                        ]
                    )
                    rewrite_prompt = f"""Dựa vào lịch sử trò chuyện sau đây, hãy viết lại câu hỏi cuối cùng của người dùng thành một câu hỏi độc lập, đầy đủ ngữ cảnh để có thể dùng cho việc tìm kiếm thông tin.

### Lịch sử trò chuyện:
{formatted_history}

### Câu hỏi cuối cùng của người dùng:
{normalized_query}

### Câu hỏi độc lập, đầy đủ ngữ cảnh:"""
                    rewritten_query = await generate_response_async(
                        prompt=rewrite_prompt
                    )
                    if (
                        rewritten_query
                        and rewritten_query.strip()
                        and rewritten_query.strip() != normalized_query
                    ):
                        log.info(
                            f"[ASYNC] Rewritten: '{normalized_query[:40]}' -> '{rewritten_query.strip()[:60]}'"
                        )
                        normalized_query = rewritten_query.strip()
                except Exception as rw_err:
                    log.warning(f"[ASYNC] Query rewrite failed: {rw_err}")
            else:
                log.info("[ASYNC] Skip rewrite (query is self-contained)")

            # Step 3: Memory — only for long conversations with explicit back-references
            if intent["needs_memory"]:
                try:
                    conv_context = await self._run_in_executor(
                        self.rag_service.memory_service.get_conversation_context,
                        conversation_id,
                        normalized_query,
                        True,
                    )
                    if (
                        conv_context.has_long_term_memory
                        or conv_context.recent_messages
                    ):
                        memory_context = (
                            self.rag_service.memory_service.format_context_for_prompt(
                                conv_context
                            )
                        )
                        log.info("🧠 [ASYNC] Loaded memory context")
                except Exception as mem_error:
                    log.warning(f"Could not load memory context: {mem_error}")
            else:
                log.info(
                    f"[ASYNC] Skip memory retrieval (turns={conv_turn_count}, no back-reference)"
                )

            # Retrieve relevant chunks (with short-TTL cache)
            relevant_chunks = await self._cached_retrieve_chunks(normalized_query)

            # Create context and sources
            context = self.rag_service.create_context(relevant_chunks)
            sources = self._build_sources(relevant_chunks)

            # Build source references
            source_references = self._build_source_references(relevant_chunks)
            confidence = self._calculate_confidence(relevant_chunks)

            if STRICT_MODE and confidence < CONFIDENCE_THRESHOLD:
                log.info(
                    f"[POLICY] Insufficient evidence, confidence={confidence:.3f} threshold={CONFIDENCE_THRESHOLD:.3f}"
                )
                response = self._build_policy_payload(
                    "insufficient_evidence",
                    conversation_id,
                    language,
                    source_references=source_references,
                    sources=sources,
                    confidence=confidence,
                    normalization_applied=normalization_applied,
                    original_query=query,
                    normalized_query=normalized_query,
                )
                self._update_conversation_history(conversation_id, query, response["answer"])
                asyncio.create_task(
                    self._save_conversation_async(
                        conversation_id,
                        query,
                        response["answer"],
                        sources,
                        confidence,
                        normalization_applied,
                        normalized_query,
                    )
                )
                return response

            # Get attachments
            attachments = await self._maybe_get_attachments(query, relevant_chunks)

            if attachments:
                attachment_context = "\n\n*** TÀI LIỆU ĐÍNH KÈM CÓ SẴN ***:\n"
                for att in attachments:
                    attachment_context += (
                        f"- {att['file_name']}: {att['description']}\n"
                    )
                context += attachment_context

            # Create prompts
            system_prompt = self.rag_service.create_system_prompt(language=language)
            user_prompt = self.rag_service.create_user_prompt(
                query, context, memory_context, language=language
            )

            # Grounding: only for real-time queries (lãnh đạo, sự kiện, tin tức...)
            full_prompt, needs_grounding = self._build_generation_prompt(
                query, language, system_prompt, user_prompt
            )

            # Generate answer using ASYNC Gemini call
            log.info(f"[ASYNC] Calling Gemini API (grounding={needs_grounding})...")
            answer = await generate_response_async(
                prompt=full_prompt, enable_grounding=needs_grounding
            )

            # Handle empty response
            if not answer or not answer.strip():
                log.error("LLM returned empty response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau."
                confidence = 0.0
            else:
                # Add engagement prompt
                answer = self.rag_service._add_engagement_prompt(
                    answer, query, language
                )

            self._update_conversation_history(conversation_id, query, answer)

            # Save to memory and DB (async background tasks)
            asyncio.create_task(
                self._save_conversation_async(
                    conversation_id,
                    query,
                    answer,
                    sources,
                    confidence,
                    normalization_applied,
                    normalized_query,
                )
            )

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

            # Populate conversation history from request if provided (fixes stateless problem)
            if (
                conversation_history
                and not self.rag_service.conversations[conversation_id]
            ):
                for message in conversation_history:
                    if (
                        isinstance(message, dict)
                        and "role" in message
                        and "content" in message
                    ):
                        if message["role"] in ["user", "assistant"]:
                            self.rag_service.conversations[conversation_id].append(
                                {"role": message["role"], "content": message["content"]}
                            )
                log.info(
                    f"[ASYNC STREAM] Loaded {len(self.rag_service.conversations[conversation_id])} history messages"
                )

            # Initial metadata
            yield {
                "type": "metadata",
                "conversation_id": conversation_id,
                "status": "processing",
            }

            # ── Smart Query Router ──────────────────────────────────────────
            if ADMISSION_ONLY_MODE:
                scope_decision = self.scope_service.classify(query)
                if scope_decision.scope != "admission":
                    log.info(
                        f"[POLICY STREAM] Short-circuit query as {scope_decision.scope}: {scope_decision.reason}"
                    )
                    answer = self.scope_service.build_policy_answer(
                        scope_decision.scope, language
                    )
                    yield {
                        "type": "sources",
                        "sources": [],
                        "source_references": [],
                        "confidence": 0.0,
                    }
                    yield {"type": "answer_chunk", "content": answer}
                    yield {
                        "type": "complete",
                        "attachments": [],
                        "chart_data": [],
                        "images": [],
                        "normalization_applied": False,
                        "original_query": None,
                        "normalized_query": None,
                    }
                    asyncio.create_task(
                        self._save_conversation_async(
                            conversation_id,
                            query or "[image]",
                            answer,
                            [],
                            0.0,
                            False,
                            query or "",
                        )
                    )
                    self._update_conversation_history(
                        conversation_id, query or "[image]", answer
                    )
                    return

            normalized_query = query
            normalization_applied = False
            memory_context = ""
            current_history = self.rag_service.conversations.get(conversation_id, [])
            conv_turn_count = len(current_history)

            intent = self._classify_query(query, conv_turn_count)

            # Step 1: Normalize — only for abbreviations / unclear short queries
            if not skip_normalization and intent["needs_normalization"]:
                log.info("[ASYNC STREAM] Normalizing query (abbreviations/typos)...")
                normalized_query = await normalize_question_async(query)
                normalization_applied = normalized_query != query
                log.info(
                    f"[ASYNC STREAM] Normalized: '{query[:40]}' -> '{normalized_query[:40]}'"
                )
            else:
                log.info("[ASYNC STREAM] Skip normalization (query is clear)")

            # Step 2: Rewrite — only for follow-up queries referencing prior turns
            if intent["needs_rewrite"] and current_history:
                try:
                    formatted_history = "\n".join(
                        [
                            f"{msg['role']}: {msg['content']}"
                            for msg in current_history[-6:]
                        ]
                    )
                    rewrite_prompt = f"""Dựa vào lịch sử trò chuyện sau đây, hãy viết lại câu hỏi cuối cùng của người dùng thành một câu hỏi độc lập, đầy đủ ngữ cảnh để có thể dùng cho việc tìm kiếm thông tin.

### Lịch sử trò chuyện:
{formatted_history}

### Câu hỏi cuối cùng của người dùng:
{normalized_query}

### Câu hỏi độc lập, đầy đủ ngữ cảnh:"""
                    rewritten_query = await generate_response_async(
                        prompt=rewrite_prompt
                    )
                    if (
                        rewritten_query
                        and rewritten_query.strip()
                        and rewritten_query.strip() != normalized_query
                    ):
                        log.info(
                            f"[ASYNC STREAM] Rewritten: '{normalized_query[:40]}' -> '{rewritten_query.strip()[:60]}'"
                        )
                        normalized_query = rewritten_query.strip()
                except Exception as rw_err:
                    log.warning(f"[ASYNC STREAM] Query rewrite failed: {rw_err}")
            else:
                log.info("[ASYNC STREAM] Skip rewrite (query is self-contained)")

            # Step 3: Memory — only for long conversations with explicit back-references
            if intent["needs_memory"]:
                try:
                    conv_context = await self._run_in_executor(
                        self.rag_service.memory_service.get_conversation_context,
                        conversation_id,
                        normalized_query,
                        True,
                    )
                    if (
                        conv_context.has_long_term_memory
                        or conv_context.recent_messages
                    ):
                        memory_context = (
                            self.rag_service.memory_service.format_context_for_prompt(
                                conv_context
                            )
                        )
                        log.info("🧠 [ASYNC STREAM] Loaded memory context")
                except Exception as mem_error:
                    log.warning(f"Memory context error: {mem_error}")
            else:
                log.info(
                    f"[ASYNC STREAM] Skip memory retrieval (turns={conv_turn_count}, no back-reference)"
                )

            # Retrieval (thread pool, with short-TTL cache)
            yield {"type": "status", "message": "Đang tìm kiếm tài liệu..."}

            relevant_chunks = await self._cached_retrieve_chunks(normalized_query)

            context = self.rag_service.create_context(relevant_chunks)

            # Get sources
            sources = self._build_sources(relevant_chunks)

            source_references = self._build_source_references(relevant_chunks)
            confidence = self._calculate_confidence(relevant_chunks)

            if STRICT_MODE and confidence < CONFIDENCE_THRESHOLD:
                answer = self.scope_service.build_policy_answer(
                    "insufficient_evidence", language
                )
                yield {
                    "type": "sources",
                    "sources": sources,
                    "source_references": source_references,
                    "confidence": confidence,
                }
                yield {"type": "answer_chunk", "content": answer}
                yield {
                    "type": "complete",
                    "attachments": [],
                    "chart_data": [],
                    "images": [],
                    "normalization_applied": normalization_applied,
                    "original_query": query if normalization_applied else None,
                    "normalized_query": normalized_query if normalization_applied else None,
                }
                asyncio.create_task(
                    self._save_conversation_async(
                        conversation_id,
                        query,
                        answer,
                        sources,
                        confidence,
                        normalization_applied,
                        normalized_query,
                    )
                )
                self._update_conversation_history(conversation_id, query, answer)
                return

            # Get attachments
            attachments = await self._maybe_get_attachments(
                query, relevant_chunks, stream=True
            )

            # Inject attachments into context for the LLM
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

            # Grounding: only for real-time queries (lãnh đạo, sự kiện, tin tức...)
            full_prompt, needs_grounding = self._build_generation_prompt(
                query, language, system_prompt, user_prompt
            )
            if needs_grounding:
                log.info("[ASYNC STREAM] Grounding ENABLED (real-time query)")
            else:
                log.info("[ASYNC STREAM] Grounding DISABLED (using internal documents)")

            # TRUE ASYNC STREAMING from Gemini
            full_answer = ""
            async for text_chunk in generate_response_stream_async(
                prompt=full_prompt, enable_grounding=needs_grounding
            ):
                full_answer += text_chunk
                yield {"type": "answer_chunk", "content": text_chunk}

            # Add engagement prompt
            if full_answer:
                original_length = len(full_answer)
                enhanced_answer = self.rag_service._add_engagement_prompt(
                    full_answer, query, language
                )
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
                "images": [],
                "normalization_applied": normalization_applied,
                "original_query": query if normalization_applied else None,
                "normalized_query": normalized_query if normalization_applied else None,
            }

            # Save conversation (background)
            asyncio.create_task(
                self._save_conversation_async(
                    conversation_id,
                    query,
                    full_answer,
                    sources,
                    confidence,
                    normalization_applied,
                    normalized_query,
                )
            )

            self._update_conversation_history(conversation_id, query, full_answer)

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
                vision_prompt = f"""You are the official admission assistant for the People's Security University.
Analyze the image(s) only for admission-related information and answer: {query if query else "Extract the admission information shown in this image."}
If the image is not related to official admission information, say you do not have enough basis from official admission materials.
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

    def _build_source_references(
        self, chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build source references from chunks."""
        source_references = []
        for chunk in chunks:
            content = chunk.get("content", "")
            snippet = content[:200] + "..." if len(content) > 200 else content

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

            source_references.append(
                {
                    "chunk_id": str(chunk.get("chunk_id", "")),
                    "filename": chunk.get("source_file", "") or chunk.get("source", ""),
                    "page_number": chunk.get("page_number"),
                    "heading": chunk.get("heading_text"),
                    "content_snippet": snippet,
                    "full_content": content,
                    "relevance_score": relevance_score,
                }
            )
        return source_references

    def _calculate_confidence(self, chunks: List[Dict[str, Any]]) -> float:
        """
        Multi-factor confidence score.

        Three components (each in [0, 1]):
        - Retrieval quality  (50%): weighted top-3 score, not blind average
        - Source diversity   (30%): number of distinct official source files
        - Document freshness (20%): year extracted from source filename

        This is more meaningful than a single raw similarity average and
        avoids users interpreting the badge as an absolute model certainty.
        """
        if not chunks:
            return 0.0

        import re as _re

        # ── 1. Retrieval quality (top-3 weighted) ──────────────────────────
        def _norm_score(raw: float) -> float:
            """Normalise cross-encoder scores (can be >1 or negative) to [0,1]."""
            if raw > 1.0:
                return min(1.0, (raw + 10) / 20)
            if raw < 0:
                return max(0.0, (raw + 10) / 20)
            return float(raw)

        top_chunks = chunks[:3]
        raw_scores = [
            _norm_score(
                c.get("rerank_score")
                or c.get("combined_score")
                or c.get("dense_score")
                or 0.0
            )
            for c in top_chunks
        ]
        # Weight: 1st result counts 50%, 2nd 30%, 3rd 20%
        weights = [0.5, 0.3, 0.2][: len(raw_scores)]
        weight_sum = sum(weights)
        retrieval_score = sum(s * w for s, w in zip(raw_scores, weights)) / weight_sum

        # ── 2. Source diversity ────────────────────────────────────────────
        distinct_sources = len(
            {
                c.get("source") or c.get("source_file", "")
                for c in chunks
                if c.get("source") or c.get("source_file")
            }
        )
        # 1 source → 0.4, 2 → 0.65, 3+ → 1.0  (soft cap)
        diversity_score = min(1.0, 0.4 + (distinct_sources - 1) * 0.3)

        # ── 3. Document freshness ──────────────────────────────────────────
        import datetime as _dt

        current_year = _dt.datetime.now().year
        years_found = []
        for c in chunks[:5]:
            src = c.get("source") or c.get("source_file", "")
            for yr in _re.findall(r"20[12][0-9]", src):
                years_found.append(int(yr))
        if years_found:
            latest_year = max(years_found)
            age = current_year - latest_year
            # 0 years old → 1.0, 1 year → 0.85, 2 years → 0.70, 3+ → 0.55
            freshness_score = max(0.55, 1.0 - age * 0.15)
        else:
            freshness_score = 0.75  # unknown age → neutral

        # ── Weighted composite ─────────────────────────────────────────────
        confidence = (
            0.50 * retrieval_score + 0.30 * diversity_score + 0.20 * freshness_score
        )
        return round(min(max(confidence, 0.0), 1.0), 3)

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
                    "normalized_query": (
                        normalized_query if normalization_applied else None
                    ),
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
