from src.utils.admission_answer_guardrails import (
    build_structured_admission_answer,
    normalize_answer_markdown,
    validate_admission_answer,
)
from src.utils.admission_document_priority import (
    filter_chunks_by_metadata,
    infer_document_metadata,
)


def test_infer_document_metadata_for_t04_quota_doc():
    metadata = infer_document_metadata(
        "Thong bao chi tieu tuyen sinh T04 2026.pdf",
        heading_text="Truong Dai hoc An ninh Nhan dan (T04)",
        content="Ky hieu truong ANS, chi tieu tuyen sinh 2026.",
    )

    assert metadata["school_code"] == "T04"
    assert metadata["school_symbol"] == "ANS"
    assert metadata["admission_cycle"] == 2026
    assert metadata["scope"] == "school_specific"
    assert metadata["doc_type"] == "quota"


def test_filter_chunks_by_metadata_prefers_t04_current_cycle_before_rerank():
    query = "thong tin ve chi tieu va to hop xet tuyen"
    chunks = [
        {
            "source_file": "Huong dan tuyen sinh CAND 2026.pdf",
            "heading_text": "Tong chi tieu cac truong CAND",
            "content": "Tong chi tieu toan bo cac truong CAND la 1870.",
        },
        {
            "source_file": "Thong bao chi tieu tuyen sinh T04 2026.pdf",
            "heading_text": "Truong Dai hoc An ninh Nhan dan (T04)",
            "content": "Ky hieu truong ANS, nhom nganh nghiep vu An ninh, 220 chi tieu.",
        },
    ]

    filtered, info = filter_chunks_by_metadata(query, chunks)

    assert info["applied"] is True
    assert filtered
    assert all(chunk.get("school_code") == "T04" for chunk in filtered)


def test_validate_admission_answer_flags_wrong_t05_and_systemwide_quota():
    query = "thong tin ve chi tieu va to hop xet tuyen"
    answer = (
        "Truong Dai hoc An ninh Nhan dan (T05) co 1.870 chi tieu trong nam 2026."
    )

    violations = validate_admission_answer(query, answer)

    assert "wrong_school_code_t05" in violations
    assert "system_wide_quota_presented_as_t04" in violations


def test_validate_admission_answer_flags_2025_for_implicit_current_cycle():
    query = "moc thoi gian dang ky va nhap hoc"
    answer = "Nam 2025, thoi gian dang ky du tuyen bat dau tu thang 3."

    violations = validate_admission_answer(query, answer)

    assert "older_year_presented_as_current" in violations


def test_build_structured_timeline_answer_from_retrieved_chunks():
    query = "moc thoi gian dang ky va xac nhan nhap hoc"
    chunks = [
        {
            "source_file": "Thong bao tuyen sinh T04 2026.pdf",
            "heading_text": "Moc thoi gian",
            "content": (
                "Dang ky du tuyen: Tu ngay 15/3/2026 den 25/4/2026.\n"
                "Xac nhan nhap hoc: Hoan thanh truoc 30/8/2026.\n"
                "Chieu sinh, nhap hoc: Tu ngay 23/9/2026 den 27/9/2026."
            ),
        }
    ]

    answer = build_structured_admission_answer(query, chunks, language="vi")

    assert answer is not None
    assert "| Mốc | Thời gian | Ghi chú |" in answer
    assert "15/3/2026 đến 25/4/2026" in answer
    assert "30/8/2026" in answer


def test_normalize_answer_markdown_inserts_blank_lines_around_tables():
    raw_answer = (
        "1. Đối với hệ Đại học chính quy tuyển mới| Phương thức | Điều kiện |\n"
        "| --- | --- |\n"
        "| Phương thức 1 | Tuyển thẳng |\n"
        "### 2. Đối với hệ Tiến sĩ"
    )

    normalized = normalize_answer_markdown(raw_answer)

    assert "tuyển mới\n\n| Phương thức | Điều kiện |" in normalized
    assert "| Phương thức 1 | Tuyển thẳng |\n\n### 2." in normalized
