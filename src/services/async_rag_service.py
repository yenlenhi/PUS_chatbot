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
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, AsyncGenerator, Tuple
import re
import unicodedata

from src.utils.logger import log
from src.utils.admission_document_priority import (
    enrich_query_for_current_cycle,
    enrich_query_for_primary_school,
)
from src.utils.admission_answer_guardrails import (
    build_answer_repair_prompt,
    build_reference_year_bridge_answer,
    build_safe_admission_fallback_answer,
    normalize_answer_markdown,
    validate_admission_answer,
)
from src.utils.fixed_admission_faq import get_fixed_admission_faq
from src.services.async_gemini_service import (
    generate_response_async,
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
    ENABLE_STAGE_TIMINGS,
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
    ) -> Tuple[List[Dict[str, Any]], bool]:
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
                return chunks, True
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
        return chunks, False

    def _new_performance_metrics(self) -> Dict[str, Any]:
        return {
            "stages": {},
            "time_to_first_token_ms": None,
            "retrieval_cache_hit": False,
            "attachment_lookup_skipped": False,
            "needs_grounding": False,
            "normalization_applied": False,
            "rewrite_applied": False,
            "memory_loaded": False,
            "retrieved_chunk_count": 0,
            "response_path": "rag",
            "policy_applied": None,
        }

    def _record_stage(
        self, performance: Optional[Dict[str, Any]], stage: str, started_at: float
    ) -> None:
        if not ENABLE_STAGE_TIMINGS or performance is None:
            return
        performance["stages"][stage] = round(
            (time.perf_counter() - started_at) * 1000, 2
        )

    def _finalize_performance(
        self,
        performance: Optional[Dict[str, Any]],
        request_started_at: float,
        **updates,
    ) -> Optional[Dict[str, Any]]:
        if not ENABLE_STAGE_TIMINGS or performance is None:
            return None

        performance.update(updates)
        performance["total_ms"] = round(
            (time.perf_counter() - request_started_at) * 1000, 2
        )
        return performance

    def _log_performance(
        self, conversation_id: str, performance: Optional[Dict[str, Any]]
    ) -> None:
        if not ENABLE_STAGE_TIMINGS or not performance:
            return

        stage_summary = ", ".join(
            f"{stage}={duration:.2f}ms"
            for stage, duration in performance.get("stages", {}).items()
        )
        first_token = performance.get("time_to_first_token_ms")
        first_token_summary = (
            f", first_token={first_token:.2f}ms"
            if isinstance(first_token, (float, int))
            else ""
        )
        log.info(
            f"[PERF] conversation_id={conversation_id} path={performance.get('response_path')} "
            f"total={performance.get('total_ms', 0):.2f}ms{first_token_summary} "
            f"cache_hit={performance.get('retrieval_cache_hit', False)} "
            f"chunks={performance.get('retrieved_chunk_count', 0)} "
            f"grounding={performance.get('needs_grounding', False)} "
            f"attachment_skipped={performance.get('attachment_lookup_skipped', False)} "
            f"stages=[{stage_summary}]"
        )

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
        performance: Optional[Dict[str, Any]] = None,
        answer_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "answer": answer_override
            if answer_override is not None
            else self.scope_service.build_policy_answer(policy, language),
            "follow_up_questions": [],
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
            "performance": performance,
        }

    def _build_fixed_faq_payload(
        self,
        faq: Dict[str, Any],
        conversation_id: str,
        query: str,
        language: str,
        *,
        performance: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        answer = faq.get("answer", "")
        sources = faq.get("sources", [])
        follow_up_questions = faq.get("follow_up_questions", [])
        if not follow_up_questions and answer:
            # Fixed FAQ responses short-circuit before the normal engagement stage,
            # so fall back to the shared deterministic follow-up generator when
            # no curated suggestions are provided in the FAQ catalog.
            follow_up_questions = self.rag_service.generate_structured_follow_up_questions(
                query,
                answer,
                language=language,
                sources=sources,
                attachments=[],
            )
        confidence = faq.get("confidence", 0.98)

        return {
            "answer": answer,
            "follow_up_questions": follow_up_questions,
            "sources": sources,
            "source_references": [],
            "attachments": [],
            "confidence": confidence,
            "conversation_id": conversation_id,
            "normalization_applied": False,
            "original_query": None,
            "normalized_query": None,
            "chart_data": [],
            "images": [],
            "performance": performance,
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

    def _normalize_for_match(self, text: Optional[str]) -> str:
        if not text:
            return ""

        stripped = unicodedata.normalize("NFD", text)
        stripped = stripped.replace("đ", "d").replace("Đ", "D")
        stripped = "".join(
            ch for ch in stripped if unicodedata.category(ch) != "Mn"
        ).lower()
        stripped = re.sub(r"[^a-z0-9\s]", " ", stripped)
        return re.sub(r"\s+", " ", stripped).strip()

    def _get_score_query_metadata(self, query: Optional[str]) -> Dict[str, bool]:
        normalized = self._normalize_for_match(query)
        explicit_score_terms = (
            "diem chuan",
            "diem xet",
            "diem trung tuyen",
        )
        generic_score_terms = (
            "diem tuyen sinh",
            "diem vao",
            "diem vao truong",
            "diem vao nganh",
            "diem dau vao",
            "muc diem",
        )

        has_explicit_score_term = any(
            term in normalized for term in explicit_score_terms
        )
        has_generic_score_term = any(term in normalized for term in generic_score_terms)
        has_year = bool(re.search(r"\b20\d{2}\b", normalized))
        has_major_hint = any(
            term in normalized
            for term in (
                " nganh ",
                "chuyen nganh",
                "ma nganh",
                "to hop",
                "khoi ",
            )
        ) or normalized.startswith("nganh ")
        token_count = len(normalized.split())

        has_score_signal = "diem" in normalized and (
            has_explicit_score_term
            or has_generic_score_term
            or "tuyen sinh" in normalized
            or "xet tuyen" in normalized
            or "truong" in normalized
            or "nganh" in normalized
        )
        is_under_specified = (
            has_score_signal and token_count <= 5 and not has_year and not has_major_hint
        )
        needs_synonym_expansion = has_score_signal and (
            has_generic_score_term or (token_count <= 5 and not has_explicit_score_term)
        )

        return {
            "has_score_signal": has_score_signal,
            "has_explicit_score_term": has_explicit_score_term,
            "has_generic_score_term": has_generic_score_term,
            "has_year": has_year,
            "has_major_hint": has_major_hint,
            "is_under_specified": is_under_specified,
            "needs_synonym_expansion": needs_synonym_expansion,
        }

    def _enrich_retrieval_query(
        self, original_query: str, retrieval_query: str
    ) -> Tuple[str, bool]:
        enriched_query, current_cycle_enriched = enrich_query_for_current_cycle(
            retrieval_query
        )
        enriched_query, primary_school_enriched = enrich_query_for_primary_school(
            enriched_query
        )
        if primary_school_enriched:
            log.info(
                f"[ASYNC] Applied primary-school enrichment: '{retrieval_query[:60]}' -> '{enriched_query[:120]}'"
            )
        metadata = self._get_score_query_metadata(retrieval_query or original_query)
        if not metadata["needs_synonym_expansion"]:
            if current_cycle_enriched:
                log.info(
                    f"[ASYNC] Applied current-cycle enrichment: '{retrieval_query[:60]}' -> '{enriched_query[:120]}'"
                )
            return enriched_query, current_cycle_enriched or primary_school_enriched

        normalized = self._normalize_for_match(enriched_query or original_query)
        enrichment_terms: List[str] = []
        if "diem chuan" not in normalized:
            enrichment_terms.append("điểm chuẩn tuyển sinh")
        if "diem xet" not in normalized:
            enrichment_terms.append("điểm xét tuyển")
        if "diem trung tuyen" not in normalized:
            enrichment_terms.append("điểm trúng tuyển")
        if not metadata["has_year"]:
            enrichment_terms.append("các năm")
        if "an ninh nhan dan" not in normalized:
            enrichment_terms.append("Trường Đại học An ninh Nhân dân")

        enriched_query = " ".join(
            part for part in [enriched_query.strip(), *enrichment_terms] if part
        ).strip()
        if enriched_query != retrieval_query:
            log.info(
                f"[ASYNC] Enriched retrieval query: '{retrieval_query[:60]}' -> '{enriched_query[:120]}'"
            )
            return enriched_query, True

        return enriched_query, current_cycle_enriched or primary_school_enriched

    async def _repair_answer_if_needed(
        self,
        query: str,
        answer: str,
        context: str,
        relevant_chunks: List[Dict[str, Any]],
        language: str = "vi",
    ) -> Tuple[str, List[str]]:
        violations = validate_admission_answer(query, answer, relevant_chunks)
        if not violations:
            return normalize_answer_markdown(answer), []

        log.warning(f"[ASYNC GUARDRAIL] Answer violations detected: {violations}")
        repaired_answer = answer
        try:
            repair_prompt = build_answer_repair_prompt(
                query=query,
                context=context,
                draft_answer=answer,
                violations=violations,
                language=language,
            )
            repair_response = await generate_response_async(prompt=repair_prompt)
            if repair_response and repair_response.strip():
                repaired_answer = repair_response.strip()
        except Exception as exc:
            log.warning(f"[ASYNC GUARDRAIL] Repair call failed: {exc}")

        remaining = validate_admission_answer(query, repaired_answer, relevant_chunks)
        if remaining:
            if set(remaining) == {"older_year_presented_as_current"}:
                return (
                    build_reference_year_bridge_answer(
                        repaired_answer, language=language
                    ),
                    remaining,
                )

            structured_answer = self.rag_service.try_build_structured_admission_answer(
                query, relevant_chunks, language=language
            )
            if structured_answer:
                return normalize_answer_markdown(structured_answer), remaining

            return (
                normalize_answer_markdown(
                    build_safe_admission_fallback_answer(
                        query, remaining, language=language
                    )
                ),
                remaining,
            )

        return normalize_answer_markdown(repaired_answer), violations

    def _split_answer_for_stream(self, answer: str, max_chars: int = 220) -> List[str]:
        if not answer:
            return []

        normalized_answer = normalize_answer_markdown(answer)
        paragraphs = [part for part in normalized_answer.split("\n\n") if part.strip()]
        chunks: List[str] = []
        current = ""

        for paragraph in paragraphs:
            candidate = paragraph if not current else f"{current}\n\n{paragraph}"
            if len(candidate) <= max_chars:
                current = candidate
                continue
            if current:
                chunks.append(f"{current}\n\n")
            current = paragraph

        if current:
            chunks.append(current)

        return chunks or [normalized_answer]

    def _should_return_score_clarification(
        self, original_query: str, retrieval_query: str
    ) -> bool:
        metadata = self._get_score_query_metadata(retrieval_query or original_query)
        return metadata["is_under_specified"]

    def _build_score_clarification_answer(self, language: str = "vi") -> str:
        if language == "en":
            return (
                "Do you want the admission cutoff score for a specific year or major? "
                "For example: \"admission cutoff score 2025\" or "
                "\"cybersecurity cutoff score 2025\". If you want, I can also provide "
                "the latest cutoff score available in the official documents."
            )

        return (
            "Bạn muốn tra điểm chuẩn tuyển sinh theo năm nào hoặc ngành nào? "
            "Ví dụ: \"điểm chuẩn tuyển sinh 2025\" hoặc "
            "\"điểm chuẩn ngành An ninh mạng năm 2025\". Nếu cần, tôi cũng có thể "
            "cung cấp điểm chuẩn gần nhất đang có trong tài liệu chính thức."
        )

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
    ) -> Tuple[List[Dict[str, Any]], bool]:
        if not relevant_chunks:
            return [], True

        if not self._should_fetch_attachments(query, relevant_chunks):
            log.info(
                "[ASYNC STREAM] Skip attachment retrieval (no attachment intent detected)"
                if stream
                else "[ASYNC] Skip attachment retrieval (no attachment intent detected)"
            )
            return [], True

        attachments = await self._run_in_executor(
            self.rag_service._retrieve_attachments_for_context,
            query,
            relevant_chunks,
        )
        return attachments, False

    def _normalize_router_text(self, query: str) -> str:
        import re
        import unicodedata

        normalized = unicodedata.normalize("NFD", (query or "").strip().lower())
        normalized = normalized.replace("đ", "d").replace("Đ", "D")
        normalized = "".join(
            ch for ch in normalized if unicodedata.category(ch) != "Mn"
        )
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.strip()

    def _is_context_dependent_followup(
        self, normalized_query: str, query_tokens: List[str]
    ) -> bool:
        import re

        if not normalized_query:
            return False

        if re.fullmatch(r"(nam\s*)?20\d{2}", normalized_query):
            return True

        if re.fullmatch(r"(nam\s*)?20\d{2}\s*(thi sao|the nao)?", normalized_query):
            return True

        short_followup_patterns = [
            r"^(con|the con|vay thi|vay con|the thi)\b",
            r"^(ngoai ra|ben canh do)\b",
            r"\b(nam do|nam kia|nam nay)\b",
            r"\b(phuong thuc do|nganh do|truong do|mon do)\b",
        ]
        if any(
            re.search(pattern, normalized_query)
            for pattern in short_followup_patterns
        ):
            return True

        return len(query_tokens) <= 3 and any(
            token in {"nam", "2024", "2025", "2026", "do", "kia", "nay"}
            for token in query_tokens
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

        query_lower = self._normalize_router_text(query)
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
            g in query_lower for g in ["xin chao", "hello", "hi", "chao"]
        )
        needs_normalization = (
            has_abbrev or is_too_short
        ) and ENABLE_GEMINI_NORMALIZATION

        # ── needs_rewrite ───────────────────────────────────────────────────
        # Query uses reference expressions that only make sense with prior context
        reference_patterns = [
            r"\b(do|kia|vay|neu tren|nhu vay|da neu)\b",
            r"nganh (nay|do|kia|tren|vua|da (noi|de cap))",
            r"truong (nay|do|kia)",
            r"^(con|the con|vay thi|vay con|the thi)\b",
            r"^(ngoai ra|ben canh do)",
            r"\btai sao\b.+\b(vay|the)\b",
            r"(mon hoc|diem chuan|hoc phi|chi tieu).*(do|kia|tren)",
        ]
        has_reference = any(re.search(p, query_lower) for p in reference_patterns)
        has_context_dependent_followup = self._is_context_dependent_followup(
            query_lower, query_tokens
        )
        needs_rewrite = (
            conv_turn_count > 0
            and (has_reference or has_context_dependent_followup or is_too_short)
        )

        # ── needs_memory ────────────────────────────────────────────────────
        # Only load long-term memory for older conversations that explicitly
        # refer back to earlier parts of the dialogue
        memory_back_ref_patterns = [
            r"\b(truoc do|hoi nay|luc nay|vua roi)\b",
            r"\b(da hoi|da noi|da de cap|nhu da)\b",
            r"\b(nho lai|nhac lai|giai thich lai|noi lai)\b",
        ]
        has_memory_ref = any(
            re.search(p, query_lower) for p in memory_back_ref_patterns
        )
        needs_memory = conv_turn_count > 4 and (
            has_memory_ref or has_reference or has_context_dependent_followup
        )

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
            request_started_at = time.perf_counter()
            performance = (
                self._new_performance_metrics() if ENABLE_STAGE_TIMINGS else None
            )

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
                scope_started_at = time.perf_counter()
                scope_decision = self.scope_service.classify(
                    query, has_images=bool(images)
                )
                self._record_stage(performance, "scope_guard", scope_started_at)
                if scope_decision.scope != "admission":
                    log.info(
                        f"[POLICY] Short-circuit query as {scope_decision.scope}: {scope_decision.reason}"
                    )
                    finalized_performance = self._finalize_performance(
                        performance,
                        request_started_at,
                        response_path="policy",
                        policy_applied=scope_decision.scope,
                    )
                    response = self._build_policy_payload(
                        scope_decision.scope,
                        conversation_id,
                        language,
                        performance=finalized_performance,
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
                    self._log_performance(conversation_id, finalized_performance)
                    return response

            fixed_faq = get_fixed_admission_faq(query)
            if fixed_faq:
                finalized_performance = self._finalize_performance(
                    performance,
                    request_started_at,
                    response_path="faq",
                    policy_applied="fixed_admission_faq",
                )
                response = self._build_fixed_faq_payload(
                    fixed_faq,
                    conversation_id,
                    query,
                    language,
                    performance=finalized_performance,
                )
                self._update_conversation_history(
                    conversation_id, query, response["answer"]
                )
                asyncio.create_task(
                    self._save_conversation_async(
                        conversation_id,
                        query,
                        response["answer"],
                        response["sources"],
                        response["confidence"],
                        False,
                        query,
                    )
                )
                self._log_performance(conversation_id, finalized_performance)
                return response

            if images and len(images) > 0:
                vision_started_at = time.perf_counter()
                vision_response = await self._generate_vision_answer_async(
                    query=query,
                    images=images,
                    conversation_id=conversation_id,
                    language=language,
                )
                self._record_stage(performance, "vision_generation", vision_started_at)
                finalized_performance = self._finalize_performance(
                    performance,
                    request_started_at,
                    response_path="vision",
                )
                vision_response["performance"] = finalized_performance
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
                self._log_performance(conversation_id, finalized_performance)
                return vision_response

            normalization_applied = False
            rewrite_applied = False
            memory_loaded = False
            normalized_query = query
            retrieval_query = query
            memory_context = ""
            current_history = self.rag_service.conversations.get(conversation_id, [])
            conv_turn_count = len(current_history)

            intent = self._classify_query(query, conv_turn_count)

            # Step 1: Normalize — only for queries with abbreviations / typos
            if not skip_normalization and intent["needs_normalization"]:
                normalization_started_at = time.perf_counter()
                log.info("[ASYNC] Normalizing query (abbreviations/typos detected)...")
                normalized_query = await normalize_question_async(query)
                normalization_applied = normalized_query != query
                if performance is not None:
                    performance["normalization_applied"] = normalization_applied
                log.info(
                    f"[ASYNC] Normalized: '{query[:40]}' -> '{normalized_query[:40]}'"
                )
                self._record_stage(
                    performance, "normalization", normalization_started_at
                )
            else:
                log.info("[ASYNC] Skip normalization (query is clear)")

            # Step 2: Rewrite — only for follow-up queries referencing prior turns
            if intent["needs_rewrite"] and current_history:
                rewrite_started_at = time.perf_counter()
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
                        rewrite_applied = True
                        if performance is not None:
                            performance["rewrite_applied"] = True
                        normalized_query = rewritten_query.strip()
                except Exception as rw_err:
                    log.warning(f"[ASYNC] Query rewrite failed: {rw_err}")
                finally:
                    self._record_stage(performance, "rewrite", rewrite_started_at)
            else:
                log.info("[ASYNC] Skip rewrite (query is self-contained)")

            retrieval_query, _ = self._enrich_retrieval_query(query, normalized_query)

            # Step 3: Memory — only for long conversations with explicit back-references
            if intent["needs_memory"]:
                memory_started_at = time.perf_counter()
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
                        memory_loaded = True
                        if performance is not None:
                            performance["memory_loaded"] = True
                        log.info("🧠 [ASYNC] Loaded memory context")
                except Exception as mem_error:
                    log.warning(f"Could not load memory context: {mem_error}")
                finally:
                    self._record_stage(performance, "memory", memory_started_at)
            else:
                log.info(
                    f"[ASYNC] Skip memory retrieval (turns={conv_turn_count}, no back-reference)"
                )

            # Retrieve relevant chunks (with short-TTL cache)
            retrieval_started_at = time.perf_counter()
            relevant_chunks, retrieval_cache_hit = await self._cached_retrieve_chunks(
                retrieval_query
            )
            self._record_stage(performance, "retrieval", retrieval_started_at)
            if performance is not None:
                performance["retrieval_cache_hit"] = retrieval_cache_hit
                performance["retrieved_chunk_count"] = len(relevant_chunks)

            # Create context and sources
            post_retrieval_started_at = time.perf_counter()
            context = self.rag_service.create_context(relevant_chunks)
            sources = self._build_sources(relevant_chunks)

            # Build source references
            source_references = self._build_source_references(relevant_chunks)
            confidence = self._calculate_confidence(relevant_chunks)
            self._record_stage(
                performance, "post_retrieval", post_retrieval_started_at
            )

            if STRICT_MODE and confidence < CONFIDENCE_THRESHOLD:
                if self._should_return_score_clarification(query, normalized_query):
                    answer = self._build_score_clarification_answer(language)
                    finalized_performance = self._finalize_performance(
                        performance,
                        request_started_at,
                        response_path="policy",
                        policy_applied="ambiguous_score_query",
                        normalization_applied=normalization_applied,
                        rewrite_applied=rewrite_applied,
                        memory_loaded=memory_loaded,
                    )
                    response = self._build_policy_payload(
                        "ambiguous",
                        conversation_id,
                        language,
                        source_references=source_references,
                        sources=sources,
                        confidence=confidence,
                        normalization_applied=normalization_applied,
                        original_query=query,
                        normalized_query=normalized_query,
                        performance=finalized_performance,
                        answer_override=answer,
                    )
                    self._update_conversation_history(
                        conversation_id, query, response["answer"]
                    )
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
                    self._log_performance(conversation_id, finalized_performance)
                    return response

                log.info(
                    f"[POLICY] Insufficient evidence, confidence={confidence:.3f} threshold={CONFIDENCE_THRESHOLD:.3f}"
                )
                finalized_performance = self._finalize_performance(
                    performance,
                    request_started_at,
                    response_path="policy",
                    policy_applied="insufficient_evidence",
                    normalization_applied=normalization_applied,
                    rewrite_applied=rewrite_applied,
                    memory_loaded=memory_loaded,
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
                    performance=finalized_performance,
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
                self._log_performance(conversation_id, finalized_performance)
                return response

            # Get attachments
            attachments_started_at = time.perf_counter()
            attachments, attachment_lookup_skipped = await self._maybe_get_attachments(
                query, relevant_chunks
            )
            self._record_stage(performance, "attachments", attachments_started_at)
            if performance is not None:
                performance["attachment_lookup_skipped"] = attachment_lookup_skipped

            if attachments:
                attachment_context = "\n\n*** TÀI LIỆU ĐÍNH KÈM CÓ SẴN ***:\n"
                for att in attachments:
                    attachment_context += (
                        f"- {att['file_name']}: {att['description']}\n"
                    )
                context += attachment_context

            structured_answer = self.rag_service.try_build_structured_admission_answer(
                query, relevant_chunks, language=language
            )

            # Create prompts
            prompt_started_at = time.perf_counter()
            system_prompt = self.rag_service.create_system_prompt(language=language)
            user_prompt = self.rag_service.create_user_prompt(
                query, context, memory_context, language=language
            )

            # Grounding: only for real-time queries (lãnh đạo, sự kiện, tin tức...)
            full_prompt, needs_grounding = self._build_generation_prompt(
                query, language, system_prompt, user_prompt
            )
            self._record_stage(performance, "prompt_build", prompt_started_at)
            if performance is not None:
                performance["needs_grounding"] = needs_grounding

            # Generate answer using ASYNC Gemini call
            if structured_answer:
                answer = structured_answer
            else:
                log.info(f"[ASYNC] Calling Gemini API (grounding={needs_grounding})...")
                generation_started_at = time.perf_counter()
                answer = await generate_response_async(
                    prompt=full_prompt, enable_grounding=needs_grounding
                )
                self._record_stage(performance, "generation", generation_started_at)

            follow_up_questions: List[str] = []

            # Handle empty response
            if not answer or not answer.strip():
                log.error("LLM returned empty response")
                answer = "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau."
                confidence = 0.0
            else:
                if not structured_answer:
                    answer, violations = await self._repair_answer_if_needed(
                        query,
                        answer,
                        context,
                        relevant_chunks,
                        language=language,
                    )
                    if violations:
                        log.info(
                            f"[ASYNC GUARDRAIL] Final answer corrected after violations: {violations}"
                        )
                # Add engagement prompt
                engagement_started_at = time.perf_counter()
                follow_up_questions = self.rag_service.generate_structured_follow_up_questions(
                    query,
                    answer,
                    language=language,
                    sources=sources,
                    attachments=attachments,
                )
                self._record_stage(performance, "engagement", engagement_started_at)

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
            chart_started_at = time.perf_counter()
            chart_data = self.rag_service._detect_chart_request(query, answer)
            self._record_stage(performance, "chart_detection", chart_started_at)

            finalized_performance = self._finalize_performance(
                performance,
                request_started_at,
                response_path="rag",
                normalization_applied=normalization_applied,
                rewrite_applied=rewrite_applied,
                memory_loaded=memory_loaded,
            )
            self._log_performance(conversation_id, finalized_performance)

            return {
                "answer": answer,
                "follow_up_questions": follow_up_questions,
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
                "performance": finalized_performance,
            }

        except Exception as e:
            log.error(f"[ASYNC] Error generating answer: {e}")
            finalized_performance = self._finalize_performance(
                locals().get("performance"),
                locals().get("request_started_at", time.perf_counter()),
                response_path="error",
            )
            self._log_performance(
                conversation_id or str(uuid.uuid4()), finalized_performance
            )
            return {
                "answer": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
                "sources": [],
                "source_references": [],
                "attachments": [],
                "confidence": 0.0,
                "conversation_id": conversation_id or str(uuid.uuid4()),
                "chart_data": [],
                "images": [],
                "performance": finalized_performance,
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
            request_started_at = time.perf_counter()
            performance = (
                self._new_performance_metrics() if ENABLE_STAGE_TIMINGS else None
            )

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
                scope_started_at = time.perf_counter()
                scope_decision = self.scope_service.classify(query)
                self._record_stage(performance, "scope_guard", scope_started_at)
                if scope_decision.scope != "admission":
                    log.info(
                        f"[POLICY STREAM] Short-circuit query as {scope_decision.scope}: {scope_decision.reason}"
                    )
                    answer = self.scope_service.build_policy_answer(
                        scope_decision.scope, language
                    )
                    finalized_performance = self._finalize_performance(
                        performance,
                        request_started_at,
                        response_path="policy",
                        policy_applied=scope_decision.scope,
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
                        "performance": finalized_performance,
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
                    self._log_performance(conversation_id, finalized_performance)
                    return

            fixed_faq = get_fixed_admission_faq(query)
            if fixed_faq:
                response = self._build_fixed_faq_payload(
                    fixed_faq,
                    conversation_id,
                    query,
                    language,
                )
                finalized_performance = self._finalize_performance(
                    performance,
                    request_started_at,
                    response_path="faq",
                    policy_applied="fixed_admission_faq",
                )
                yield {
                    "type": "sources",
                    "sources": response["sources"],
                    "source_references": [],
                    "confidence": response["confidence"],
                }
                yield {"type": "answer_chunk", "content": response["answer"]}
                yield {
                    "type": "complete",
                    "attachments": [],
                    "chart_data": [],
                    "images": [],
                    "follow_up_questions": response["follow_up_questions"],
                    "normalization_applied": False,
                    "original_query": None,
                    "normalized_query": None,
                    "performance": finalized_performance,
                }
                asyncio.create_task(
                    self._save_conversation_async(
                        conversation_id,
                        query,
                        response["answer"],
                        response["sources"],
                        response["confidence"],
                        False,
                        query,
                    )
                )
                self._update_conversation_history(
                    conversation_id, query, response["answer"]
                )
                self._log_performance(conversation_id, finalized_performance)
                return

            normalized_query = query
            normalization_applied = False
            rewrite_applied = False
            memory_loaded = False
            retrieval_query = query
            memory_context = ""
            current_history = self.rag_service.conversations.get(conversation_id, [])
            conv_turn_count = len(current_history)

            intent = self._classify_query(query, conv_turn_count)

            # Step 1: Normalize — only for abbreviations / unclear short queries
            if not skip_normalization and intent["needs_normalization"]:
                normalization_started_at = time.perf_counter()
                log.info("[ASYNC STREAM] Normalizing query (abbreviations/typos)...")
                normalized_query = await normalize_question_async(query)
                normalization_applied = normalized_query != query
                if performance is not None:
                    performance["normalization_applied"] = normalization_applied
                log.info(
                    f"[ASYNC STREAM] Normalized: '{query[:40]}' -> '{normalized_query[:40]}'"
                )
                self._record_stage(
                    performance, "normalization", normalization_started_at
                )
            else:
                log.info("[ASYNC STREAM] Skip normalization (query is clear)")

            # Step 2: Rewrite — only for follow-up queries referencing prior turns
            if intent["needs_rewrite"] and current_history:
                rewrite_started_at = time.perf_counter()
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
                        rewrite_applied = True
                        if performance is not None:
                            performance["rewrite_applied"] = True
                        normalized_query = rewritten_query.strip()
                except Exception as rw_err:
                    log.warning(f"[ASYNC STREAM] Query rewrite failed: {rw_err}")
                finally:
                    self._record_stage(performance, "rewrite", rewrite_started_at)
            else:
                log.info("[ASYNC STREAM] Skip rewrite (query is self-contained)")

            retrieval_query, _ = self._enrich_retrieval_query(query, normalized_query)

            # Step 3: Memory — only for long conversations with explicit back-references
            if intent["needs_memory"]:
                memory_started_at = time.perf_counter()
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
                        memory_loaded = True
                        if performance is not None:
                            performance["memory_loaded"] = True
                        log.info("🧠 [ASYNC STREAM] Loaded memory context")
                except Exception as mem_error:
                    log.warning(f"Memory context error: {mem_error}")
                finally:
                    self._record_stage(performance, "memory", memory_started_at)
            else:
                log.info(
                    f"[ASYNC STREAM] Skip memory retrieval (turns={conv_turn_count}, no back-reference)"
                )

            # Retrieval (thread pool, with short-TTL cache)
            yield {"type": "status", "message": "Đang tìm kiếm tài liệu..."}

            retrieval_started_at = time.perf_counter()
            relevant_chunks, retrieval_cache_hit = await self._cached_retrieve_chunks(
                retrieval_query
            )
            self._record_stage(performance, "retrieval", retrieval_started_at)
            if performance is not None:
                performance["retrieval_cache_hit"] = retrieval_cache_hit
                performance["retrieved_chunk_count"] = len(relevant_chunks)

            post_retrieval_started_at = time.perf_counter()
            context = self.rag_service.create_context(relevant_chunks)

            # Get sources
            sources = self._build_sources(relevant_chunks)

            source_references = self._build_source_references(relevant_chunks)
            confidence = self._calculate_confidence(relevant_chunks)
            self._record_stage(
                performance, "post_retrieval", post_retrieval_started_at
            )

            if STRICT_MODE and confidence < CONFIDENCE_THRESHOLD:
                if self._should_return_score_clarification(query, normalized_query):
                    answer = self._build_score_clarification_answer(language)
                    policy_name = "ambiguous_score_query"
                else:
                    answer = self.scope_service.build_policy_answer(
                        "insufficient_evidence", language
                    )
                    policy_name = "insufficient_evidence"
                finalized_performance = self._finalize_performance(
                    performance,
                    request_started_at,
                    response_path="policy",
                    policy_applied=policy_name,
                    normalization_applied=normalization_applied,
                    rewrite_applied=rewrite_applied,
                    memory_loaded=memory_loaded,
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
                    "performance": finalized_performance,
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
                self._log_performance(conversation_id, finalized_performance)
                return

            # Get attachments
            attachments_started_at = time.perf_counter()
            attachments, attachment_lookup_skipped = await self._maybe_get_attachments(
                query, relevant_chunks, stream=True
            )
            self._record_stage(performance, "attachments", attachments_started_at)
            if performance is not None:
                performance["attachment_lookup_skipped"] = attachment_lookup_skipped

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

            if attachments:
                yield {
                    "type": "attachments",
                    "attachments": attachments,
                }

            # Send sources
            yield {
                "type": "sources",
                "sources": sources,
                "source_references": source_references,
                "confidence": confidence,
            }

            # Generate streaming answer
            yield {"type": "status", "message": "Đang tạo câu trả lời..."}

            prompt_started_at = time.perf_counter()
            system_prompt = self.rag_service.create_system_prompt(language=language)
            user_prompt = self.rag_service.create_user_prompt(
                query, context, memory_context, language=language
            )

            # Grounding: only for real-time queries (lãnh đạo, sự kiện, tin tức...)
            full_prompt, needs_grounding = self._build_generation_prompt(
                query, language, system_prompt, user_prompt
            )
            self._record_stage(performance, "prompt_build", prompt_started_at)
            if performance is not None:
                performance["needs_grounding"] = needs_grounding
            if needs_grounding:
                log.info("[ASYNC STREAM] Grounding ENABLED (real-time query)")
            else:
                log.info("[ASYNC STREAM] Grounding DISABLED (using internal documents)")

            structured_answer = self.rag_service.try_build_structured_admission_answer(
                query, relevant_chunks, language=language
            )
            full_answer = structured_answer or ""
            first_token_ms = None

            if structured_answer:
                if full_answer:
                    first_token_ms = round(
                        (time.perf_counter() - request_started_at) * 1000, 2
                    )
                for text_chunk in self._split_answer_for_stream(full_answer):
                    yield {"type": "answer_chunk", "content": text_chunk}
            else:
                generation_started_at = time.perf_counter()
                generated_answer = await generate_response_async(
                    prompt=full_prompt, enable_grounding=needs_grounding
                )
                self._record_stage(
                    performance, "generation_stream", generation_started_at
                )
                full_answer = generated_answer or ""
                if full_answer:
                    full_answer, violations = await self._repair_answer_if_needed(
                        query,
                        full_answer,
                        context,
                        relevant_chunks,
                        language=language,
                    )
                    if violations:
                        log.info(
                            f"[ASYNC STREAM GUARDRAIL] Final answer corrected after violations: {violations}"
                        )

                if full_answer:
                    first_token_ms = round(
                        (time.perf_counter() - request_started_at) * 1000, 2
                    )
                    for text_chunk in self._split_answer_for_stream(full_answer):
                        yield {"type": "answer_chunk", "content": text_chunk}

            follow_up_questions: List[str] = []

            # Build structured follow-up suggestions
            if full_answer:
                engagement_started_at = time.perf_counter()
                follow_up_questions = self.rag_service.generate_structured_follow_up_questions(
                    query,
                    full_answer,
                    language=language,
                    sources=sources,
                    attachments=attachments,
                )
                self._record_stage(performance, "engagement", engagement_started_at)

            # Detect charts
            chart_started_at = time.perf_counter()
            chart_data = self.rag_service._detect_chart_request(query, full_answer)
            self._record_stage(performance, "chart_detection", chart_started_at)

            finalized_performance = self._finalize_performance(
                performance,
                request_started_at,
                response_path="rag",
                normalization_applied=normalization_applied,
                rewrite_applied=rewrite_applied,
                memory_loaded=memory_loaded,
                time_to_first_token_ms=first_token_ms,
            )

            # Final metadata
            yield {
                "type": "complete",
                "attachments": attachments,
                "chart_data": chart_data,
                "images": [],
                "follow_up_questions": follow_up_questions,
                "normalization_applied": normalization_applied,
                "original_query": query if normalization_applied else None,
                "normalized_query": normalized_query if normalization_applied else None,
                "performance": finalized_performance,
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
            self._log_performance(conversation_id, finalized_performance)

        except Exception as e:
            log.error(f"[ASYNC STREAM] Error: {e}")
            finalized_performance = self._finalize_performance(
                locals().get("performance"),
                locals().get("request_started_at", time.perf_counter()),
                response_path="error",
            )
            self._log_performance(
                conversation_id or str(uuid.uuid4()), finalized_performance
            )
            yield {
                "type": "error",
                "message": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
                "performance": finalized_performance,
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
        # Load display names once for all chunks
        try:
            display_names = self.rag_service.db_service.get_all_display_names()
        except Exception:
            display_names = {}

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

            source_file = chunk.get("source_file", "") or chunk.get("source", "")
            source_references.append(
                {
                    "chunk_id": str(chunk.get("chunk_id", "")),
                    "filename": source_file,
                    "page_number": chunk.get("page_number"),
                    "heading": chunk.get("heading_text"),
                    "content_snippet": snippet,
                    "relevance_score": relevance_score,
                    "document_year": chunk.get("document_year"),
                    "source_url": chunk.get("source_url"),
                    "display_name": display_names.get(source_file) or None,
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
