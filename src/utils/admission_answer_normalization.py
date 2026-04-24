"""
Shared normalization, markdown cleanup, and validation helpers for admission answers.
"""

from __future__ import annotations

import datetime as dt
import re
from typing import Any, Dict, List, Optional

from src.utils.admission_document_priority import (
    has_explicit_year,
    infer_query_school_metadata,
    infer_target_year,
    is_admission_query,
    query_targets_primary_school,
)
from src.utils.admission_shared import normalize_text

YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
INLINE_TABLE_PATTERN = re.compile(r"([^\n])(\|(?:[^|\n]+\|){2,}.*)")
TABLE_SEPARATOR_PATTERN = re.compile(r"^:?-{3,}:?$")

_CP1252_REVERSE_MAP = {
    chr(0x20AC): 0x80,
    chr(0x201A): 0x82,
    chr(0x0192): 0x83,
    chr(0x201E): 0x84,
    chr(0x2026): 0x85,
    chr(0x2020): 0x86,
    chr(0x2021): 0x87,
    chr(0x02C6): 0x88,
    chr(0x2030): 0x89,
    chr(0x0160): 0x8A,
    chr(0x2039): 0x8B,
    chr(0x0152): 0x8C,
    chr(0x017D): 0x8E,
    chr(0x2018): 0x91,
    chr(0x2019): 0x92,
    chr(0x201C): 0x93,
    chr(0x201D): 0x94,
    chr(0x2022): 0x95,
    chr(0x2013): 0x96,
    chr(0x2014): 0x97,
    chr(0x02DC): 0x98,
    chr(0x2122): 0x99,
    chr(0x0161): 0x9A,
    chr(0x203A): 0x9B,
    chr(0x0153): 0x9C,
    chr(0x017E): 0x9E,
    chr(0x0178): 0x9F,
}
_MOJIBAKE_MARKERS = (
    "Ãƒ",
    "Ã‚",
    "Ã„",
    "Ã…",
    "Ã†",
    "Ã",
    "Ã‘",
    "Ã¡",
    "Ã¢",
    chr(0x0192),
    chr(0x2018),
    chr(0x2019),
    chr(0x201C),
    chr(0x201D),
    chr(0x2026),
)
_REFERENCE_YEAR_MARKERS = (
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


def _mojibake_score(value: str) -> int:
    return sum(value.count(marker) for marker in _MOJIBAKE_MARKERS)


def _encode_cp1252ish(value: str) -> bytes:
    raw_bytes = bytearray()
    for index, char in enumerate(value):
        code_point = ord(char)
        if code_point <= 255:
            raw_bytes.append(code_point)
            continue

        mapped_byte = _CP1252_REVERSE_MAP.get(char)
        if mapped_byte is None:
            raise UnicodeEncodeError(
                "cp1252ish", value, index, index + 1, "character not mappable"
            )
        raw_bytes.append(mapped_byte)
    return bytes(raw_bytes)


def repair_mojibake_text(value: Optional[str]) -> str:
    text = str(value or "")
    if not text or _mojibake_score(text) == 0:
        return text

    repaired = text
    for _ in range(3):
        try:
            candidate = _encode_cp1252ish(repaired).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if _mojibake_score(candidate) >= _mojibake_score(repaired):
            break
        repaired = candidate

    return repaired


def _answer_acknowledges_reference_year(answer: str, reference_year: int) -> bool:
    normalized = normalize_text(answer)
    if str(reference_year) not in normalized:
        return False

    has_reference_marker = any(marker in normalized for marker in _REFERENCE_YEAR_MARKERS)
    has_reference_year_context = any(
        phrase in normalized
        for phrase in (
            f"nam {reference_year}",
            f"quy dinh cua nam {reference_year}",
            f"tai lieu nam {reference_year}",
            f"thong tin nam {reference_year}",
        )
    )
    return has_reference_marker and has_reference_year_context


def _answer_mentions_system_wide_context(answer: str) -> bool:
    normalized = normalize_text(answer)
    return any(
        phrase in normalized
        for phrase in (
            "toan khoi cand",
            "cac truong cand",
            "toan he thong",
            "toan bo cac truong cand",
            "tong chi tieu cua cac truong cand",
            "bo cong an",
        )
    )


def normalize_answer_markdown(answer: str) -> str:
    if not answer:
        return answer

    normalized_answer = repair_mojibake_text(answer)
    normalized_answer = normalized_answer.replace("\r\n", "\n").replace("\r", "\n")
    normalized_answer = INLINE_TABLE_PATTERN.sub(r"\1\n\n\2", normalized_answer)

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

        if not is_table_line and previous_was_table and stripped and rebuilt[-1].strip():
            rebuilt.append("")

        rebuilt.append(line)
        previous_was_table = is_table_line

    return "\n".join(rebuilt)


def extract_table_cells(line: str) -> Optional[List[str]]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None

    body = stripped[1:]
    if body.endswith("|"):
        body = body[:-1]

    cells = [cell.strip() for cell in body.split("|")]
    if any(cell for cell in cells):
        return cells

    return [""] if stripped.strip("|").strip() == "" else None


def is_table_separator_cells(cells: List[str]) -> bool:
    return bool(cells) and all(TABLE_SEPARATOR_PATTERN.match(cell) for cell in cells)


def _format_table_row(cells: List[str]) -> str:
    return "| " + " | ".join(cell.strip() for cell in cells) + " |"


def _pad_table_cells(cells: List[str], target_columns: int) -> List[str]:
    if len(cells) >= target_columns:
        return cells[:target_columns]
    return cells + [""] * (target_columns - len(cells))


def _fill_blank_first_cells(rows: List[List[str]]) -> List[List[str]]:
    previous_first_cell = ""
    rebuilt_rows: List[List[str]] = []

    for row in rows:
        current_row = list(row)
        first_is_blank = current_row and not current_row[0].strip()
        other_cells_have_content = any(cell.strip() for cell in current_row[1:])

        if first_is_blank and other_cells_have_content and previous_first_cell:
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
        cells = extract_table_cells(line)
        if not cells:
            return None
        parsed_rows.append(cells)

    separator_start = next(
        (
            index
            for index, cells in enumerate(parsed_rows)
            if is_table_separator_cells(cells)
        ),
        None,
    )
    if separator_start is None or separator_start == 0:
        return None

    header_cells = [cell for cells in parsed_rows[:separator_start] for cell in cells]
    separator_cells: List[str] = []
    separator_end = separator_start
    while separator_end < len(parsed_rows) and is_table_separator_cells(
        parsed_rows[separator_end]
    ):
        separator_cells.extend(parsed_rows[separator_end])
        separator_end += 1

    if len(header_cells) != len(separator_cells) or len(header_cells) < 2:
        return None

    target_columns = len(header_cells)
    rebuilt_block = [
        _format_table_row(header_cells),
        _format_table_row(separator_cells),
    ]

    current_cells: List[str] = []
    for cells in parsed_rows[separator_end:]:
        if is_table_separator_cells(cells):
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
        cells = extract_table_cells(line)
        if not cells:
            return repaired_block
        parsed_rows.append(cells)

    separator_start = next(
        (
            index
            for index, cells in enumerate(parsed_rows)
            if is_table_separator_cells(cells)
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
        cell if TABLE_SEPARATOR_PATTERN.match(cell) else "---"
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
        if is_table_separator_cells(cells):
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
    del relevant_chunks

    violations: List[str] = []
    normalized_answer = normalize_text(answer)
    query_school_code = infer_query_school_metadata(query).get("school_code")
    answer_school_code = infer_query_school_metadata(answer).get("school_code")

    if query_school_code and answer_school_code and answer_school_code != query_school_code:
        violations.append("wrong_school_identity")
    elif query_targets_primary_school(query) and answer_school_code and answer_school_code != "T04":
        violations.append("wrong_school_identity")

    if query_targets_primary_school(query):
        wrong_t01_markers = (
            "hoc vien an ninh nhan dan",
            "ma truong t01",
            "ma truong la t01",
            "ky hieu truong anh",
            "ky hieu truong la anh",
        )
        if any(marker in normalized_answer for marker in wrong_t01_markers):
            violations.append("wrong_school_identity")

        compact_answer = normalized_answer.replace(" ", "")
        if "1870" in compact_answer and not _answer_mentions_system_wide_context(answer):
            violations.append("system_wide_quota_presented_as_t04")

    target_year = infer_target_year(query)
    current_year = dt.datetime.now().year
    if (
        is_admission_query(query)
        and not has_explicit_year(query)
        and target_year == current_year
    ):
        referenced_past_years = sorted(
            {
                int(year)
                for year in YEAR_PATTERN.findall(normalized_answer)
                if int(year) < current_year
            },
            reverse=True,
        )
        if referenced_past_years and not any(
            _answer_acknowledges_reference_year(answer, year)
            for year in referenced_past_years
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
    current_year = dt.datetime.now().year
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
- If the query targets T04 or explicitly names a school, do not replace it with a different school code or school name.
- Do not present whole-system CAND/BCA quota numbers as if they were specific to one school.
- If the user did not specify a year, treat the question as the current cycle year {current_year}.
- If the available documents only confirm older-year information, you may still answer using that material as reference, but you must label it clearly as reference or temporary basis and state that {current_year} depends on the latest official guidance.
- If the documents are insufficient, state that clearly instead of guessing.
- Prefer Markdown tables for quota, methods, and score questions.
- When you use a Markdown table, keep each row on a single line and keep the same number of columns in every row.
- Never leave the first cell blank to imitate merged rows; repeat the row label in every row.
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
- Nếu câu hỏi mặc định thuộc phạm vi Trường Đại học An ninh nhân dân (T04) hoặc người dùng đã nêu rõ một trường cụ thể, tuyệt đối không được đổi sang trường hoặc mã trường khác.
- Không được trình bày các con số chỉ tiêu toàn hệ thống CAND/Bộ Công an như thể là chỉ tiêu riêng của một trường.
- Nếu người dùng không nêu năm, phải hiểu theo chu kỳ tuyển sinh hiện tại năm {current_year}.
- Nếu tài liệu hiện có mới xác nhận đến năm cũ như 2025, vẫn được phép trả lời theo hướng tham khảo gần nhất, nhưng phải nói rõ đây là căn cứ tham khảo hoặc tạm thời và việc áp dụng cho {current_year} phụ thuộc hướng dẫn chính thức mới nhất.
- Nếu tài liệu không đủ căn cứ, phải nói rõ là chưa đủ căn cứ thay vì suy đoán.
- Với câu hỏi về chỉ tiêu, phương thức, điểm số, ưu tiên trình bày bằng bảng Markdown.
- Khi dùng bảng Markdown, mỗi hàng phải nằm trên một dòng duy nhất và mọi hàng phải có cùng số cột như hàng tiêu đề.
- Tuyệt đối không để trống ô đầu dòng để giả lập gộp dòng; hãy lặp lại nhãn dòng ở mọi hàng.
"""


def build_safe_admission_fallback_answer(
    query: str, violations: List[str], language: str = "vi"
) -> str:
    del query

    if language == "en":
        return (
            "I do not have enough safe evidence to confirm this answer from the current "
            "document set. I should only present verified admission information tied to "
            "the correct school scope and current cycle, so I am withholding the unsupported claim."
        )

    notices: List[str] = []
    if "wrong_school_identity" in violations:
        notices.append(
            "- Câu trả lời đang lệch phạm vi trường; với chatbot này phải bám đúng trường mà người dùng hỏi, mặc định ưu tiên T04."
        )
    if "system_wide_quota_presented_as_t04" in violations:
        notices.append(
            "- Không được biến chỉ tiêu toàn hệ thống CAND/Bộ Công an thành chỉ tiêu riêng của Trường Đại học An ninh nhân dân."
        )
    if "older_year_presented_as_current" in violations:
        notices.append(
            f"- Câu hỏi không nêu năm nên phải ưu tiên chu kỳ tuyển sinh hiện tại **{dt.datetime.now().year}**."
        )
    if not notices:
        notices.append("- Câu trả lời hiện tại chưa đủ căn cứ an toàn.")

    notice_block = "\n".join(notices)
    return (
        "Tôi chưa đủ căn cứ an toàn để khẳng định nội dung này từ bộ tài liệu hiện tại.\n\n"
        f"{notice_block}\n\n"
        "Vui lòng xem các tài liệu tuyển sinh chính thức mà hệ thống đã ưu tiên hiển thị theo đúng phạm vi Trường Đại học An ninh nhân dân (T04) hoặc trường mà bạn nêu rõ."
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


__all__ = [
    "YEAR_PATTERN",
    "build_answer_repair_prompt",
    "build_reference_year_bridge_answer",
    "build_safe_admission_fallback_answer",
    "extract_table_cells",
    "is_table_separator_cells",
    "normalize_answer_markdown",
    "normalize_text",
    "repair_mojibake_text",
    "validate_admission_answer",
]
