"""
Quota-specific matching and structured answer builders for admission answers.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from src.utils.admission_answer_normalization import (
    extract_table_cells,
    is_table_separator_cells,
    normalize_answer_markdown,
    repair_mojibake_text,
)
from src.utils.admission_document_priority import (
    infer_document_metadata,
    query_prefers_system_wide_scope,
    query_targets_primary_school,
)
from src.utils.admission_shared import (
    SCHOOL_ORDER,
    match_school,
    normalize_text,
)

_QUOTA_QUERY_TERMS = ("chi tieu", "so luong", "quota")
_QUOTA_MIXED_QUERY_TERMS = (
    "to hop",
    "phuong thuc",
    "moc thoi gian",
    "lich trinh",
    "ho so",
    "dieu kien",
    "diem chuan",
    "diem xet",
    "diem trung tuyen",
)
_QUOTA_NUMBER_PATTERN = re.compile(r"\b\d{1,4}\b")


def should_use_structured_quota_pipeline(query: str) -> bool:
    normalized_query = normalize_text(query)
    if not normalized_query:
        return False

    if not any(term in normalized_query for term in _QUOTA_QUERY_TERMS):
        return False

    return not any(term in normalized_query for term in _QUOTA_MIXED_QUERY_TERMS)


def _infer_requested_school(query: str) -> Optional[Dict[str, Any]]:
    school = match_school(query, alias_field="content_aliases")
    if school:
        return school

    if query_targets_primary_school(query):
        return match_school("t04", alias_field="content_aliases")

    return None


def _beautify_text(value: str) -> str:
    cleaned = repair_mojibake_text(str(value or "")).strip(" |:;-")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _normalize_header(cell: str) -> str:
    normalized = normalize_text(cell)
    if "ten truong" in normalized or normalized in {"truong", "hoc vien", "don vi"}:
        return "school_name"
    if "ma truong" in normalized:
        return "school_code"
    if "ky hieu truong" in normalized:
        return "school_symbol"
    if "tong chi tieu" in normalized or normalized == "chi tieu":
        return "total_quota"
    if normalized in {"nam", "chi tieu nam"}:
        return "male_quota"
    if normalized in {"nu", "chi tieu nu"}:
        return "female_quota"
    if "pt1" in normalized and "nam" in normalized:
        return "pt1_male"
    if "pt1" in normalized and "nu" in normalized:
        return "pt1_female"
    if any(term in normalized for term in ("pt2 pt3", "pt2, pt3", "pt2 pt 3")) and "nam" in normalized:
        return "pt23_male"
    if any(term in normalized for term in ("pt2 pt3", "pt2, pt3", "pt2 pt 3")) and "nu" in normalized:
        return "pt23_female"
    if "ma nganh" in normalized:
        return "major_code"
    if "dia ban" in normalized or "vung tuyen sinh" in normalized:
        return "region"
    if "to hop" in normalized:
        return "combinations"
    if "ma bai thi" in normalized:
        return "exam_codes"
    return ""


def _iter_table_blocks(text: str) -> Iterable[List[str]]:
    normalized_text = normalize_answer_markdown(repair_mojibake_text(text or ""))
    current_block: List[str] = []

    for raw_line in normalized_text.splitlines():
        stripped = raw_line.strip()
        if stripped.count("|") >= 2:
            table_line = stripped
            if not table_line.startswith("|"):
                table_line = f"| {table_line.strip('| ')} |"
            current_block.append(table_line)
            continue

        if current_block:
            yield current_block
            current_block = []

    if current_block:
        yield current_block


def _parse_int(value: str) -> Optional[int]:
    digits = re.sub(r"[^\d]", "", str(value or ""))
    if not digits:
        return None
    return int(digits)


def _infer_school_from_text(value: str) -> Optional[Dict[str, Any]]:
    return match_school(value, alias_field="content_aliases")


def _extract_system_rows_from_table(
    block: List[str],
    chunk: Dict[str, Any],
) -> List[Dict[str, Any]]:
    parsed_rows: List[List[str]] = []
    for line in block:
        cells = extract_table_cells(line)
        if not cells or is_table_separator_cells(cells):
            continue
        parsed_rows.append(cells)

    if len(parsed_rows) < 2:
        return []

    raw_headers = parsed_rows[0]
    headers = [_normalize_header(cell) for cell in raw_headers]
    if not {"school_name", "total_quota", "male_quota", "female_quota"}.issubset(headers):
        return []

    row_count = len(raw_headers)
    metadata = infer_document_metadata(
        chunk.get("source_file") or chunk.get("source"),
        heading_text=chunk.get("heading_text") or chunk.get("heading"),
        content=chunk.get("content"),
    )
    records: List[Dict[str, Any]] = []

    for raw_row in parsed_rows[1:]:
        cells = raw_row[:row_count] + [""] * max(0, row_count - len(raw_row))
        row_map = {
            header: _beautify_text(value)
            for header, value in zip(headers, cells)
            if header
        }
        school = _infer_school_from_text(" ".join(cells))
        total = _parse_int(row_map.get("total_quota", ""))
        male = _parse_int(row_map.get("male_quota", ""))
        female = _parse_int(row_map.get("female_quota", ""))

        if not school or total is None or male is None or female is None:
            continue

        name = row_map.get("school_name") or school["name"]
        code = row_map.get("school_code") or school["code"]
        records.append(
            {
                "school_name": name,
                "school_code": code,
                "total_quota": total,
                "male_quota": male,
                "female_quota": female,
                "scope": chunk.get("scope") or metadata.get("scope"),
                "source_file": chunk.get("source_file") or chunk.get("source"),
                "sum_matches": total == male + female,
            }
        )

    return records


def _choose_quota_triplet(numbers: List[int]) -> Optional[Tuple[int, int, int]]:
    if len(numbers) < 3:
        return None

    filtered = [number for number in numbers if number < 1900]
    if len(filtered) < 3:
        filtered = numbers

    for index in range(len(filtered) - 2):
        total, male, female = filtered[index : index + 3]
        if total == male + female:
            return total, male, female

    if len(filtered) >= 3:
        return tuple(filtered[:3])  # type: ignore[return-value]

    return None


def _extract_system_rows_from_text(
    text: str, chunk: Dict[str, Any]
) -> List[Dict[str, Any]]:
    metadata = infer_document_metadata(
        chunk.get("source_file") or chunk.get("source"),
        heading_text=chunk.get("heading_text") or chunk.get("heading"),
        content=chunk.get("content"),
    )
    rows: List[Dict[str, Any]] = []

    for raw_line in repair_mojibake_text(text or "").splitlines():
        line = _beautify_text(raw_line)
        if not line:
            continue

        school = _infer_school_from_text(line)
        if not school:
            continue

        compact = re.sub(r"\b(?:T|B)\d{2}\b", " ", line, flags=re.IGNORECASE)
        numbers = [int(value) for value in _QUOTA_NUMBER_PATTERN.findall(compact)]
        triplet = _choose_quota_triplet(numbers)
        if not triplet:
            continue

        total, male, female = triplet
        rows.append(
            {
                "school_name": school["name"],
                "school_code": school["code"],
                "total_quota": total,
                "male_quota": male,
                "female_quota": female,
                "scope": chunk.get("scope") or metadata.get("scope"),
                "source_file": chunk.get("source_file") or chunk.get("source"),
                "sum_matches": total == male + female,
            }
        )

    return rows


def _dedupe_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deduped: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        code = str(row.get("school_code") or "").upper()
        if not code:
            continue

        current = deduped.get(code)
        if current is None:
            deduped[code] = row
            continue

        current_score = (
            int(bool(current.get("sum_matches"))),
            current.get("scope") == "system_wide",
        )
        candidate_score = (
            int(bool(row.get("sum_matches"))),
            row.get("scope") == "system_wide",
        )
        if candidate_score >= current_score:
            deduped[code] = row

    return list(deduped.values())


def _extract_system_wide_rows(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for chunk in chunks[:8]:
        content = str(chunk.get("content") or "")
        for block in _iter_table_blocks(content):
            rows.extend(_extract_system_rows_from_table(block, chunk))
        rows.extend(_extract_system_rows_from_text(content, chunk))

    deduped_rows = _dedupe_rows(rows)
    deduped_rows.sort(
        key=lambda row: (
            SCHOOL_ORDER.get(str(row.get("school_code") or "").upper(), 999),
            str(row.get("school_name") or ""),
        )
    )
    return deduped_rows


def build_structured_quota_answer(
    query: str, chunks: List[Dict[str, Any]]
) -> Optional[str]:
    requested_school = _infer_requested_school(query)
    prefers_system_wide = query_prefers_system_wide_scope(query)
    rows = _extract_system_wide_rows(chunks)
    if not rows:
        return None

    if requested_school:
        rows = [
            row
            for row in rows
            if str(row.get("school_code") or "").upper() == requested_school["code"]
        ]
        if not rows:
            return None
    elif prefers_system_wide:
        system_rows = [row for row in rows if row.get("scope") == "system_wide"]
        if len(system_rows) >= 2:
            rows = system_rows

    if requested_school and len(rows) > 1:
        rows = rows[:1]

    if not rows:
        return None

    title = (
        f"### Chi tieu tuyen sinh cua {requested_school['name']}"
        if requested_school
        else "### Chi tieu tuyen sinh theo truong"
    )
    intro = (
        "Duoi day la dong chi tieu toi trich duoc tu tai lieu tuyen sinh lien quan:"
        if requested_school
        else "Duoi day la bang chi tieu toi trich duoc tu tai lieu tuyen sinh toan he thong CAND/Bo Cong an lien quan:"
    )

    lines = [
        title,
        "",
        intro,
        "",
        "| Ten truong | Ma truong | Tong chi tieu | Nam | Nu |",
        "| --- | --- | ---: | ---: | ---: |",
    ]

    total_quota = 0
    total_male = 0
    total_female = 0
    for row in rows:
        total_quota += int(row["total_quota"])
        total_male += int(row["male_quota"])
        total_female += int(row["female_quota"])
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["school_name"]),
                    str(row["school_code"]).upper(),
                    str(row["total_quota"]),
                    str(row["male_quota"]),
                    str(row["female_quota"]),
                ]
            )
            + " |"
        )

    if len(rows) > 1:
        lines.extend(
            [
                "",
                (
                    "Tong cong trong cac dong toi trich duoc: "
                    f"**{total_quota}** chi tieu, gom **{total_male} nam** va **{total_female} nu**."
                ),
            ]
        )

    return "\n".join(lines)


__all__ = [
    "build_structured_quota_answer",
    "should_use_structured_quota_pipeline",
]
