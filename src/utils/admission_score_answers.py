"""
Score-specific structured answer helpers for admission answers.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from src.utils.admission_answer_normalization import (
    YEAR_PATTERN,
    extract_table_cells,
    is_table_separator_cells,
    normalize_text,
)
from src.utils.admission_document_priority import has_explicit_year, infer_target_year

_SCORE_ROW_PATTERN = re.compile(
    r"\b(20\d{2})\b.*?\b(\d{2}(?:[.,]\d{1,2})?)\b",
    re.IGNORECASE,
)
_SCORE_VALUE_PATTERN = re.compile(r"\b\d{2}(?:[.,]\d{1,2})?\b")


def build_structured_score_answer(
    query: str, chunks: List[Dict[str, object]]
) -> Optional[str]:
    def _score_source_priority(chunk: Dict[str, object]) -> tuple[float, int]:
        source_file = str(chunk.get("source_file") or chunk.get("source") or "")
        heading = str(chunk.get("heading_text") or chunk.get("heading") or "")
        content = str(chunk.get("content") or "")
        normalized = normalize_text(" ".join([source_file, heading, content[:400]]))

        priority = 0.0
        if "diem chuan" in normalized or "diem trung tuyen" in normalized:
            priority += 6.0
        if "giai doan" in normalized or re.search(
            r"20\d{2}\s*[-_]\s*20\d{2}", source_file
        ):
            priority += 2.0
        if "t04" in normalized or "ans" in normalized:
            priority += 1.5

        document_year = chunk.get("document_year")
        if isinstance(document_year, int):
            priority += document_year / 10000.0

        return priority, len(content)

    def _select_primary_score_chunks() -> List[Dict[str, object]]:
        groups: Dict[str, Dict[str, object]] = {}
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
        normalized = normalize_text(text)
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
            (r"\bPhia Nam\b", "Phia Nam"),
            (r"\bPhia Bac\b", "Phia Bac"),
            (r"\bDia ban\b", "Dia ban"),
            (r"\bVung\b", "Vung"),
            (r"\bNu\b", "Nu"),
            (r"\bDoi tuong\b", "Doi tuong"),
            (r"\bNganh/nhom nganh\b", "Nganh/nhom nganh"),
        )
        for pattern, replacement in replacements:
            pretty = re.sub(pattern, replacement, pretty, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", pretty).strip(" /")

    def _looks_like_region(value: str) -> bool:
        normalized = normalize_text(value)
        return any(
            term in normalized
            for term in ("vung", "dia ban", "phia nam", "phia bac", "khu vuc")
        )

    def _looks_like_object(value: str) -> bool:
        return normalize_text(value) in {"nam", "nu"}

    def _looks_like_header_cell(value: str) -> bool:
        normalized = normalize_text(value)
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
        normalized = normalize_text(region)
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
            return f"Chua co du lieu {previous_year}"

        try:
            delta = float(current_score) - float(previous_score)
        except ValueError:
            return f"So voi {previous_year}: {previous_score}"

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
        normalized_region = normalize_text(region or "nganh nhom nganh")
        normalized_object = normalize_text(object_name)
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
                "region": region or "Nganh/nhom nganh",
                "object": object_name,
                "exam_code": normalized_exam_code,
                "score": score,
            }
        )

    for chunk in primary_chunks:
        heading = str(chunk.get("heading_text") or chunk.get("heading") or "").strip()
        default_region = _beautify_text(heading) if heading else "Nganh/nhom nganh"
        if normalize_text(default_region) in {
            "bang tong hop diem chuan",
            "bang diem chuan",
            "chi tiet diem chuan",
        }:
            default_region = "Nganh/nhom nganh"

        current_year: Optional[str] = None
        segments = _split_score_segments(str(chunk.get("content") or ""))

        for segment in segments:
            segment_years = YEAR_PATTERN.findall(segment)
            if segment_years and (
                _contains_score_header(segment) or "nam " in normalize_text(segment)
            ):
                current_year = segment_years[-1]

            table_candidate = segment
            if "|" in segment and not segment.lstrip().startswith("|"):
                table_candidate = f"| {segment.strip().strip('|')} |"

            cells = extract_table_cells(table_candidate)
            if cells:
                if is_table_separator_cells(cells):
                    continue

                row_year = current_year
                label_cells: List[str] = []
                score_values: List[str] = []

                for cell in cells:
                    normalized_cell = normalize_text(cell)
                    if not normalized_cell:
                        continue

                    cell_years = YEAR_PATTERN.findall(cell)
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
                        for object_label, score in zip(
                            ("Nam", "Nu"), score_values[:2]
                        ):
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
        if normalize_text(entry["region"]) not in {"nganh nhom nganh", ""}
    }
    entries = [
        entry
        for entry in entries
        if not (
            normalize_text(entry["region"]) == "nganh nhom nganh"
            and entry["year"] in detailed_years
        )
    ]
    if not entries:
        return None

    available_years = sorted(
        {int(entry["year"]) for entry in entries if entry["year"].isdigit()}
    )
    normalized_query = normalize_text(query)
    broad_history_intent = any(
        term in normalized_query for term in ("cac nam", "giai doan", "lich su")
    )
    comparison_intent = any(
        term in normalized_query for term in ("so sanh", "xu huong")
    )
    explicit_year = infer_target_year(query) if has_explicit_year(query) else None

    def _comparison_year() -> Optional[int]:
        if explicit_year and explicit_year in available_years:
            return explicit_year

        paired_years = [year for year in available_years if year - 1 in available_years]
        if paired_years:
            return max(paired_years)

        return max(available_years) if available_years else None

    should_build_comparison = explicit_year is not None or (
        comparison_intent and not broad_history_intent
    )
    target_year = _comparison_year() if should_build_comparison else None

    if should_build_comparison and target_year is not None:
        previous_year = target_year - 1
        target_entries = [
            entry for entry in entries if int(entry["year"]) == target_year
        ]
        if target_entries:
            previous_scores = {
                (
                    normalize_text(entry["region"]),
                    normalize_text(entry["object"]),
                    entry["exam_code"],
                ): entry["score"]
                for entry in entries
                if int(entry["year"]) == previous_year
            }

            target_entries.sort(
                key=lambda entry: (
                    _sort_region_key(entry["region"]),
                    {"nam": 0, "nu": 1}.get(normalize_text(entry["object"]), 9),
                    entry["exam_code"] or "ZZZ",
                    entry["score"],
                )
            )

            lines = [
                "### Bang so sanh diem chuan",
                "",
                f"Toi dang uu tien tai lieu diem chuan theo dung pham vi T04 va so sanh nam {target_year} voi nam {previous_year} de ban de doi chieu.",
                "",
                f"| Vung | Doi tuong | Ma bai thi | Diem chuan {target_year} | Xu huong (so voi {previous_year}) |",
                "| --- | --- | --- | ---: | --- |",
            ]

            for entry in target_entries:
                comparison_key = (
                    normalize_text(entry["region"]),
                    normalize_text(entry["object"]),
                    entry["exam_code"],
                )
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            entry["region"] or "Nganh/nhom nganh",
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
                        "Giai doan tai lieu dang bao phu: "
                        + ", ".join(str(year) for year in available_years)
                        + ".",
                    ]
                )

            return "\n".join(lines)

    entries.sort(
        key=lambda entry: (
            int(entry["year"]) if entry["year"].isdigit() else 0,
            _sort_region_key(entry["region"]),
            {"nam": 0, "nu": 1}.get(normalize_text(entry["object"]), 9),
            entry["exam_code"] or "ZZZ",
            entry["score"],
        )
    )

    lines = [
        "### Bang diem tuyen sinh",
        "",
        "Toi da chuan hoa cac moc diem truy xuat duoc tu tai lieu diem chuan de ban de doi chieu.",
        "",
        "| Nam | Hang muc | Diem |",
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
                "Cac moc diem truy xuat duoc hien dang bao phu "
                f"{available_years[0]}-{available_years[-1]}.",
            ]
        )

    return "\n".join(lines)


__all__ = ["build_structured_score_answer"]
