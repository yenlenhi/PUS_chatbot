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
from typing import Any, Dict, Optional
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
)
_ADMISSION_DOC_TERMS = (
    "tuyen sinh",
    "chi tieu",
    "thong bao",
    "huong dan",
    "de an",
)
_CURRENT_CYCLE_HINTS = (
    "nam nay",
    "moi nhat",
    "hien tai",
    "dot nay",
    "ky nay",
)
_DRAFT_TERMS = ("du thao", "draft")
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
        current = registry.get(normalized_name)

        candidate = {
            "url": url,
            "domain": domain,
            "authority_bonus": authority_bonus,
            "authority_label": authority_label,
            "document_year": year,
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
    return {
        "url": raw_source if domain else None,
        "domain": domain or None,
        "authority_bonus": authority_bonus,
        "authority_label": authority_label,
        "document_year": _extract_year_from_text(raw_source),
    }


def enrich_chunk_source_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    source_name = chunk.get("source_file") or chunk.get("source") or ""
    metadata = resolve_source_metadata(source_name)

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

    return metadata


def compute_priority_adjustment(query: Optional[str], chunk: Dict[str, Any]) -> float:
    source_name = chunk.get("source_file") or chunk.get("source") or ""
    normalized_source = _normalize_text(source_name)
    metadata = enrich_chunk_source_metadata(chunk)

    target_year = infer_target_year(query)
    document_year = chunk.get("document_year")
    authority_bonus = float(metadata.get("authority_bonus") or 0.0)

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
    draft_penalty = -0.08 if any(term in normalized_source for term in _DRAFT_TERMS) else 0.0

    total_adjustment = year_bonus + authority_bonus + title_bonus + draft_penalty
    chunk["priority_adjustment"] = round(total_adjustment, 4)
    return total_adjustment
