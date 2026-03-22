import datetime as dt

from src.utils.admission_document_priority import (
    compute_priority_adjustment,
    enrich_query_for_primary_school,
    enrich_query_for_current_cycle,
    filter_chunks_by_metadata,
    infer_target_year,
    is_admission_query,
    is_personnel_query,
    query_targets_primary_school,
)


def test_infer_target_year_defaults_to_current_cycle_for_admission_queries():
    assert is_admission_query("chi tieu tuyen sinh la bao nhieu")
    assert (
        infer_target_year("chi tieu tuyen sinh la bao nhieu") == dt.datetime.now().year
    )


def test_explicit_year_query_keeps_requested_year():
    assert infer_target_year("diem chuan tuyen sinh 2025") == 2025


def test_current_cycle_enrichment_adds_current_year_for_implicit_timeline_query():
    enriched_query, enriched = enrich_query_for_current_cycle(
        "moc thoi gian dang ky va xac nhan nhap hoc"
    )

    assert enriched is True
    assert f"nam {dt.datetime.now().year}" in enriched_query
    assert "ky tuyen sinh hien tai" in enriched_query


def test_current_cycle_enrichment_keeps_explicit_year_query_unchanged():
    original_query = "moc thoi gian dang ky va xac nhan nhap hoc 2025"
    enriched_query, enriched = enrich_query_for_current_cycle(original_query)

    assert enriched is False
    assert enriched_query == original_query


def test_priority_adjustment_prefers_2026_for_current_cycle_queries():
    current_cycle_query = "chi tieu tuyen sinh nam nay"

    newer_chunk = {
        "source_file": "Thong bao chi tieu tuyen sinh 2026.pdf",
        "content": "Chi tieu tuyen sinh dai hoc nam 2026.",
    }
    older_chunk = {
        "source_file": "Thong bao chi tieu tuyen sinh 2025.pdf",
        "content": "Chi tieu tuyen sinh dai hoc nam 2025.",
    }

    assert compute_priority_adjustment(
        current_cycle_query, newer_chunk
    ) > compute_priority_adjustment(current_cycle_query, older_chunk)


def test_priority_adjustment_respects_explicit_2025_query():
    query = "chi tieu tuyen sinh 2025"

    newer_chunk = {
        "source_file": "Thong bao chi tieu tuyen sinh 2026.pdf",
        "content": "Chi tieu tuyen sinh dai hoc nam 2026.",
    }
    requested_chunk = {
        "source_file": "Thong bao chi tieu tuyen sinh 2025.pdf",
        "content": "Chi tieu tuyen sinh dai hoc nam 2025.",
    }

    assert compute_priority_adjustment(query, requested_chunk) > compute_priority_adjustment(
        query, newer_chunk
    )


def test_personnel_query_prefers_org_structure_document():
    query = "hieu truong hien nay la ai"

    org_chunk = {
        "source_file": "Co_cau_to_chuc_va_Nhan_su_T04_Cap_nhat.pdf",
        "content": "Ban giam hieu va lanh dao nha truong.",
    }
    generic_chunk = {
        "source_file": "gioi_thieu.pdf",
        "content": "Thong tin gioi thieu chung ve nha truong.",
    }

    assert is_personnel_query(query)
    assert compute_priority_adjustment(query, org_chunk) > compute_priority_adjustment(
        query, generic_chunk
    )


def test_primary_school_enrichment_applies_to_generic_admission_query():
    query = "thong tin ve chi tieu va to hop xet tuyen"

    enriched_query, enriched = enrich_query_for_primary_school(query)

    assert query_targets_primary_school(query)
    assert enriched is True
    assert "Trường Đại Học An Ninh Nhân Dân" in enriched_query
    assert "T04" in enriched_query
    assert "ANS" not in enriched_query


def test_priority_adjustment_prefers_t04_over_system_wide_or_t05_chunks():
    query = "thong tin ve chi tieu va to hop xet tuyen"

    t04_chunk = {
        "source_file": "Thong bao chi tieu tuyen sinh T04 2026.pdf",
        "heading_text": "Truong Dai hoc An ninh Nhan dan (T04)",
        "content": "Ky hieu truong ANS, nhom nganh nghiep vu An ninh, phia Nam, 220 chi tieu.",
    }
    system_wide_chunk = {
        "source_file": "Huong dan tuyen sinh CAND 2026.pdf",
        "heading_text": "Tong chi tieu cac truong CAND",
        "content": "Tong chi tieu toan bo cac truong CAND la 1870.",
    }
    t05_chunk = {
        "source_file": "Thong bao tuyen sinh T05 2026.pdf",
        "heading_text": "Truong Dai hoc T05",
        "content": "Thong tin chi tieu tuyen sinh cua truong T05.",
    }

    t04_score = compute_priority_adjustment(query, t04_chunk)
    system_score = compute_priority_adjustment(query, system_wide_chunk)
    t05_score = compute_priority_adjustment(query, t05_chunk)

    assert t04_score > system_score
    assert t04_score > t05_score


def test_filter_chunks_by_metadata_prefers_method_docs_over_score_docs():
    query = "dieu kien ap dung cua tung phuong thuc xet tuyen"
    chunks = [
        {
            "source_file": "Thong_bao_tuyen_sinh_T04_2026.pdf",
            "content": "Phuong thuc 1, phuong thuc 2, phuong thuc 3.",
            "school_code": "T04",
            "admission_cycle": dt.datetime.now().year,
            "doc_type": "methods",
            "scope": "school_specific",
        },
        {
            "source_file": "Diem_chuan_T04_2025.pdf",
            "content": "Diem chuan nam 2025.",
            "school_code": "T04",
            "admission_cycle": 2025,
            "doc_type": "scores",
            "scope": "school_specific",
        },
    ]

    filtered, metadata = filter_chunks_by_metadata(query, chunks)

    assert metadata["applied"] is True
    assert all(chunk.get("doc_type") == "methods" for chunk in filtered)
