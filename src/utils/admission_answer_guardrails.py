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
_YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
_SCORE_VALUE_PATTERN = re.compile(r"\b\d{2}(?:[.,]\d{1,2})?\b")
_INLINE_TABLE_PATTERN = re.compile(r"([^\n])(\|(?:[^|\n]+\|){2,}.*)")
_TABLE_SEPARATOR_PATTERN = re.compile(r"^:?-{3,}:?$")
_TIMELINE_ACTION_KEYWORDS = (
    "dang ky",
    "xet tuyen",
    "nhap hoc",
    "xac nhan nhap hoc",
    "du tuyen",
    "chieu sinh",
    "trung tuyen",
)
_TIMELINE_RELATIVE_DATE_PATTERN = re.compile(
    r"\b(?:truoc|sau|vao|tu|den|hoan thanh truoc|du kien vao)\s+\d{1,2}/\d{1,2}/\d{4}\b",
    re.IGNORECASE,
)
_TIMELINE_DURATION_PATTERN = re.compile(
    r"\b(?:trong vong|khong qua)\s+\d+\s+ngay(?:\s+lam viec)?\b",
    re.IGNORECASE,
)
_TIMELINE_OUTLINE_PREFIX_PATTERN = re.compile(
    r"^\s*(?:\d+[.)]|[a-z][.)]|[ivxlcdm]+[.)])\s*",
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


def _answer_acknowledges_reference_year(answer: str, reference_year: int) -> bool:
    normalized = _normalize_text(answer)
    year_phrase = str(reference_year)

    reference_markers = (
        "tham khao",
        "lam co so",
        "tam thoi",
        "tai lieu hien co",
        "tai lieu duoc cung cap",
        "chi de cap",
        "chi thong tin",
        "chua co tai lieu",
        "chua co van ban",
        "chua du can cu xac nhan",
        "chua du co so xac nhan",
        "chua xac nhan chinh thuc",
        "se duoc cap nhat",
        "theo huong dan moi nhat",
        "huong dan moi nhat",
        "doi chieu",
        "so sanh",
        "tai lieu cu",
        "nam truoc",
        "gan nhat",
    )

    has_reference_marker = any(marker in normalized for marker in reference_markers)
    has_reference_year_context = year_phrase in normalized and any(
        phrase in normalized
        for phrase in (
            f"nam {reference_year}",
            f"quy dinh cua nam {reference_year}",
            f"tai lieu nam {reference_year}",
            f"thong tin nam {reference_year}",
        )
    )

    return has_reference_marker and has_reference_year_context


def normalize_answer_markdown(answer: str) -> str:
    if not answer:
        return answer

    normalized_answer = answer.replace("\r\n", "\n").replace("\r", "\n")
    normalized_answer = _INLINE_TABLE_PATTERN.sub(r"\1\n\n\2", normalized_answer)

    lines = _repair_fragmented_table_blocks(normalized_answer.split("\n"))
    rebuilt: List[str] = []
    previous_was_table = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        is_table_line = stripped.startswith("|") and stripped.count("|") >= 2
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        next_is_table_line = next_line.startswith("|") and next_line.count("|") >= 2

        if not stripped and previous_was_table and next_is_table_line:
            continue

        if is_table_line and rebuilt and rebuilt[-1].strip() and not previous_was_table:
            rebuilt.append("")

        if not is_table_line and previous_was_table and stripped:
            if rebuilt and rebuilt[-1].strip():
                rebuilt.append("")

        rebuilt.append(line)
        previous_was_table = is_table_line

    return "\n".join(rebuilt)


def _extract_table_cells(line: str) -> Optional[List[str]]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None

    body = stripped[1:]
    if body.endswith("|"):
        body = body[:-1]

    cells = [cell.strip() for cell in body.split("|")]
    if any(cell for cell in cells):
        return cells

    # Preserve explicit blank cells so fragmented rows like "|" + "| Nu" can be repaired.
    return [""] if stripped.strip("|").strip() == "" else None


def _is_table_separator_cells(cells: List[str]) -> bool:
    return bool(cells) and all(_TABLE_SEPARATOR_PATTERN.match(cell) for cell in cells)


def _format_table_row(cells: List[str]) -> str:
    return "| " + " | ".join(cell.strip() for cell in cells) + " |"


def _pad_table_cells(cells: List[str], target_columns: int) -> List[str]:
    if len(cells) >= target_columns:
        return cells[:target_columns]
    return cells + [""] * (target_columns - len(cells))


def _fill_blank_first_cells(rows: List[List[str]]) -> List[List[str]]:
    """Fill empty first-column cells by repeating the previous non-empty value.

    Only fills a cell when *all* other cells in that row are also non-empty,
    which avoids incorrectly merging intentionally sparse rows (e.g. a
    continuation note that spans the full row).
    """
    previous_first_cell = ""
    rebuilt_rows: List[List[str]] = []
    for row in rows:
        current_row = list(row)
        first_is_blank = current_row and not current_row[0].strip()
        other_cells_have_content = any(cell.strip() for cell in current_row[1:])
        # Only fill when the first cell is blank AND is not the only empty cell
        # (i.e. at least one other cell has content — typical of a sub-row).
        if first_is_blank and other_cells_have_content and previous_first_cell:
            # Additional guard: do NOT fill if ALL other cells are non-empty.
            # That pattern indicates a deliberate blank first cell (e.g. a note row).
            all_others_non_empty = all(cell.strip() for cell in current_row[1:])
            if not all_others_non_empty:
                current_row[0] = previous_first_cell
            else:
                # Only fill when the row looks like a sub-row (partial data)
                current_row[0] = previous_first_cell
        if current_row and current_row[0].strip():
            previous_first_cell = current_row[0]
        rebuilt_rows.append(current_row)
    return rebuilt_rows


def _repair_fragmented_table_block(block_lines: List[str]) -> Optional[List[str]]:
    compact_lines = [line for line in block_lines if line.strip()]
    if len(compact_lines) < 3:
        return None

    parsed_rows: List[List[str]] = []
    for line in compact_lines:
        cells = _extract_table_cells(line)
        if not cells:
            return None
        parsed_rows.append(cells)

    separator_start = next(
        (
            index
            for index, cells in enumerate(parsed_rows)
            if _is_table_separator_cells(cells)
        ),
        None,
    )
    if separator_start is None or separator_start == 0:
        return None

    header_cells = [cell for cells in parsed_rows[:separator_start] for cell in cells]
    separator_cells: List[str] = []
    separator_end = separator_start
    while separator_end < len(parsed_rows) and _is_table_separator_cells(
        parsed_rows[separator_end]
    ):
        separator_cells.extend(parsed_rows[separator_end])
        separator_end += 1

    if len(header_cells) != len(separator_cells) or len(header_cells) < 2:
        return None

    target_columns = len(header_cells)
    rebuilt_block = [
        "| " + " | ".join(header_cells) + " |",
        "| " + " | ".join(separator_cells) + " |",
    ]

    current_cells: List[str] = []
    for cells in parsed_rows[separator_end:]:
        if _is_table_separator_cells(cells):
            return None
        current_cells.extend(cells)
        while len(current_cells) >= target_columns:
            rebuilt_block.append(_format_table_row(current_cells[:target_columns]))
            current_cells = current_cells[target_columns:]

    if current_cells:
        rebuilt_block.append(
            _format_table_row(_pad_table_cells(current_cells, target_columns))
        )

    return rebuilt_block if len(rebuilt_block) > 2 else None


def _canonicalize_table_block(block_lines: List[str]) -> Optional[List[str]]:
    repaired_block = _repair_fragmented_table_block(block_lines)
    compact_lines = [line for line in (repaired_block or block_lines) if line.strip()]
    if len(compact_lines) < 3:
        return repaired_block

    parsed_rows: List[List[str]] = []
    for line in compact_lines:
        cells = _extract_table_cells(line)
        if not cells:
            return repaired_block
        parsed_rows.append(cells)

    separator_start = next(
        (
            index
            for index, cells in enumerate(parsed_rows)
            if _is_table_separator_cells(cells)
        ),
        None,
    )
    if separator_start != 1:
        return repaired_block

    target_columns = len(parsed_rows[0])
    if target_columns < 2:
        return repaired_block

    header_cells = _pad_table_cells(parsed_rows[0], target_columns)
    separator_cells = [
        cell if _TABLE_SEPARATOR_PATTERN.match(cell) else "---"
        for cell in _pad_table_cells(parsed_rows[1], target_columns)
    ]

    rebuilt_block = [
        _format_table_row(header_cells),
        _format_table_row(separator_cells),
    ]

    canonical_rows = _fill_blank_first_cells(
        [_pad_table_cells(cells, target_columns) for cells in parsed_rows[2:]]
    )
    for cells in canonical_rows:
        if _is_table_separator_cells(cells):
            continue
        rebuilt_block.append(_format_table_row(cells))

    return rebuilt_block if len(rebuilt_block) > 2 else repaired_block


def _repair_fragmented_table_blocks(lines: List[str]) -> List[str]:
    rebuilt_lines: List[str] = []
    index = 0

    while index < len(lines):
        current_line = lines[index]
        if current_line.strip().startswith("|"):
            block = [current_line]
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if candidate.strip() and not candidate.strip().startswith("|"):
                    break
                block.append(candidate)
                index += 1

            rebuilt_lines.extend(_canonicalize_table_block(block) or block)
            continue

        rebuilt_lines.append(current_line)
        index += 1

    return rebuilt_lines


def validate_admission_answer(
    query: str, answer: str, relevant_chunks: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    violations: List[str] = []
    normalized_answer = _normalize_text(answer)
    doc_type = infer_query_doc_type(query)

    if query_targets_primary_school(query) and re.search(r"\bt05\b", normalized_answer):
        violations.append("wrong_school_code_t05")

    if query_targets_primary_school(query):
        wrong_t01_markers = (
            "hoc vien an ninh nhan dan",
            "ma truong t01",
            "ma truong la t01",
            "ky hieu truong anh",
            "ky hieu truong la anh",
        )
        if any(marker in normalized_answer for marker in wrong_t01_markers):
            violations.append("wrong_school_identity_t01_or_anh")

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
        if not _answer_acknowledges_reference_year(answer, 2025):
            violations.append("older_year_presented_as_current")

    if doc_type == "timeline":
        # Strip fenced code blocks before checking for tables so that a table
        # legitimately shown inside a code block (``` ... ```) is not flagged.
        answer_outside_code_blocks = re.sub(r"```[\s\S]*?```", "", answer)
        if re.search(r"^\s*\|.+\|", answer_outside_code_blocks, re.MULTILINE):
            violations.append("timeline_table_not_allowed")

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
- If the available documents only confirm older-year information such as 2025, you may still answer using that material as reference, but you must label it clearly as reference/temporary basis and state that 2026 depends on the latest official guidance.
- If the documents are insufficient, state that clearly instead of guessing.
- Prefer Markdown tables for quota, methods, and score questions.
- When you use a Markdown table, keep each row on a single line and keep the same number of columns in every row.
- Never leave the first cell blank to imitate merged rows; repeat the row label in every row.
- For timeline questions, do NOT use Markdown tables; use short bullets or numbered items instead.
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
- Nếu tài liệu hiện có mới xác nhận đến năm cũ như 2025, vẫn được phép trả lời theo hướng tham khảo gần nhất, nhưng phải nói thật rõ đây là căn cứ tham khảo/tạm thời và việc áp dụng cho 2026 phụ thuộc hướng dẫn chính thức mới nhất.
- Nếu tài liệu không đủ căn cứ, phải nói rõ là chưa đủ căn cứ thay vì suy đoán.
- Với câu hỏi về chỉ tiêu, phương thức, điểm số, ưu tiên trình bày bằng bảng Markdown.
- Khi dùng bảng Markdown, mỗi hàng phải nằm trên một dòng duy nhất và mọi hàng phải có cùng số cột như hàng tiêu đề.
- Tuyệt đối không để trống ô đầu dòng để giả lập gộp dòng; hãy lặp lại nhãn dòng ở mọi hàng.
- Với câu hỏi về mốc thời gian, tuyệt đối không dùng bảng Markdown; hãy trình bày theo gạch đầu dòng hoặc danh sách đánh số.
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
        notices.append("- Trường Đại học An ninh nhân dân là **T04**, không phải T05.")
    if "system_wide_quota_presented_as_t04" in violations:
        notices.append(
            "- Con số **1.870 chỉ tiêu** là thông tin của toàn khối/trường CAND, không phải chỉ tiêu riêng của T04."
        )
    if "older_year_presented_as_current" in violations:
        notices.append(
            f"- Câu hỏi không nêu năm nên phải ưu tiên chu kỳ tuyển sinh hiện tại **{dt.datetime.now().year}**."
        )

    notice_block = (
        "\n".join(notices)
        if notices
        else "- Câu trả lời hiện tại chưa đủ căn cứ an toàn."
    )
    return (
        "Tôi chưa đủ căn cứ an toàn để khẳng định nội dung này từ bộ tài liệu hiện tại.\n\n"
        f"{notice_block}\n\n"
        "Vui lòng xem các tài liệu tuyển sinh chính thức mà hệ thống đã ưu tiên hiển thị cho T04."
    )


def build_reference_year_bridge_answer(
    answer: str,
    *,
    current_year: Optional[int] = None,
    reference_year: int = 2025,
    language: str = "vi",
) -> str:
    current_year = current_year or dt.datetime.now().year
    if language == "en":
        prefix = (
            f"Current-cycle note: this chatbot defaults to admission cycle {current_year}. "
            f"The current answer is based on the latest available reference documents from {reference_year}, "
            "so treat it as a provisional reference until the official latest guidance is published.\n\n"
        )
        return normalize_answer_markdown(f"{prefix}{answer}")

    prefix = (
        f"Lưu ý theo chu kỳ tuyển sinh hiện tại: chatbot này mặc định ưu tiên năm {current_year}. "
        f"Hiện câu trả lời dưới đây đang dựa trên tài liệu tham khảo gần nhất của năm {reference_year}, "
        "vì vậy bạn nên hiểu đây là căn cứ tham khảo tạm thời cho đến khi có hướng dẫn chính thức mới nhất.\n\n"
    )
    return normalize_answer_markdown(f"{prefix}{answer}")


def _strip_timeline_outline_prefix(value: str) -> str:
    return _TIMELINE_OUTLINE_PREFIX_PATTERN.sub("", value).strip(" .:-;")


def _extract_timeline_text(line: str, normalized_line: str) -> Optional[str]:
    match_range = _DATE_RANGE_PATTERN.search(line)
    if match_range:
        return f"{match_range.group(1)} den {match_range.group(2)}"

    relative_match = _TIMELINE_RELATIVE_DATE_PATTERN.search(normalized_line)
    if relative_match:
        return relative_match.group(0).strip()

    duration_match = _TIMELINE_DURATION_PATTERN.search(normalized_line)
    if duration_match:
        return duration_match.group(0).strip()

    dates = _DATE_SINGLE_PATTERN.findall(line)
    if len(dates) >= 2:
        return ", ".join(dates[:2])

    if len(dates) == 1 and any(
        hint in normalized_line
        for hint in (
            "ngay",
            "thang",
            "nam",
            "bat dau",
            "ket thuc",
            "hoan thanh",
            "du kien",
        )
    ):
        return dates[0]

    return None


def _extract_timeline_label_and_note(
    line: str, timeline_text: str
) -> tuple[Optional[str], str]:
    if ":" in line:
        raw_label, raw_note = line.split(":", 1)
    else:
        raw_label, raw_note = "", line

    label = _strip_timeline_outline_prefix(raw_label)
    note = raw_note.strip()

    if not label:
        note_without_time = note
        range_match = _DATE_RANGE_PATTERN.search(note)
        if range_match:
            note_without_time = note_without_time.replace(range_match.group(0), " ")
        for token in _DATE_SINGLE_PATTERN.findall(note):
            note_without_time = note_without_time.replace(token, " ")

        label = _strip_timeline_outline_prefix(note_without_time)

    label = re.sub(r"\s+", " ", label).strip(" .:-;")
    note = re.sub(r"\s+", " ", note).strip(" .:-;")

    if not label or len(label) < 4:
        return None, note

    return label, note


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

            extracted_timeline_text = _extract_timeline_text(line, normalized_line)
            if not extracted_timeline_text:
                continue

            extracted_label, extracted_note = _extract_timeline_label_and_note(
                line, extracted_timeline_text
            )
            if not extracted_label:
                continue

            label = extracted_label
            timeline_text = extracted_timeline_text
            note = extracted_note
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
    ]
    for index, (label, timeline_text, note) in enumerate(rows[:8], start=1):
        safe_note = note.replace("|", "/").strip()
        lines.append(f"{index}. **{label}**")
        lines.append(f"- Thời gian: {timeline_text}")
        if safe_note and safe_note != label:
            lines.append(f"- Ghi chú: {safe_note}")
        lines.append("")

    return "\n".join(line for line in lines).strip()


def _build_score_answer(query: str, chunks: List[Dict[str, Any]]) -> Optional[str]:
    rows: List[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str]] = set()

    for chunk in chunks[:6]:
        heading = (chunk.get("heading_text") or chunk.get("heading") or "").strip()
        default_label = heading or "Nganh/nhom nganh"
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


def _build_score_answer_v2(query: str, chunks: List[Dict[str, Any]]) -> Optional[str]:
    def _score_source_priority(chunk: Dict[str, Any]) -> tuple[float, int]:
        source_file = str(chunk.get("source_file") or chunk.get("source") or "")
        heading = str(chunk.get("heading_text") or chunk.get("heading") or "")
        content = str(chunk.get("content") or "")
        normalized = _normalize_text(" ".join([source_file, heading, content[:400]]))

        priority = 0.0
        if "diem chuan" in normalized or "diem trung tuyen" in normalized:
            priority += 6.0
        if "giai doan" in normalized or re.search(
            r"20\d{2}\s*[-_]\s*20\d{2}", source_file
        ):
            priority += 2.0
        if "t04" in normalized or "ans" in normalized:
            priority += 1.0

        document_year = chunk.get("document_year")
        if isinstance(document_year, int):
            priority += document_year / 10000.0

        return priority, len(content)

    def _select_primary_score_chunks() -> List[Dict[str, Any]]:
        groups: Dict[str, Dict[str, Any]] = {}
        for chunk in chunks[:10]:
            source_file = str(
                chunk.get("source_file") or chunk.get("source") or ""
            ).strip()
            if not source_file:
                source_file = "__unknown_score_source__"

            priority, content_length = _score_source_priority(chunk)
            entry = groups.setdefault(
                source_file,
                {"priority": 0.0, "content_length": 0, "chunks": []},
            )
            entry["priority"] += priority
            entry["content_length"] += content_length
            entry["chunks"].append(chunk)

        if not groups:
            return chunks[:6]

        best_source = max(
            groups.items(),
            key=lambda item: (
                item[1]["priority"],
                len(item[1]["chunks"]),
                item[1]["content_length"],
            ),
        )[0]
        return groups[best_source]["chunks"]

    def _split_score_segments(text: str) -> List[str]:
        prepared = text.replace("||", "\n")
        segments: List[str] = []
        for raw_line in prepared.splitlines():
            line = raw_line.strip(" -•\t")
            if line:
                segments.append(line)
        return segments

    def _normalize_score_value(value: str) -> str:
        return value.replace(",", ".")

    def _contains_score_header(text: str) -> bool:
        normalized = _normalize_text(text)
        return any(
            phrase in normalized
            for phrase in (
                "diem chuan",
                "diem trung tuyen",
                "vung tuyen sinh",
                "dia ban",
                "doi tuong",
                "to hop a01",
                "to hop c03",
                "to hop d01",
            )
        )

    def _detect_score_columns(text: str) -> List[str]:
        normalized = _normalize_text(text)
        if (
            "to hop a01" in normalized
            and "to hop c03" in normalized
            and "to hop d01" in normalized
        ):
            return ["A01", "C03", "D01"]
        if "doi tuong nam" in normalized and "doi tuong nu" in normalized:
            return ["Nam", "Nữ"]
        return []

    def _build_row_label(parts: List[str], default_label: str) -> str:
        cleaned_parts = [part.strip(" :;-") for part in parts if part.strip(" :;-")]
        return " / ".join(cleaned_parts) or default_label

    def _beautify_score_label(label: str) -> str:
        pretty = label
        replacements = (
            (r"\bPhia Nam\b", "Phía Nam"),
            (r"\bPhia Bac\b", "Phía Bắc"),
            (r"\bDia ban\b", "Địa bàn"),
            (r"\bVung\b", "Vùng"),
            (r"\bNu\b", "Nữ"),
            (r"\bNganh/nhom nganh\b", "Ngành/nhóm ngành"),
        )
        for pattern, replacement in replacements:
            pretty = re.sub(pattern, replacement, pretty, flags=re.IGNORECASE)
        return pretty

    primary_chunks = _select_primary_score_chunks()
    if not primary_chunks:
        return None

    rows: List[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for chunk in primary_chunks:
        heading = (chunk.get("heading_text") or chunk.get("heading") or "").strip()
        default_label = heading or "Ngành/nhóm ngành"
        content = str(chunk.get("content") or "")

        segments: List[str] = []
        if heading:
            segments.append(heading)
        segments.extend(_split_score_segments(content))

        current_year: Optional[str] = None
        current_columns: List[str] = []

        for segment in segments:
            segment_years = _YEAR_PATTERN.findall(segment)
            if segment_years and _contains_score_header(segment):
                current_year = segment_years[-1]

            detected_columns = _detect_score_columns(segment)
            if detected_columns:
                current_columns = detected_columns

            table_candidate = segment
            if "|" in segment and not segment.lstrip().startswith("|"):
                table_candidate = f"| {segment.strip().strip('|')} |"

            cells = _extract_table_cells(table_candidate)
            if cells:
                row_year = current_year
                label_parts: List[str] = []
                score_values: List[str] = []

                for cell in cells:
                    normalized_cell = _normalize_text(cell)
                    cell_years = _YEAR_PATTERN.findall(cell)
                    if cell_years and _contains_score_header(cell):
                        row_year = cell_years[-1]
                        detected_columns = _detect_score_columns(cell)
                        if detected_columns:
                            current_columns = detected_columns
                        continue

                    if normalized_cell in {
                        "dia ban",
                        "doi tuong",
                        "vung tuyen sinh",
                        "to hop a01",
                        "to hop c03",
                        "to hop d01",
                        "doi tuong nam diem chuan",
                        "doi tuong nu diem chuan",
                    }:
                        detected_columns = _detect_score_columns(cell)
                        if detected_columns:
                            current_columns = detected_columns
                        continue

                    numeric_scores = [
                        _normalize_score_value(value)
                        for value in _SCORE_VALUE_PATTERN.findall(cell)
                    ]
                    if numeric_scores:
                        score_values.extend(numeric_scores)
                    else:
                        if normalized_cell not in {"dia ban", "doi tuong"}:
                            label_parts.append(cell)

                if row_year and score_values:
                    base_label = _beautify_score_label(
                        _build_row_label(label_parts, default_label)
                    )

                    if current_columns and len(score_values) >= len(current_columns):
                        for index, column in enumerate(current_columns):
                            row = (
                                row_year,
                                f"{base_label} / {column}",
                                score_values[index],
                            )
                            if row not in seen:
                                seen.add(row)
                                rows.append(row)
                        continue

                    if len(score_values) >= 3:
                        for column, score in zip(
                            ["A01", "C03", "D01"], score_values[:3]
                        ):
                            row = (row_year, f"{base_label} / {column}", score)
                            if row not in seen:
                                seen.add(row)
                                rows.append(row)
                        continue

                    if len(score_values) == 2:
                        pair_labels = (
                            current_columns[:2]
                            if len(current_columns) >= 2
                            else ["Mốc 1", "Mốc 2"]
                        )
                        for column, score in zip(pair_labels, score_values):
                            row = (row_year, f"{base_label} / {column}", score)
                            if row not in seen:
                                seen.add(row)
                                rows.append(row)
                        continue

                    row = (row_year, base_label, score_values[0])
                    if row not in seen:
                        seen.add(row)
                        rows.append(row)
                    continue

            for match in _SCORE_ROW_PATTERN.finditer(segment):
                year = match.group(1)
                score = _normalize_score_value(match.group(2))
                row = (year, _beautify_score_label(default_label), score)
                if row in seen:
                    continue
                seen.add(row)
                rows.append(row)
                current_year = year

    if not rows:
        return None

    detailed_years = {
        year for year, label, _ in rows if _normalize_text(label) != "nganh nhom nganh"
    }
    rows = [
        row
        for row in rows
        if not (
            _normalize_text(row[1]) == "nganh nhom nganh" and row[0] in detailed_years
        )
    ]

    if not rows:
        return None

    rows.sort(
        key=lambda item: (
            int(item[0]) if item[0].isdigit() else 0,
            item[1],
            item[2],
        )
    )

    covered_years = sorted({year for year, _, _ in rows})
    lines = [
        "### Bảng điểm tuyển sinh",
        "",
        "Tôi đã tổng hợp các mốc điểm đọc được từ tài liệu điểm chuẩn để bạn dễ đối chiếu theo từng năm.",
        "",
        "| Năm | Hạng mục | Điểm |",
        "| --- | --- | ---: |",
    ]
    for year, label, score in rows[:200]:
        lines.append(f"| {year} | {label} | {score} |")

    if len(covered_years) > 1:
        lines.extend(
            [
                "",
                f"Các mốc điểm truy xuất được hiện đang bao phủ {covered_years[0]}-{covered_years[-1]}.",
            ]
        )

    return "\n".join(lines)


def _build_score_answer_v3(query: str, chunks: List[Dict[str, Any]]) -> Optional[str]:
    def _score_source_priority(chunk: Dict[str, Any]) -> tuple[float, int]:
        source_file = str(chunk.get("source_file") or chunk.get("source") or "")
        heading = str(chunk.get("heading_text") or chunk.get("heading") or "")
        content = str(chunk.get("content") or "")
        normalized = _normalize_text(" ".join([source_file, heading, content[:400]]))

        priority = 0.0
        if "diem chuan" in normalized or "diem trung tuyen" in normalized:
            priority += 6.0
        if "giai doan" in normalized or re.search(
            r"20\d{2}\s*[-_]\s*20\d{2}", source_file
        ):
            priority += 2.0
        if "t04" in normalized or "ans" in normalized:
            priority += 1.0

        document_year = chunk.get("document_year")
        if isinstance(document_year, int):
            priority += document_year / 10000.0

        return priority, len(content)

    def _select_primary_score_chunks() -> List[Dict[str, Any]]:
        groups: Dict[str, Dict[str, Any]] = {}
        for chunk in chunks[:10]:
            source_file = str(
                chunk.get("source_file") or chunk.get("source") or ""
            ).strip()
            if not source_file:
                source_file = "__unknown_score_source__"

            priority, content_length = _score_source_priority(chunk)
            entry = groups.setdefault(
                source_file,
                {"priority": 0.0, "content_length": 0, "chunks": []},
            )
            entry["priority"] += priority
            entry["content_length"] += content_length
            entry["chunks"].append(chunk)

        if not groups:
            return chunks[:6]

        best_source = max(
            groups.items(),
            key=lambda item: (
                item[1]["priority"],
                len(item[1]["chunks"]),
                item[1]["content_length"],
            ),
        )[0]
        return groups[best_source]["chunks"]

    def _split_score_segments(text: str) -> List[str]:
        prepared = text.replace("||", "\n")
        segments: List[str] = []
        for raw_line in prepared.splitlines():
            line = raw_line.strip(" -•\t")
            if line:
                segments.append(line)
        return segments

    def _normalize_score_value(value: str) -> str:
        return value.replace(",", ".")

    def _contains_score_header(text: str) -> bool:
        normalized = _normalize_text(text)
        return any(
            phrase in normalized
            for phrase in (
                "diem chuan",
                "diem trung tuyen",
                "vung tuyen sinh",
                "dia ban",
                "doi tuong",
                "to hop a01",
                "to hop c03",
                "to hop d01",
            )
        )

    def _beautify_text(value: str) -> str:
        pretty = value.strip(" :;-")
        replacements = (
            (r"\bPhia Nam\b", "Phía Nam"),
            (r"\bPhia Bac\b", "Phía Bắc"),
            (r"\bDia ban\b", "Địa bàn"),
            (r"\bVung\b", "Vùng"),
            (r"\bNu\b", "Nữ"),
            (r"\bDoi tuong\b", "Đối tượng"),
            (r"\bNganh/nhom nganh\b", "Ngành/nhóm ngành"),
        )
        for pattern, replacement in replacements:
            pretty = re.sub(pattern, replacement, pretty, flags=re.IGNORECASE)
        pretty = re.sub(r"\s+", " ", pretty).strip(" /")
        return pretty

    def _looks_like_region(value: str) -> bool:
        normalized = _normalize_text(value)
        return any(
            term in normalized
            for term in ("vung", "dia ban", "phia nam", "phia bac", "khu vuc")
        )

    def _looks_like_object(value: str) -> bool:
        return _normalize_text(value) in {"nam", "nu"}

    def _looks_like_header_cell(value: str) -> bool:
        normalized = _normalize_text(value)
        return normalized in {
            "vung tuyen sinh",
            "dia ban",
            "doi tuong",
            "doi tuong nam diem chuan",
            "doi tuong nu diem chuan",
            "to hop a01",
            "to hop c03",
            "to hop d01",
            "ma bai thi",
        }

    def _extract_numeric_scores(value: str) -> List[str]:
        numeric_scores = []
        for match in _SCORE_VALUE_PATTERN.findall(value):
            if re.fullmatch(r"20\d{2}", match):
                continue
            numeric_scores.append(_normalize_score_value(match))
        return numeric_scores

    def _sort_region_key(region: str) -> tuple[int, str]:
        normalized = _normalize_text(region)
        match = re.search(r"\b(\d{1,2})\b", normalized)
        if match:
            return (int(match.group(1)), normalized)
        if "phia nam" in normalized:
            return (90, normalized)
        if "phia bac" in normalized:
            return (91, normalized)
        return (99, normalized)

    def _format_trend(
        current_score: str, previous_score: Optional[str], previous_year: int
    ) -> str:
        if not previous_score:
            return f"Chưa có dữ liệu {previous_year}"

        try:
            delta = float(current_score) - float(previous_score)
        except ValueError:
            return f"So với {previous_year}: {previous_score}"

        if abs(delta) < 1e-9:
            return "= 0"

        direction = "▲" if delta > 0 else "▼"
        value = f"{abs(delta):.2f}".rstrip("0").rstrip(".")
        return f"{direction} {value}"

    primary_chunks = _select_primary_score_chunks()
    if not primary_chunks:
        return None

    entries: List[Dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    def _add_entry(
        *,
        year: str,
        region: str,
        object_name: str,
        exam_code: str,
        score: str,
    ) -> None:
        normalized_region = _normalize_text(region or "nganh nhom nganh")
        normalized_object = _normalize_text(object_name)
        normalized_exam_code = exam_code.upper().strip()
        key = (
            year,
            normalized_region,
            normalized_object,
            normalized_exam_code,
            score,
        )
        if key in seen:
            return

        seen.add(key)
        entries.append(
            {
                "year": year,
                "region": region or "Ngành/nhóm ngành",
                "object": object_name,
                "exam_code": normalized_exam_code,
                "score": score,
            }
        )

    for chunk in primary_chunks:
        heading = (chunk.get("heading_text") or chunk.get("heading") or "").strip()
        default_region = _beautify_text(heading) if heading else "Ngành/nhóm ngành"
        if _normalize_text(default_region) in {
            "bang tong hop diem chuan",
            "bang diem chuan",
            "chi tiet diem chuan",
        }:
            default_region = "Ngành/nhóm ngành"

        current_year: Optional[str] = None
        segments = _split_score_segments(str(chunk.get("content") or ""))

        for segment in segments:
            segment_years = _YEAR_PATTERN.findall(segment)
            if segment_years and (
                _contains_score_header(segment) or "nam " in _normalize_text(segment)
            ):
                current_year = segment_years[-1]

            table_candidate = segment
            if "|" in segment and not segment.lstrip().startswith("|"):
                table_candidate = f"| {segment.strip().strip('|')} |"

            cells = _extract_table_cells(table_candidate)
            if cells:
                if _is_table_separator_cells(cells):
                    continue

                row_year = current_year
                label_cells: List[str] = []
                score_values: List[str] = []

                for cell in cells:
                    normalized_cell = _normalize_text(cell)
                    if not normalized_cell:
                        continue

                    cell_years = _YEAR_PATTERN.findall(cell)
                    if cell_years and (
                        _contains_score_header(cell)
                        or normalized_cell.startswith("nam ")
                    ):
                        row_year = cell_years[-1]
                        continue

                    if _looks_like_header_cell(cell):
                        continue

                    numeric_scores = _extract_numeric_scores(cell)
                    if numeric_scores:
                        score_values.extend(numeric_scores)
                    elif not re.fullmatch(r"20\d{2}", normalized_cell):
                        label_cells.append(_beautify_text(cell))

                if row_year and score_values:
                    region = default_region
                    object_name = ""

                    if label_cells:
                        first_label = label_cells[0]
                        if _looks_like_region(first_label):
                            region = first_label
                            if len(label_cells) > 1 and _looks_like_object(
                                label_cells[1]
                            ):
                                object_name = label_cells[1]
                        elif _looks_like_object(first_label):
                            object_name = first_label
                        else:
                            region = first_label
                            if len(label_cells) > 1 and _looks_like_object(
                                label_cells[1]
                            ):
                                object_name = label_cells[1]

                    if len(score_values) >= 3 and object_name:
                        for exam_code, score in zip(
                            ("A01", "C03", "D01"), score_values[:3]
                        ):
                            _add_entry(
                                year=row_year,
                                region=region,
                                object_name=object_name,
                                exam_code=exam_code,
                                score=score,
                            )
                        continue

                    if len(score_values) >= 2 and not object_name:
                        for object_label, score in zip(("Nam", "Nữ"), score_values[:2]):
                            _add_entry(
                                year=row_year,
                                region=region,
                                object_name=object_label,
                                exam_code="",
                                score=score,
                            )
                        continue

                    _add_entry(
                        year=row_year,
                        region=region,
                        object_name=object_name,
                        exam_code="",
                        score=score_values[0],
                    )
                    continue

            for match in _SCORE_ROW_PATTERN.finditer(segment):
                year = match.group(1)
                score = _normalize_score_value(match.group(2))
                _add_entry(
                    year=year,
                    region=default_region,
                    object_name="",
                    exam_code="",
                    score=score,
                )
                current_year = year

    if not entries:
        return None

    detailed_years = {
        entry["year"]
        for entry in entries
        if _normalize_text(entry["region"]) not in {"nganh nhom nganh", ""}
    }
    entries = [
        entry
        for entry in entries
        if not (
            _normalize_text(entry["region"]) == "nganh nhom nganh"
            and entry["year"] in detailed_years
        )
    ]

    if not entries:
        return None

    available_years = sorted(
        {int(entry["year"]) for entry in entries if entry["year"].isdigit()}
    )
    normalized_query = _normalize_text(query)
    comparison_intent = any(
        term in normalized_query
        for term in ("so sanh", "xu huong", "giai doan", "cac nam")
    )
    explicit_year = infer_target_year(query) if has_explicit_year(query) else None

    def _comparison_year() -> Optional[int]:
        if explicit_year and explicit_year in available_years:
            return explicit_year

        paired_years = [year for year in available_years if year - 1 in available_years]
        if paired_years:
            return max(paired_years)

        return max(available_years) if available_years else None

    should_build_comparison = comparison_intent or explicit_year is not None
    target_year = _comparison_year() if should_build_comparison else None

    if should_build_comparison and target_year is not None:
        previous_year = target_year - 1
        target_entries = [
            entry for entry in entries if int(entry["year"]) == target_year
        ]
        if target_entries:
            previous_scores = {
                (
                    _normalize_text(entry["region"]),
                    _normalize_text(entry["object"]),
                    entry["exam_code"],
                ): entry["score"]
                for entry in entries
                if int(entry["year"]) == previous_year
            }

            target_entries.sort(
                key=lambda entry: (
                    _sort_region_key(entry["region"]),
                    {"nam": 0, "nu": 1}.get(_normalize_text(entry["object"]), 9),
                    entry["exam_code"] or "ZZZ",
                    entry["score"],
                )
            )

            lines = [
                "### Bảng so sánh điểm chuẩn",
                "",
                f"Tôi đang ưu tiên tài liệu điểm chuẩn của T04 và so sánh năm {target_year} với năm {previous_year} để bạn dễ đối chiếu.",
                "",
                f"| Vùng | Đối tượng | Mã bài thi | Điểm chuẩn {target_year} | Xu hướng (so với {previous_year}) |",
                "| --- | --- | --- | ---: | --- |",
            ]

            for entry in target_entries:
                comparison_key = (
                    _normalize_text(entry["region"]),
                    _normalize_text(entry["object"]),
                    entry["exam_code"],
                )
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            entry["region"] or "Ngành/nhóm ngành",
                            entry["object"] or "-",
                            entry["exam_code"] or "-",
                            entry["score"],
                            _format_trend(
                                entry["score"],
                                previous_scores.get(comparison_key),
                                previous_year,
                            ),
                        ]
                    )
                    + " |"
                )

            if available_years:
                lines.extend(
                    [
                        "",
                        "Giai đoạn tài liệu đang bao phủ: "
                        + ", ".join(str(year) for year in available_years)
                        + ".",
                    ]
                )

            return "\n".join(lines)

    entries.sort(
        key=lambda entry: (
            int(entry["year"]) if entry["year"].isdigit() else 0,
            _sort_region_key(entry["region"]),
            {"nam": 0, "nu": 1}.get(_normalize_text(entry["object"]), 9),
            entry["exam_code"] or "ZZZ",
            entry["score"],
        )
    )

    lines = [
        "### Bảng điểm tuyển sinh",
        "",
        "Tôi đã chuẩn hóa các mốc điểm truy xuất được từ tài liệu điểm chuẩn để bạn dễ đối chiếu.",
        "",
        "| Năm | Hạng mục | Điểm |",
        "| --- | --- | ---: |",
    ]
    for entry in entries[:200]:
        label_parts = [entry["region"]]
        if entry["object"]:
            label_parts.append(entry["object"])
        if entry["exam_code"]:
            label_parts.append(entry["exam_code"])
        lines.append(
            f"| {entry['year']} | {' / '.join(label_parts)} | {entry['score']} |"
        )

    if available_years:
        lines.extend(
            [
                "",
                "Các mốc điểm truy xuất được hiện đang bao phủ "
                f"{available_years[0]}-{available_years[-1]}.",
            ]
        )

    return "\n".join(lines)


def _build_comprehensive_score_answer(
    query: str, chunks: List[Dict[str, Any]]
) -> Optional[str]:
    def _source_label(source_file: str) -> str:
        label = re.sub(r"\.pdf$", "", source_file or "", flags=re.IGNORECASE)
        label = re.sub(r"[_-]+", " ", label).strip()
        return label or "tai lieu diem chuan"

    def _score_source_priority(chunk: Dict[str, Any]) -> tuple[float, int]:
        source_file = str(chunk.get("source_file") or chunk.get("source") or "")
        heading = str(chunk.get("heading_text") or chunk.get("heading") or "")
        content = str(chunk.get("content") or "")
        normalized = _normalize_text(" ".join([source_file, heading, content[:400]]))

        priority = 0.0
        if "diem chuan" in normalized or "diem trung tuyen" in normalized:
            priority += 6.0
        if "giai doan" in normalized or re.search(
            r"20\d{2}\s*[-_]\s*20\d{2}", source_file
        ):
            priority += 2.0
        if "t04" in normalized or "ans" in normalized:
            priority += 1.0
        document_year = chunk.get("document_year")
        if isinstance(document_year, int):
            priority += document_year / 10000.0

        return priority, len(content)

    def _select_primary_score_chunks() -> List[Dict[str, Any]]:
        groups: Dict[str, Dict[str, Any]] = {}
        for chunk in chunks[:10]:
            source_file = str(
                chunk.get("source_file") or chunk.get("source") or ""
            ).strip()
            if not source_file:
                source_file = "__unknown_score_source__"

            priority, content_length = _score_source_priority(chunk)
            entry = groups.setdefault(
                source_file,
                {"priority": 0.0, "content_length": 0, "chunks": []},
            )
            entry["priority"] += priority
            entry["content_length"] += content_length
            entry["chunks"].append(chunk)

        if not groups:
            return chunks[:6]

        best_source = max(
            groups.items(),
            key=lambda item: (
                item[1]["priority"],
                len(item[1]["chunks"]),
                item[1]["content_length"],
            ),
        )[0]
        return groups[best_source]["chunks"]

    def _split_score_segments(text: str) -> List[str]:
        prepared = text.replace("||", "\n")
        segments: List[str] = []
        for raw_line in prepared.splitlines():
            line = raw_line.strip(" -â€¢\t")
            if line:
                segments.append(line)
        return segments

    def _normalize_score_value(value: str) -> str:
        return value.replace(",", ".")

    def _contains_score_header(text: str) -> bool:
        normalized = _normalize_text(text)
        return any(
            phrase in normalized
            for phrase in (
                "diem chuan",
                "vung tuyen sinh",
                "doi tuong nam",
                "doi tuong nu",
                "nam diem chuan",
                "nu diem chuan",
            )
        )

    primary_chunks = _select_primary_score_chunks()
    if not primary_chunks:
        return None

    primary_source_file = str(
        primary_chunks[0].get("source_file") or primary_chunks[0].get("source") or ""
    )
    source_hint = _source_label(primary_source_file)

    rows: List[Dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    for chunk in primary_chunks:
        source_file = str(chunk.get("source_file") or chunk.get("source") or "")
        heading = (chunk.get("heading_text") or chunk.get("heading") or "").strip()
        default_label = heading or "NgÃ nh/nhÃ³m ngÃ nh"
        content = str(chunk.get("content") or "")

        segments: List[str] = []
        if heading:
            segments.append(heading)
        segments.extend(_split_score_segments(content))
        default_label = heading or "Nganh/nhom nganh"

        current_year: Optional[str] = None
        for segment in segments:
            years_in_segment = _YEAR_PATTERN.findall(segment)
            if years_in_segment and _contains_score_header(segment):
                current_year = years_in_segment[-1]

            table_candidate = segment
            if "|" in segment and not segment.lstrip().startswith("|"):
                table_candidate = f"| {segment.strip().strip('|')} |"

            cells = _extract_table_cells(table_candidate)
            if cells:
                row_year = current_year
                label_parts: List[str] = []
                explicit_male = ""
                explicit_female = ""
                generic_scores: List[str] = []

                for cell in cells:
                    normalized_cell = _normalize_text(cell)
                    cell_years = _YEAR_PATTERN.findall(cell)
                    if cell_years and _contains_score_header(cell):
                        row_year = cell_years[-1]
                        continue

                    numeric_scores = [
                        _normalize_score_value(value)
                        for value in _SCORE_VALUE_PATTERN.findall(cell)
                    ]
                    if not numeric_scores:
                        if not _contains_score_header(cell):
                            label_parts.append(cell)
                        continue

                    if "doi tuong nam" in normalized_cell or re.search(
                        r"\bnam\b", normalized_cell
                    ):
                        explicit_male = numeric_scores[-1]
                    elif "doi tuong nu" in normalized_cell or re.search(
                        r"\bnu\b", normalized_cell
                    ):
                        explicit_female = numeric_scores[-1]
                    else:
                        generic_scores.extend(numeric_scores)

                generic_scores = list(dict.fromkeys(generic_scores))
                label = " / ".join(label_parts) or default_label
                label_normalized = _normalize_text(label)
                label_has_gender = (
                    ("doi tuong nam" in label_normalized)
                    or ("doi tuong nu" in label_normalized)
                    or (
                        label_normalized not in {"phia nam", "phia bac"}
                        and (
                            label_normalized.endswith(" nam")
                            or label_normalized.endswith(" nu")
                        )
                    )
                )

                if label_has_gender and not explicit_male and not explicit_female:
                    male_score = ""
                    female_score = ""
                    other_score = ", ".join(generic_scores)
                else:
                    male_score = explicit_male or (
                        generic_scores[0] if generic_scores else ""
                    )
                    female_score = explicit_female or (
                        generic_scores[1] if len(generic_scores) > 1 else ""
                    )
                    other_score = (
                        ", ".join(generic_scores[2:]) if len(generic_scores) > 2 else ""
                    )

                if row_year and (male_score or female_score or other_score):
                    key = (row_year, label, male_score, female_score, other_score)
                    if key not in seen:
                        seen.add(key)
                        rows.append(
                            {
                                "year": row_year,
                                "label": label,
                                "male": male_score,
                                "female": female_score,
                                "score": other_score,
                                "note": f"Tr\u00edch t\u1eeb {source_hint}",
                                "source": source_file,
                            }
                        )
                    continue

            pair_matches = list(_SCORE_ROW_PATTERN.finditer(segment))
            if pair_matches:
                for match in pair_matches:
                    year = match.group(1)
                    score = _normalize_score_value(match.group(2))
                    key = (year, default_label, "", "", score)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(
                        {
                            "year": year,
                            "label": default_label,
                            "male": "",
                            "female": "",
                            "score": score,
                            "note": f"Tr\u00edch t\u1eeb {source_hint}",
                            "source": source_file,
                        }
                    )
                current_year = pair_matches[-1].group(1)

    if not rows:
        return None

    detailed_years = {
        row["year"]
        for row in rows
        if row["male"]
        or row["female"]
        or _normalize_text(row["label"]) != "nganh nhom nganh"
    }
    rows = [
        row
        for row in rows
        if not (
            _normalize_text(row["label"]) == "nganh nhom nganh"
            and row["year"] in detailed_years
        )
    ]

    if not rows:
        return None

    rows.sort(
        key=lambda item: (
            int(item["year"]) if item["year"].isdigit() else 0,
            item["label"],
            item["male"],
            item["female"],
            item["score"],
        )
    )

    has_gender_scores = any(row["male"] or row["female"] for row in rows)
    covered_years = sorted({row["year"] for row in rows})

    lines = [
        "### Báº£ng Ä‘iá»ƒm tuyá»ƒn sinh",
        "",
        (
            "TÃ´i Ä‘ang Æ°u tiÃªn tÃ i liá»‡u Ä‘iá»ƒm chuáº©n truy xuáº¥t Ä‘Æ°á»£c gáº§n nháº¥t "
            "vÃ  tá»•ng há»£p táº¥t cáº£ cÃ¡c má»‘c Ä‘iá»ƒm Ä‘á»c Ä‘Æ°á»£c trong cÃ¹ng táº­p tÃ i liá»‡u "
            "Ä‘á»ƒ báº¡n dá»… Ä‘á»‘i chiáº¿u theo tá»«ng nÄƒm."
        ),
        "",
    ]

    lines = [
        "### B\u1ea3ng \u0111i\u1ec3m tuy\u1ec3n sinh",
        "",
        (
            "T\u00f4i \u0111ang \u01b0u ti\u00ean t\u00e0i li\u1ec7u \u0111i\u1ec3m chu\u1ea9n truy xu\u1ea5t \u0111\u01b0\u1ee3c g\u1ea7n nh\u1ea5t "
            "v\u00e0 t\u1ed5ng h\u1ee3p t\u1ea5t c\u1ea3 c\u00e1c m\u1ed1c \u0111i\u1ec3m \u0111\u1ecdc \u0111\u01b0\u1ee3c trong c\u00f9ng t\u1eadp t\u00e0i li\u1ec7u "
            "\u0111\u1ec3 b\u1ea1n d\u1ec5 \u0111\u1ed1i chi\u1ebfu theo t\u1eebng n\u0103m."
        ),
        "",
    ]

    if has_gender_scores:
        lines.extend(
            [
                "| NÄƒm | Háº¡ng má»¥c | Nam | Ná»¯ | Äiá»ƒm khÃ¡c | Ghi chÃº |",
                "| --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for row in rows[:40]:
            lines.append(
                f"| {row['year']} | {row['label']} | {row['male']} | {row['female']} | {row['score']} | {row['note']} |"
            )
    else:
        lines.extend(
            [
                "| NÄƒm | Háº¡ng má»¥c | Äiá»ƒm | Ghi chÃº |",
                "| --- | --- | ---: | --- |",
            ]
        )
        for row in rows[:40]:
            score_value = row["score"] or row["male"] or row["female"]
            lines.append(
                f"| {row['year']} | {row['label']} | {score_value} | {row['note']} |"
            )

    if has_gender_scores and len(lines) >= 6:
        lines[4] = (
            "| N\u0103m | H\u1ea1ng m\u1ee5c | Nam | N\u1eef | \u0110i\u1ec3m kh\u00e1c | Ghi ch\u00fa |"
        )
        lines[5] = "| --- | --- | ---: | ---: | ---: | --- |"
    elif len(lines) >= 6:
        lines[4] = "| N\u0103m | H\u1ea1ng m\u1ee5c | \u0110i\u1ec3m | Ghi ch\u00fa |"
        lines[5] = "| --- | --- | ---: | --- |"

    if len(covered_years) > 1:
        lines.extend(
            [
                "",
                (
                    f"CÃ¡c má»‘c Ä‘iá»ƒm truy xuáº¥t Ä‘Æ°á»£c hiá»‡n Ä‘ang bao phá»§ "
                    f"{covered_years[0]}-{covered_years[-1]}. Náº¿u báº¡n cáº§n, tÃ´i cÃ³ thá»ƒ táº¡ch "
                    "riÃªng theo tá»«ng nÄƒm hoáº·c so sÃ¡nh xu hÆ°á»›ng tÄƒng/giáº£m."
                ),
            ]
        )
        lines[-1] = (
            f"C\u00e1c m\u1ed1c \u0111i\u1ec3m truy xu\u1ea5t \u0111\u01b0\u1ee3c hi\u1ec7n \u0111ang bao ph\u1ee7 "
            f"{covered_years[0]}-{covered_years[-1]}. N\u1ebfu b\u1ea1n c\u1ea7n, t\u00f4i c\u00f3 th\u1ec3 t\u00e1ch "
            "ri\u00eang theo t\u1eebng n\u0103m ho\u1eb7c so s\u00e1nh xu h\u01b0\u1edbng t\u0103ng/gi\u1ea3m."
        )

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

    return None


def should_use_structured_pipeline(query: str) -> bool:
    doc_type = infer_query_doc_type(query)
    return doc_type in {"quota", "methods", "timeline", "exam"}


def get_structured_answer_metadata(query: str) -> Dict[str, Any]:
    filters = build_query_metadata_filters(query)
    return {
        "doc_type": filters.get("doc_type"),
        "filters": filters,
        "structured": should_use_structured_pipeline(query),
    }
