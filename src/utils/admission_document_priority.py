"""
Utilities for prioritizing official admission documents for the current cycle.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

log = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"

_YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
_ADMISSION_TERMS = (
    "tuyen sinh",
    "xet tuyen",
    "chi tieu",
    "ho so",
    "diem chuan",
    "nganh",
    "phuong thuc",
    "dieu kien",
    "dang ky",
    "moc thoi gian",
    "nhap hoc",
    "xac nhan nhap hoc",
    "so tuyen",
)
_ADMISSION_DOC_TERMS = (
    "tuyen sinh",
    "chi tieu",
    "thong bao",
    "huong dan",
    "de an",
)
_PERSONNEL_TERMS = (
    "hieu truong",
    "pho hieu truong",
    "ban giam hieu",
    "lanh dao",
    "can bo",
    "nhan su",
    "co cau to chuc",
    "co cau",
    "truong khoa",
    "pho truong khoa",
    "truong phong",
    "pho truong phong",
    "phong ban",
    "don vi",
    "bo mon",
)
_PERSONNEL_DOC_STRONG_TERMS = (
    "co cau to chuc",
    "nhan su",
)
_PERSONNEL_DOC_TERMS = (
    "co cau",
    "to chuc",
    "nhan su",
    "ban giam hieu",
    "lanh dao",
    "can bo",
)
_UPDATED_DOC_TERMS = ("cap nhat", "updated", "moi nhat")
_CURRENT_CYCLE_HINTS = (
    "nam nay",
    "moi nhat",
    "hien tai",
    "dot nay",
    "ky nay",
)
_DRAFT_TERMS = ("du thao", "draft")
_PRIMARY_SCHOOL_TERMS = (
    "truong dai hoc an ninh nhan dan",
    "an ninh nhan dan",
    "annd",
    "t04",
    "ans",
)
_PRIMARY_SCHOOL_STRONG_DOC_TERMS = (
    "truong dai hoc an ninh nhan dan",
    "t04",
    "ans",
)
_OTHER_SCHOOL_TERMS = (
    "hoc vien an ninh nhan dan",
    "hoc vien canh sat nhan dan",
    "truong dai hoc canh sat nhan dan",
    "truong dai hoc phong chay chua chay",
    "truong dai hoc ky thuat hau can cand",
    "t01",
    "t02",
    "t03",
    "t05",
    "t06",
    "csh",
    "tdhc",
    "pccc",
)
_SYSTEM_WIDE_QUERY_TERMS = (
    "cac truong cand",
    "toan bo cac truong cand",
    "toan khoi cand",
    "toan nganh cong an",
    "toan luc luong cand",
    "bo cong an",
)
_SYSTEM_WIDE_DOC_TERMS = (
    "cac truong cand",
    "tong chi tieu",
    "toan quoc",
    "toan nganh",
    "bo cong an",
)
_QUOTA_QUERY_TERMS = ("chi tieu", "so luong")
_METHOD_QUERY_TERMS = ("phuong thuc",)
_TIMELINE_QUERY_TERMS = (
    "moc thoi gian",
    "thoi gian",
    "dang ky",
    "xac nhan nhap hoc",
    "nhap hoc",
)
_SCORE_QUERY_TERMS = ("diem chuan", "diem xet", "diem trung tuyen", "diem")
_EXAM_QUERY_TERMS = (
    "ma bai thi",
    "bai thi danh gia",
    "cau truc de thi",
    "cau truc bai thi",
)
_DOC_TYPE_HINTS = (
    ("quota", _QUOTA_QUERY_TERMS),
    ("methods", _METHOD_QUERY_TERMS),
    ("timeline", _TIMELINE_QUERY_TERMS),
    ("scores", _SCORE_QUERY_TERMS),
    ("exam", _EXAM_QUERY_TERMS),
)
_SCHOOL_CODE_HINTS = (
    ("T04", "ANS", ("truong dai hoc an ninh nhan dan", "t04", "ans")),
    ("T01", "ANH", ("hoc vien an ninh nhan dan", "t01", "anh")),
    ("T02", "CSH", ("hoc vien canh sat nhan dan", "t02", "csh")),
    ("T03", None, ("truong dai hoc canh sat nhan dan", "t03")),
    ("T05", None, ("t05",)),
    ("T06", None, ("truong dai hoc phong chay chua chay", "t06", "pccc")),
)
_SOURCE_AUTHORITY_BONUS = (
    ("dhannd.bocongan.gov.vn", 0.14, "school"),
    ("dhannd.edu.vn", 0.14, "school"),
    ("bocongan.gov.vn", 0.10, "ministry"),
    ("xaydungchinhsach.chinhphu.vn", 0.07, "government"),
    ("chinhphu.vn", 0.07, "government"),
    ("moet.gov.vn", 0.06, "moet"),
)


def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""

    normalized = unicodedata.normalize("NFD", str(value))
    normalized = normalized.replace("đ", "d").replace("Đ", "D")
    normalized = "".join(
        ch for ch in normalized if unicodedata.category(ch) != "Mn"
    ).lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _normalize_source_name(value: Optional[str]) -> str:
    if not value:
        return ""

    return _normalize_text(Path(str(value)).stem)


def _extract_year_from_text(value: Optional[str]) -> Optional[int]:
    if not value:
        return None

    years = [int(match) for match in _YEAR_PATTERN.findall(str(value))]
    if not years:
        return None

    plausible_years = [year for year in years if 2015 <= year <= 2100]
    if not plausible_years:
        return None

    return max(plausible_years)


def is_admission_query(query: Optional[str]) -> bool:
    normalized_query = _normalize_text(query)
    return any(term in normalized_query for term in _ADMISSION_TERMS)


def is_personnel_query(query: Optional[str]) -> bool:
    normalized_query = _normalize_text(query)
    return any(term in normalized_query for term in _PERSONNEL_TERMS)


def has_explicit_year(query: Optional[str]) -> bool:
    normalized_query = _normalize_text(query)
    return _extract_year_from_text(normalized_query) is not None


def query_targets_primary_school(query: Optional[str]) -> bool:
    normalized_query = _normalize_text(query)
    if not normalized_query:
        return False

    if any(term in normalized_query for term in _SYSTEM_WIDE_QUERY_TERMS):
        return False

    if any(term in normalized_query for term in _OTHER_SCHOOL_TERMS):
        return False

    if any(term in normalized_query for term in _PRIMARY_SCHOOL_TERMS):
        return True

    return is_admission_query(query)


def infer_target_year(query: Optional[str]) -> Optional[int]:
    normalized_query = _normalize_text(query)
    explicit_year = _extract_year_from_text(normalized_query)
    if explicit_year is not None:
        return explicit_year

    if not is_admission_query(query):
        return None

    current_year = dt.datetime.now().year
    if any(hint in normalized_query for hint in _CURRENT_CYCLE_HINTS):
        return current_year

    return current_year


def infer_query_doc_type(query: Optional[str]) -> Optional[str]:
    normalized_query = _normalize_text(query)
    if not normalized_query:
        return None

    for doc_type, terms in _DOC_TYPE_HINTS:
        if any(term in normalized_query for term in terms):
            return doc_type

    return None


def infer_document_metadata(
    source_name: Optional[str],
    source_url: Optional[str] = None,
    heading_text: Optional[str] = None,
    content: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_blob = " ".join(
        part
        for part in (
            _normalize_text(source_name),
            _normalize_text(source_url),
            _normalize_text(heading_text),
            _normalize_text(str(content or "")[:1600]),
        )
        if part
    ).strip()

    school_code = None
    school_symbol = None
    for candidate_code, candidate_symbol, terms in _SCHOOL_CODE_HINTS:
        if any(term in normalized_blob for term in terms):
            school_code = candidate_code
            school_symbol = candidate_symbol
            break

    if school_code == "T04" and not school_symbol:
        school_symbol = "ANS"

    if school_code:
        scope = "school_specific"
    elif any(term in normalized_blob for term in _SYSTEM_WIDE_DOC_TERMS):
        scope = "system_wide"
    else:
        scope = "general"

    admission_cycle = (
        _extract_year_from_text(source_name)
        or _extract_year_from_text(source_url)
        or _extract_year_from_text(heading_text)
        or _extract_year_from_text(content)
    )

    doc_type = None
    for candidate_doc_type, terms in _DOC_TYPE_HINTS:
        if any(term in normalized_blob for term in terms):
            doc_type = candidate_doc_type
            break

    return {
        "school_code": school_code,
        "school_symbol": school_symbol,
        "admission_cycle": admission_cycle,
        "scope": scope,
        "doc_type": doc_type or "general",
    }


def build_query_metadata_filters(query: Optional[str]) -> Dict[str, Any]:
    filters: Dict[str, Any] = {}
    if not query:
        return filters

    if query_targets_primary_school(query):
        filters["school_code"] = "T04"
        filters["school_symbol"] = "ANS"

    target_year = infer_target_year(query)
    if is_admission_query(query) and target_year is not None:
        filters["admission_cycle"] = target_year

    doc_type = infer_query_doc_type(query)
    if doc_type:
        filters["doc_type"] = doc_type

    return filters


def _build_current_cycle_query(raw_query: str, normalized_query: str) -> tuple[str, bool]:
    current_year = dt.datetime.now().year
    enrichment_terms = []

    current_year_phrase = f"nam {current_year}"
    if current_year_phrase not in normalized_query:
        enrichment_terms.append(f"nam {current_year}")

    if "ky tuyen sinh hien tai" not in normalized_query:
        enrichment_terms.append("ky tuyen sinh hien tai")

    if "tuyen sinh" not in normalized_query:
        enrichment_terms.append("tuyen sinh")

    enriched_query = " ".join(
        part for part in [raw_query, *enrichment_terms] if part
    ).strip()
    return enriched_query, enriched_query != raw_query


def enrich_query_for_current_cycle(query: Optional[str]) -> tuple[str, bool]:
    raw_query = str(query or "").strip()
    if not raw_query:
        return raw_query, False

    if not is_admission_query(raw_query) or has_explicit_year(raw_query):
        return raw_query, False

    normalized_query = _normalize_text(raw_query)
    return _build_current_cycle_query(raw_query, normalized_query)

    current_year = dt.datetime.now().year
    enrichment_terms = []

    current_year_phrase = f"nam {current_year}"
    if current_year_phrase not in normalized_query:
        enrichment_terms.append(f"năm {current_year}")

    if "ky tuyen sinh hien tai" not in normalized_query:
        enrichment_terms.append("kỳ tuyển sinh hiện tại")

    if "tuyen sinh" not in normalized_query:
        enrichment_terms.append("tuyển sinh")

    enriched_query = " ".join(
        part for part in [raw_query, *enrichment_terms] if part
    ).strip()
    return enriched_query, enriched_query != raw_query


def enrich_query_for_primary_school(query: Optional[str]) -> tuple[str, bool]:
    raw_query = str(query or "").strip()
    if not raw_query or not query_targets_primary_school(raw_query):
        return raw_query, False

    normalized_query = _normalize_text(raw_query)
    enrichment_terms = []

    if "truong dai hoc an ninh nhan dan" not in normalized_query:
        enrichment_terms.append("Truong Dai hoc An ninh Nhan dan")

    if "t04" not in normalized_query:
        enrichment_terms.append("T04")

    if "ans" not in normalized_query:
        enrichment_terms.append("ANS")

    enriched_query = " ".join(
        part for part in [raw_query, *enrichment_terms] if part
    ).strip()
    return enriched_query, enriched_query != raw_query


def _get_source_authority(domain: str) -> tuple[float, Optional[str]]:
    for host_suffix, bonus, label in _SOURCE_AUTHORITY_BONUS:
        if domain == host_suffix or domain.endswith(f".{host_suffix}"):
            return bonus, label
    return 0.0, None


@lru_cache(maxsize=1)
def _load_pdf_registry() -> Dict[str, Dict[str, Any]]:
    registry_path = _DATA_DIR / "pdf_urls.json"
    if not registry_path.exists():
        return {}

    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning(f"Could not parse PDF registry '{registry_path}': {exc}")
        return {}

    registry: Dict[str, Dict[str, Any]] = {}
    for entry in payload:
        name = entry.get("name")
        url = entry.get("url")
        normalized_name = _normalize_source_name(name)
        if not normalized_name or not url:
            continue

        domain = urlparse(url).netloc.lower()
        authority_bonus, authority_label = _get_source_authority(domain)
        year = _extract_year_from_text(name) or _extract_year_from_text(url)
        inferred_metadata = infer_document_metadata(name, source_url=url)
        current = registry.get(normalized_name)

        candidate = {
            "url": url,
            "domain": domain,
            "authority_bonus": authority_bonus,
            "authority_label": authority_label,
            "document_year": year,
            "school_code": inferred_metadata.get("school_code"),
            "school_symbol": inferred_metadata.get("school_symbol"),
            "admission_cycle": inferred_metadata.get("admission_cycle") or year,
            "scope": inferred_metadata.get("scope"),
            "doc_type": inferred_metadata.get("doc_type"),
        }

        if current is None:
            registry[normalized_name] = candidate
            continue

        current_score = (
            current.get("authority_bonus", 0.0),
            current.get("document_year") or 0,
        )
        candidate_score = (
            candidate.get("authority_bonus", 0.0),
            candidate.get("document_year") or 0,
        )
        if candidate_score >= current_score:
            registry[normalized_name] = candidate

    return registry


def resolve_source_metadata(source_name: Optional[str]) -> Dict[str, Any]:
    normalized_name = _normalize_source_name(source_name)
    metadata = dict(_load_pdf_registry().get(normalized_name, {}))

    if metadata:
        return metadata

    raw_source = str(source_name or "")
    domain = ""
    if raw_source.startswith("http://") or raw_source.startswith("https://"):
        domain = urlparse(raw_source).netloc.lower()

    authority_bonus, authority_label = _get_source_authority(domain)
    inferred_metadata = infer_document_metadata(raw_source, source_url=raw_source)
    return {
        "url": raw_source if domain else None,
        "domain": domain or None,
        "authority_bonus": authority_bonus,
        "authority_label": authority_label,
        "document_year": _extract_year_from_text(raw_source),
        "school_code": inferred_metadata.get("school_code"),
        "school_symbol": inferred_metadata.get("school_symbol"),
        "admission_cycle": inferred_metadata.get("admission_cycle"),
        "scope": inferred_metadata.get("scope"),
        "doc_type": inferred_metadata.get("doc_type"),
    }


def enrich_chunk_source_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    source_name = chunk.get("source_file") or chunk.get("source") or ""
    metadata = resolve_source_metadata(source_name)
    inferred_chunk_metadata = infer_document_metadata(
        source_name,
        source_url=metadata.get("url"),
        heading_text=chunk.get("heading_text") or chunk.get("heading"),
        content=chunk.get("content"),
    )

    if not chunk.get("document_year"):
        document_year = metadata.get("document_year") or _extract_year_from_text(
            source_name
        )
        if document_year is not None:
            chunk["document_year"] = document_year

    if not chunk.get("source_url") and metadata.get("url"):
        chunk["source_url"] = metadata["url"]

    if not chunk.get("source_authority") and metadata.get("authority_label"):
        chunk["source_authority"] = metadata["authority_label"]

    for field in ("school_code", "school_symbol", "scope", "doc_type"):
        if not chunk.get(field) and inferred_chunk_metadata.get(field):
            chunk[field] = inferred_chunk_metadata[field]

    admission_cycle = (
        chunk.get("admission_cycle")
        or inferred_chunk_metadata.get("admission_cycle")
        or chunk.get("document_year")
        or metadata.get("admission_cycle")
        or metadata.get("document_year")
    )
    if admission_cycle is not None and not chunk.get("admission_cycle"):
        chunk["admission_cycle"] = admission_cycle

    return metadata


def filter_chunks_by_metadata(
    query: Optional[str], chunks: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not chunks:
        return chunks, {"applied": False, "stage": "empty"}

    filters = build_query_metadata_filters(query)
    if not filters:
        for chunk in chunks:
            enrich_chunk_source_metadata(chunk)
        return chunks, {"applied": False, "stage": "no_filters"}

    for chunk in chunks:
        enrich_chunk_source_metadata(chunk)

    school_code = filters.get("school_code")
    admission_cycle = filters.get("admission_cycle")
    doc_type = filters.get("doc_type")
    allow_system_wide = doc_type in {"methods", "timeline", "exam"}

    def _match(
        chunk: Dict[str, Any],
        *,
        require_school: bool = False,
        require_cycle: bool = False,
        require_doc_type: bool = False,
        allow_system_scope: bool = False,
    ) -> bool:
        if require_school and school_code:
            if chunk.get("school_code") != school_code:
                if not (
                    allow_system_scope and chunk.get("scope") == "system_wide"
                ):
                    return False

        if require_cycle and admission_cycle is not None:
            if chunk.get("admission_cycle") != admission_cycle:
                return False

        if require_doc_type and doc_type:
            if chunk.get("doc_type") != doc_type:
                return False

        return True

    candidate_stages = [
        (
            "strict_school_cycle_doc_type",
            dict(
                require_school=bool(school_code),
                require_cycle=bool(admission_cycle),
                require_doc_type=bool(doc_type),
                allow_system_scope=False,
            ),
        ),
        (
            "school_doc_type",
            dict(
                require_school=bool(school_code),
                require_cycle=False,
                require_doc_type=bool(doc_type),
                allow_system_scope=False,
            ),
        ),
    ]

    if school_code:
        candidate_stages.append(
            (
                "school_only",
                dict(
                    require_school=True,
                    require_cycle=False,
                    require_doc_type=False,
                    allow_system_scope=allow_system_wide,
                ),
            )
        )

    if doc_type:
        candidate_stages.append(
            (
                "doc_type_only",
                dict(
                    require_school=False,
                    require_cycle=False,
                    require_doc_type=True,
                    allow_system_scope=False,
                ),
            )
        )

    for stage_name, stage_kwargs in candidate_stages:
        filtered = [chunk for chunk in chunks if _match(chunk, **stage_kwargs)]
        if filtered:
            return filtered, {
                "applied": True,
                "stage": stage_name,
                "filters": filters,
                "matched": len(filtered),
                "total": len(chunks),
            }

    return chunks, {
        "applied": False,
        "stage": "fallback_original",
        "filters": filters,
        "matched": len(chunks),
        "total": len(chunks),
    }


def compute_priority_adjustment(query: Optional[str], chunk: Dict[str, Any]) -> float:
    source_name = chunk.get("source_file") or chunk.get("source") or ""
    normalized_source = _normalize_text(source_name)
    normalized_heading = _normalize_text(chunk.get("heading_text") or chunk.get("heading"))
    normalized_content = _normalize_text(str(chunk.get("content") or "")[:1600])
    normalized_chunk_text = " ".join(
        part for part in (normalized_source, normalized_heading, normalized_content) if part
    ).strip()
    metadata = enrich_chunk_source_metadata(chunk)

    target_year = infer_target_year(query)
    document_year = chunk.get("document_year")
    authority_bonus = float(metadata.get("authority_bonus") or 0.0)
    personnel_query = is_personnel_query(query)
    primary_school_query = query_targets_primary_school(query)

    year_bonus = 0.0
    if target_year is not None and document_year is not None:
        year_gap = document_year - target_year
        if year_gap == 0:
            year_bonus = 0.22
        elif year_gap == -1:
            year_bonus = 0.05
        elif year_gap > 0:
            year_bonus = 0.08
        else:
            year_bonus = max(-0.18, year_gap * 0.05)

    title_bonus = 0.04 if any(term in normalized_source for term in _ADMISSION_DOC_TERMS) else 0.0
    personnel_bonus = 0.0
    if personnel_query:
        if any(term in normalized_source for term in _PERSONNEL_DOC_STRONG_TERMS):
            personnel_bonus += 0.28
        elif any(term in normalized_source for term in _PERSONNEL_DOC_TERMS):
            personnel_bonus += 0.16

        if personnel_bonus and any(
            term in normalized_source for term in _UPDATED_DOC_TERMS
        ):
            personnel_bonus += 0.08

    school_bonus = 0.0
    if primary_school_query:
        if any(
            term in normalized_chunk_text for term in _PRIMARY_SCHOOL_STRONG_DOC_TERMS
        ):
            school_bonus += 0.22
        elif "an ninh nhan dan" in normalized_chunk_text:
            school_bonus += 0.12

        if any(term in normalized_chunk_text for term in _OTHER_SCHOOL_TERMS):
            school_bonus -= 0.18

        if school_bonus <= 0 and any(
            term in normalized_chunk_text for term in _SYSTEM_WIDE_DOC_TERMS
        ):
            school_bonus -= 0.10

    draft_penalty = -0.08 if any(term in normalized_source for term in _DRAFT_TERMS) else 0.0

    total_adjustment = (
        year_bonus
        + authority_bonus
        + title_bonus
        + personnel_bonus
        + school_bonus
        + draft_penalty
    )
    chunk["priority_adjustment"] = round(total_adjustment, 4)
    return total_adjustment
