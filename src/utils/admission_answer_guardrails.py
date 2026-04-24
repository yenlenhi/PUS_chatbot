"""
Public facade for admission answer guardrails and structured answer helpers.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional

from src.utils.admission_answer_normalization import (
    build_answer_repair_prompt,
    build_reference_year_bridge_answer,
    build_safe_admission_fallback_answer,
    normalize_answer_markdown,
    validate_admission_answer,
)
from src.utils.admission_document_priority import (
    build_query_metadata_filters,
    has_explicit_year,
    infer_query_doc_type,
)
from src.utils.admission_quota_answers import (
    build_structured_quota_answer,
    should_use_structured_quota_pipeline,
)
from src.utils.admission_score_answers import build_structured_score_answer
from src.utils.fixed_admission_faq import get_fixed_admission_faq


def _collect_chunk_years(chunks: List[Dict[str, Any]]) -> List[int]:
    years: set[int] = set()
    for chunk in chunks:
        for field in ("admission_cycle", "document_year"):
            value = chunk.get(field)
            if isinstance(value, int):
                years.add(value)

        for field in ("admission_years", "document_years"):
            values = chunk.get(field)
            if not isinstance(values, list):
                continue
            years.update(value for value in values if isinstance(value, int))

    return sorted(years)


def _finalize_structured_answer(
    query: str,
    chunks: List[Dict[str, Any]],
    answer: Optional[str],
    *,
    allow_reference_bridge: bool = True,
) -> Optional[str]:
    if not answer:
        return None

    if allow_reference_bridge:
        available_years = _collect_chunk_years(chunks)
        current_year = dt.datetime.now().year
        if available_years and not has_explicit_year(query):
            latest_reference_year = max(
                (year for year in available_years if year <= current_year),
                default=max(available_years),
            )
            if latest_reference_year < current_year:
                answer = build_reference_year_bridge_answer(
                    answer,
                    current_year=current_year,
                    reference_year=latest_reference_year,
                )

    violations = validate_admission_answer(query, answer, chunks)
    return None if violations else answer


def build_structured_admission_answer(
    query: str, chunks: List[Dict[str, Any]], language: str = "vi"
) -> Optional[str]:
    if language != "vi":
        return None

    faq = get_fixed_admission_faq(query)
    if faq:
        return _finalize_structured_answer(
            query,
            chunks,
            faq["answer"],
            allow_reference_bridge=False,
        )

    doc_type = infer_query_doc_type(query)
    if doc_type == "quota" and should_use_structured_quota_pipeline(query):
        return _finalize_structured_answer(
            query, chunks, build_structured_quota_answer(query, chunks)
        )

    if doc_type == "scores":
        return _finalize_structured_answer(
            query, chunks, build_structured_score_answer(query, chunks)
        )

    return None


def should_use_structured_pipeline(query: str) -> bool:
    if get_fixed_admission_faq(query):
        return True

    doc_type = infer_query_doc_type(query)
    if should_use_structured_quota_pipeline(query):
        return True

    if doc_type == "scores":
        return True

    return False


def get_structured_answer_metadata(query: str) -> Dict[str, Any]:
    filters = build_query_metadata_filters(query)
    return {
        "doc_type": filters.get("doc_type"),
        "filters": filters,
        "structured": should_use_structured_pipeline(query),
    }


__all__ = [
    "build_answer_repair_prompt",
    "build_reference_year_bridge_answer",
    "build_safe_admission_fallback_answer",
    "build_structured_admission_answer",
    "build_structured_score_answer",
    "get_structured_answer_metadata",
    "normalize_answer_markdown",
    "should_use_structured_pipeline",
    "validate_admission_answer",
]
