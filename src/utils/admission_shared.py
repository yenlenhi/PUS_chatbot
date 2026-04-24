"""
Shared admission helpers for text normalization and school matching.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Sequence

_ALPHANUMERIC_PATTERN = re.compile(r"[^a-z0-9]+")

SCHOOL_CATALOG: tuple[Dict[str, Any], ...] = (
    {
        "code": "T01",
        "symbol": "ANH",
        "name": "Hoc vien An ninh nhan dan",
        "query_aliases": ("hoc vien an ninh nhan dan", "t01", "anh"),
        "content_aliases": ("hoc vien an ninh nhan dan", "t01", "anh"),
    },
    {
        "code": "T02",
        "symbol": "CSH",
        "name": "Hoc vien Canh sat nhan dan",
        "query_aliases": ("hoc vien canh sat nhan dan", "t02", "csh"),
        "content_aliases": ("hoc vien canh sat nhan dan", "t02", "csh"),
    },
    {
        "code": "T03",
        "symbol": "CTC",
        "name": "Hoc vien Chinh tri CAND",
        "query_aliases": ("hoc vien chinh tri cand", "hoc vien chinh tri cong an nhan dan", "t03", "ctc"),
        "content_aliases": ("hoc vien chinh tri cand", "hoc vien chinh tri cong an nhan dan", "t03", "ctc"),
    },
    {
        "code": "T04",
        "symbol": "ANS",
        "name": "Truong Dai hoc An ninh nhan dan",
        "query_aliases": ("truong dai hoc an ninh nhan dan", "an ninh nhan dan", "annd", "t04", "ans"),
        "content_aliases": ("truong dai hoc an ninh nhan dan", "an ninh nhan dan", "annd", "t04", "ans"),
    },
    {
        "code": "T05",
        "symbol": None,
        "name": "Truong Dai hoc Canh sat nhan dan",
        "query_aliases": ("truong dai hoc canh sat nhan dan", "t05"),
        "content_aliases": ("truong dai hoc canh sat nhan dan", "t05"),
    },
    {
        "code": "T06",
        "symbol": None,
        "name": "Truong Dai hoc Phong chay chua chay",
        "query_aliases": ("truong dai hoc phong chay chua chay", "truong dai hoc pccc", "t06", "pccc"),
        "content_aliases": ("truong dai hoc phong chay chua chay", "truong dai hoc pccc", "t06", "pccc"),
    },
    {
        "code": "T07",
        "symbol": None,
        "name": "Hoc vien Ky thuat va Cong nghe an ninh",
        "query_aliases": ("hoc vien ky thuat va cong nghe an ninh", "t07"),
        "content_aliases": ("hoc vien ky thuat va cong nghe an ninh", "t07"),
    },
    {
        "code": "B06",
        "symbol": "HVQT",
        "name": "Hoc vien Quoc te",
        "query_aliases": ("hoc vien quoc te", "b06", "hvqt", "hvtmqt"),
        "content_aliases": ("hoc vien quoc te", "b06", "hvqt", "hvtmqt"),
    },
    {
        "code": "T08",
        "symbol": None,
        "name": "Truong Cao dang An ninh nhan dan I",
        "query_aliases": ("truong cao dang an ninh nhan dan i", "t08"),
        "content_aliases": ("truong cao dang an ninh nhan dan i", "t08"),
    },
    {
        "code": "T09",
        "symbol": None,
        "name": "Truong Cao dang Canh sat nhan dan I",
        "query_aliases": ("truong cao dang canh sat nhan dan i", "t09"),
        "content_aliases": ("truong cao dang canh sat nhan dan i", "t09"),
    },
    {
        "code": "T10",
        "symbol": None,
        "name": "Truong Cao dang Canh sat nhan dan II",
        "query_aliases": ("truong cao dang canh sat nhan dan ii", "t10"),
        "content_aliases": ("truong cao dang canh sat nhan dan ii", "t10"),
    },
    {
        "code": "T11",
        "symbol": None,
        "name": "Truong Van hoa",
        "query_aliases": ("truong van hoa", "t11"),
        "content_aliases": ("truong van hoa", "t11"),
    },
)

SCHOOL_ORDER = {
    school["code"]: index for index, school in enumerate(SCHOOL_CATALOG)
}


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""

    normalized = unicodedata.normalize("NFD", str(value))
    normalized = (
        normalized.replace("đ", "d")
        .replace("Đ", "D")
        .replace("Ä‘", "d")
        .replace("Ä", "D")
        .replace("Ã„â€˜", "d")
        .replace("Ã„Â", "D")
    )
    normalized = "".join(
        ch for ch in normalized if unicodedata.category(ch) != "Mn"
    ).lower()
    normalized = _ALPHANUMERIC_PATTERN.sub(" ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _matches_school_alias(normalized_value: str, alias: str) -> bool:
    normalized_alias = normalize_text(alias)
    if not normalized_alias:
        return False

    padded_value = f" {normalized_value} "
    padded_alias = f" {normalized_alias} "

    if normalized_alias.startswith(("t", "b")) and normalized_alias[1:].isdigit():
        return padded_alias in padded_value

    if len(normalized_alias) <= 4:
        return padded_alias in padded_value

    return normalized_alias in normalized_value


def find_matching_schools(
    value: Optional[str], *, alias_field: str = "query_aliases"
) -> List[Dict[str, Any]]:
    normalized_value = normalize_text(value)
    if not normalized_value:
        return []

    matched: List[Dict[str, Any]] = []
    for school in SCHOOL_CATALOG:
        aliases: Sequence[str] = school.get(alias_field) or ()
        if any(_matches_school_alias(normalized_value, alias) for alias in aliases):
            matched.append(school)
    return matched


def match_school(
    value: Optional[str], *, alias_field: str = "query_aliases"
) -> Optional[Dict[str, Any]]:
    matches = find_matching_schools(value, alias_field=alias_field)
    return matches[0] if matches else None


def build_school_metadata(
    school: Optional[Dict[str, Any]],
) -> Dict[str, Optional[str]]:
    if not school:
        return {"school_code": None, "school_symbol": None}

    return {
        "school_code": school["code"],
        "school_symbol": school.get("symbol"),
    }


__all__ = [
    "SCHOOL_CATALOG",
    "SCHOOL_ORDER",
    "build_school_metadata",
    "find_matching_schools",
    "match_school",
    "normalize_text",
]
