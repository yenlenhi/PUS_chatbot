from src.utils.admission_answer_guardrails import (
    build_reference_year_bridge_answer,
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
    answer = "Truong Dai hoc An ninh Nhan dan (T05) co 1.870 chi tieu trong nam 2026."

    violations = validate_admission_answer(query, answer)

    assert "wrong_school_code_t05" in violations
    assert "system_wide_quota_presented_as_t04" in violations


def test_validate_admission_answer_flags_2025_for_implicit_current_cycle():
    query = "moc thoi gian dang ky va nhap hoc"
    answer = "Nam 2025, thoi gian dang ky du tuyen bat dau tu thang 3."

    violations = validate_admission_answer(query, answer)

    assert "older_year_presented_as_current" in violations


def test_validate_admission_answer_allows_2025_when_clearly_marked_as_reference():
    query = "dieu kien ap dung cua tung phuong thuc xet tuyen"
    answer = (
        "Hien tai tai lieu duoc cung cap chi thong tin ve quy dinh cua nam 2025. "
        "Ban co the tham khao cac dieu kien nay lam co so, con viec ap dung cho 2026 "
        "se theo huong dan moi nhat."
    )

    violations = validate_admission_answer(query, answer)

    assert "older_year_presented_as_current" not in violations


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
    assert "| --- | --- | --- |" in answer
    assert "Dang ky du tuyen" in answer
    assert "15/3/2026" in answer
    assert "25/4/2026" in answer
    assert "30/8/2026" in answer


def test_normalize_answer_markdown_inserts_blank_lines_around_tables():
    raw_answer = (
        "1. Doi voi he Dai hoc chinh quy tuyen moi| Phuong thuc | Dieu kien |\n"
        "| --- | --- |\n"
        "| Phuong thuc 1 | Tuyen thang |\n"
        "### 2. Doi voi he Tien si"
    )

    normalized = normalize_answer_markdown(raw_answer)

    assert "tuyen moi\n\n| Phuong thuc | Dieu kien |" in normalized
    assert "| Phuong thuc 1 | Tuyen thang |\n\n### 2." in normalized


def test_normalize_answer_markdown_removes_blank_lines_inside_table():
    raw_answer = (
        "Su khac biet nhu sau:\n\n"
        "| Ma bai thi |\n\n"
        "| Phan Tu luan bat buoc |\n\n"
        "| Phan Trac nghiem tu chon |\n\n"
        "| :--- |\n\n"
        "| :--- |\n\n"
        "| :--- |\n\n"
        "| CA1 |\n\n"
        "| Ngu van |\n\n"
        "| Vat li |"
    )

    normalized = normalize_answer_markdown(raw_answer)

    assert "|\n\n| Phan" not in normalized
    assert (
        "| Ma bai thi | Phan Tu luan bat buoc | Phan Trac nghiem tu chon |"
        in normalized
    )
    assert "| :--- | :--- | :--- |" in normalized
    assert "| CA1 | Ngu van | Vat li |" in normalized


def test_normalize_answer_markdown_repairs_fragmented_multi_column_table():
    raw_answer = (
        "Bang diem tuyen sinh\n"
        "Toi da chuan hoa cac moc diem truy xuat duoc duoi dang bang de de doi chieu:\n\n"
        "| Nam\n\n"
        "| Nganh/Ma nganh\n\n"
        "| Diem | Ghi chu |\n\n"
        "| ---\n\n"
        "| ---\n\n"
        "| ---: | --- |\n\n"
        "| 2022\n\n"
        "| Nganh/nhom nganh\n\n"
        "| 14.69 | Theo tai lieu truy xuat |\n\n"
        "| 2023\n\n"
        "| Nganh/nhom nganh\n\n"
        "| 18.62 | Theo tai lieu truy xuat |"
    )

    normalized = normalize_answer_markdown(raw_answer)

    assert "| Nam | Nganh/Ma nganh | Diem | Ghi chu |" in normalized
    assert "| --- | --- | ---: | --- |" in normalized
    assert "| 2022 | Nganh/nhom nganh | 14.69 | Theo tai lieu truy xuat |" in normalized
    assert "| 2023 | Nganh/nhom nganh | 18.62 | Theo tai lieu truy xuat |" in normalized


def test_build_reference_year_bridge_answer_adds_current_cycle_disclaimer():
    bridged = build_reference_year_bridge_answer(
        "Noi dung tham khao tu tai lieu nam 2025.", language="vi"
    )

    assert "2026" in bridged
    assert "tham khao" in bridged
    assert "nam 2025" in bridged


def test_build_structured_score_answer_aggregates_all_years_from_primary_score_doc():
    query = "so sanh diem chuan cac nam"
    chunks = [
        {
            "source_file": "iem_Chuan_ai_Hoc_An_Ninh_Nhan_Dan_2020-2025.pdf",
            "heading_text": "Bang tong hop diem chuan",
            "content": (
                "Chi tiet diem chuan nam 2020 | Vung tuyen sinh | Doi tuong Nam (Diem chuan) | "
                "Doi tuong Nu (Diem chuan) || Phia Nam | 14.69 | 17.25 || "
                "Chi tiet diem chuan nam 2021 | Vung tuyen sinh | Doi tuong Nam (Diem chuan) | "
                "Doi tuong Nu (Diem chuan) || Phia Nam | 15.32 | 18.10 || "
                "Chi tiet diem chuan nam 2022 | Vung tuyen sinh | Doi tuong Nam (Diem chuan) | "
                "Doi tuong Nu (Diem chuan) || Phia Nam | 16.48 | 19.05 || "
                "Chi tiet diem chuan nam 2023 | Vung tuyen sinh | Doi tuong Nam (Diem chuan) | "
                "Doi tuong Nu (Diem chuan) || Phia Nam | 18.62 | 21.14 || "
                "Chi tiet diem chuan nam 2024 | Vung tuyen sinh | Doi tuong Nam (Diem chuan) | "
                "Doi tuong Nu (Diem chuan) || Phia Nam | 19.40 | 22.05 || "
                "Chi tiet diem chuan nam 2025 | Vung tuyen sinh | Doi tuong Nam (Diem chuan) | "
                "Doi tuong Nu (Diem chuan) || Phia Nam | 20.10 | 22.80 ||"
            ),
            "document_year": 2025,
        },
        {
            "source_file": "So_tay_BDCL_2025_T04.pdf",
            "heading_text": "So chuan",
            "content": "Noi dung khong phai diem chuan tuyen sinh.",
            "document_year": 2025,
        },
    ]

    answer = build_structured_admission_answer(query, chunks, language="vi")

    assert answer is not None
    assert "| --- | --- | ---: | ---: | ---: | --- |" in answer
    assert "| 2020 | Phia Nam | 14.69 | 17.25 |  |" in answer
    assert "| 2021 | Phia Nam | 15.32 | 18.10 |  |" in answer
    assert "| 2022 | Phia Nam | 16.48 | 19.05 |  |" in answer
    assert "| 2023 | Phia Nam | 18.62 | 21.14 |  |" in answer
    assert "| 2024 | Phia Nam | 19.40 | 22.05 |  |" in answer
    assert "| 2025 | Phia Nam | 20.10 | 22.80 |  |" in answer
