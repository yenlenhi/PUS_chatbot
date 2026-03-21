"""
Guardrails and structured answer helpers for admission-specific responses.
"""

from __future__ import annotations

import datetime as dt
import re
import unicodedata
from typing import Any, Dict, List, Optional

from src.utils.admission_document_priority import (
    build_query_metadata_filters,
    has_explicit_year,
    infer_query_doc_type,
    infer_target_year,
    is_admission_query,
    query_targets_primary_school,
)
from src.utils.fixed_admission_faq import get_fixed_admission_faq

_DATE_RANGE_PATTERN = re.compile(
    r"(\d{1,2}/\d{1,2}(?:/\d{4})?)\s*(?:den|-|to)\s*(\d{1,2}/\d{1,2}(?:/\d{4})?)",
    re.IGNORECASE,
)
_DATE_SINGLE_PATTERN = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")
_SCORE_ROW_PATTERN = re.compile(
    r"\b(20\d{2})\b.*?\b(\d{2}(?:[.,]\d{1,2})?)\b",
    re.IGNORECASE,
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


def _answer_mentions_system_wide_context(answer: str) -> bool:
    normalized = _normalize_text(answer)
    return any(
        phrase in normalized
        for phrase in (
            "toan khoi cand",
            "cac truong cand",
            "toan he thong",
            "toan bo cac truong cand",
            "tong chi tieu cua cac truong cand",
        )
    )


def validate_admission_answer(
    query: str, answer: str, relevant_chunks: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    violations: List[str] = []
    normalized_answer = _normalize_text(answer)

    if query_targets_primary_school(query) and re.search(r"\bt05\b", normalized_answer):
        violations.append("wrong_school_code_t05")

    compact_answer = normalized_answer.replace(" ", "")
    if query_targets_primary_school(query) and (
        "1870" in compact_answer or "1.870" in answer
    ):
        if not _answer_mentions_system_wide_context(answer):
            violations.append("system_wide_quota_presented_as_t04")

    target_year = infer_target_year(query)
    current_year = dt.datetime.now().year
    if (
        is_admission_query(query)
        and not has_explicit_year(query)
        and target_year == current_year
        and "2025" in normalized_answer
    ):
        if not any(
            marker in normalized_answer
            for marker in (
                "tham khao cu",
                "doi chieu",
                "so sanh",
                "khong du co so",
                "khong du can cu",
                "tai lieu cu",
            )
        ):
            violations.append("older_year_presented_as_current")

    return violations


def build_answer_repair_prompt(
    query: str,
    context: str,
    draft_answer: str,
    violations: List[str],
    language: str = "vi",
) -> str:
    if language == "en":
        return f"""You must repair the draft answer so it complies with all policy violations below.

User query:
{query}

Official document context:
{context}

Draft answer:
{draft_answer}

Violations to fix:
- {'; '.join(violations)}

Rules:
- Keep the answer grounded only in the provided documents.
- If the query is about People's Security University by default, do not mention T05.
- Do not present the whole-system CAND quota 1,870 as if it were T04-specific.
- If the user did not specify a year, treat the question as the current cycle year {dt.datetime.now().year}.
- If the documents are insufficient, state that clearly instead of guessing.
- Prefer Markdown tables for quota, methods, timeline, and score questions.
"""

    return f"""Hãy sửa lại bản nháp câu trả lời dưới đây để loại bỏ toàn bộ lỗi chính sách.

Câu hỏi của người dùng:
{query}

Ngữ cảnh tài liệu chính thức:
{context}

Bản nháp hiện tại:
{draft_answer}

Các lỗi cần sửa:
- {'; '.join(violations)}

Yêu cầu bắt buộc:
- Chỉ được dùng thông tin có trong tài liệu đã cung cấp.
- Nếu câu hỏi mặc định thuộc phạm vi Trường Đại học An ninh nhân dân, tuyệt đối không được ghi T05.
- Không được trình bày 1.870 chỉ tiêu như thể là chỉ tiêu riêng của T04.
- Nếu người dùng không nêu năm, phải hiểu theo chu kỳ tuyển sinh hiện tại năm {dt.datetime.now().year}.
- Nếu tài liệu không đủ căn cứ, phải nói rõ là chưa đủ căn cứ thay vì suy đoán.
- Với câu hỏi về chỉ tiêu, phương thức, mốc thời gian, điểm số, ưu tiên trình bày bằng bảng Markdown.
"""


def build_safe_admission_fallback_answer(
    query: str, violations: List[str], language: str = "vi"
) -> str:
    if language == "en":
        return (
            "I do not have enough safe evidence to confirm this answer from the current "
            "document set. For People's Security University (T04), I should only present "
            "T04-specific and current-cycle information, so I am withholding the unsupported claim."
        )

    notices: List[str] = []
    if "wrong_school_code_t05" in violations:
        notices.append(
            "- Trường Đại học An ninh nhân dân là **T04**, không phải T05."
        )
    if "system_wide_quota_presented_as_t04" in violations:
        notices.append(
            "- Con số **1.870 chỉ tiêu** là thông tin của toàn khối/trường CAND, không phải chỉ tiêu riêng của T04."
        )
    if "older_year_presented_as_current" in violations:
        notices.append(
            f"- Câu hỏi không nêu năm nên phải ưu tiên chu kỳ tuyển sinh hiện tại **{dt.datetime.now().year}**."
        )

    notice_block = "\n".join(notices) if notices else "- Câu trả lời hiện tại chưa đủ căn cứ an toàn."
    return (
        "Tôi chưa đủ căn cứ an toàn để khẳng định nội dung này từ bộ tài liệu hiện tại.\n\n"
        f"{notice_block}\n\n"
        "Vui lòng xem các tài liệu tuyển sinh chính thức mà hệ thống đã ưu tiên hiển thị cho T04."
    )


def _build_timeline_answer(query: str, chunks: List[Dict[str, Any]]) -> Optional[str]:
    rows: List[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()

    for chunk in chunks[:5]:
        content = str(chunk.get("content") or "")
        for raw_line in content.splitlines():
            line = raw_line.strip(" -•\t")
            if len(line) < 12:
                continue
            normalized_line = _normalize_text(line)
            if not any(
                keyword in normalized_line
                for keyword in (
                    "dang ky",
                    "xet tuyen",
                    "nhap hoc",
                    "xac nhan nhap hoc",
                    "du tuyen",
                    "chieu sinh",
                )
            ):
                continue

            label = line.split(":", 1)[0].strip()
            note = ""
            timeline_text = line
            match_range = _DATE_RANGE_PATTERN.search(line)
            if match_range:
                timeline_text = f"{match_range.group(1)} đến {match_range.group(2)}"
                note = line.replace(match_range.group(0), "").replace(":", " ").strip()
            else:
                dates = _DATE_SINGLE_PATTERN.findall(line)
                if dates:
                    timeline_text = ", ".join(dates)
                    note = line
            key = (label, timeline_text)
            if timeline_text and key not in seen:
                seen.add(key)
                rows.append((label, timeline_text, note))

    if len(rows) < 2:
        return None

    lines = [
        "### Mốc thời gian tuyển sinh",
        "",
        "Dưới đây là các mốc thời gian nổi bật tôi trích được từ tài liệu tuyển sinh liên quan:",
        "",
        "| Mốc | Thời gian | Ghi chú |",
        "| --- | --- | --- |",
    ]
    for label, timeline_text, note in rows[:8]:
        safe_note = note.replace("|", "/")
        lines.append(f"| {label} | {timeline_text} | {safe_note} |")

    return "\n".join(lines)


def _build_score_answer(query: str, chunks: List[Dict[str, Any]]) -> Optional[str]:
    rows: List[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str]] = set()

    for chunk in chunks[:6]:
        heading = (chunk.get("heading_text") or chunk.get("heading") or "").strip()
        major = heading or "Ngành/nhóm ngành"
        content = str(chunk.get("content") or "")
        for raw_line in content.splitlines():
            line = raw_line.strip(" -•\t")
            if len(line) < 8:
                continue
            match = _SCORE_ROW_PATTERN.search(line)
            if not match:
                continue
            year, score = match.group(1), match.group(2).replace(",", ".")
            key = (year, score)
            if key in seen:
                continue
            seen.add(key)
            rows.append((year, major, score, "Theo tài liệu truy xuất"))

    if not rows:
        return None

    rows.sort(key=lambda item: item[0])
    lines = [
        "### Bảng điểm tuyển sinh",
        "",
        "Tôi đã chuẩn hóa các mốc điểm truy xuất được dưới dạng bảng để dễ đối chiếu:",
        "",
        "| Năm | Ngành/Mã ngành | Điểm | Ghi chú |",
        "| --- | --- | ---: | --- |",
    ]
    for year, major, score, note in rows[:10]:
        lines.append(f"| {year} | {major or 'Ngành/nhóm ngành'} | {score} | {note} |")

    return "\n".join(lines)


def build_structured_admission_answer(
    query: str, chunks: List[Dict[str, Any]], language: str = "vi"
) -> Optional[str]:
    if language != "vi":
        return None

    faq = get_fixed_admission_faq(query)
    if faq:
        return faq["answer"]

    doc_type = infer_query_doc_type(query)
    if doc_type == "timeline":
        return _build_timeline_answer(query, chunks)
    if doc_type == "scores":
        return _build_score_answer(query, chunks)

    return None


def should_use_structured_pipeline(query: str) -> bool:
    doc_type = infer_query_doc_type(query)
    return doc_type in {"quota", "methods", "timeline", "scores", "exam"}


def get_structured_answer_metadata(query: str) -> Dict[str, Any]:
    filters = build_query_metadata_filters(query)
    return {
        "doc_type": filters.get("doc_type"),
        "filters": filters,
        "structured": should_use_structured_pipeline(query),
    }
