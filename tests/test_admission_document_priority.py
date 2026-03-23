import datetime as dt

from src.utils.admission_document_priority import (
    compute_priority_adjustment,
    enrich_query_for_primary_school,
    enrich_query_for_current_cycle,
    filter_chunks_by_metadata,
    infer_document_metadata,
    infer_query_doc_type,
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


def test_personnel_query_maps_to_personnel_doc_type_and_primary_school():
    query = "hieu truong hien nay la ai"

    assert infer_query_doc_type(query) == "personnel"
    assert query_targets_primary_school(query) is True


def test_infer_document_metadata_marks_org_structure_pdf_as_personnel():
    metadata = infer_document_metadata(
        "Co_cau_to_chuc_va_Nhan_su_T04_Cap_nhat_2026.pdf",
        heading_text="Co cau to chuc va nhan su",
        content="Ban giam hieu va lanh dao nha truong.",
    )

    assert metadata["school_code"] == "T04"
    assert metadata["doc_type"] == "personnel"


def test_infer_document_metadata_preserves_multi_year_coverage():
    metadata = infer_document_metadata(
        "Tong_hop_diem_chuan_T04_giai_doan_2020_2025.pdf",
        heading_text="Tong hop diem chuan 2020-2025",
        content="Du lieu diem chuan cac nam 2020, 2021, 2022, 2023, 2024, 2025.",
    )

    assert metadata["admission_cycle"] == 2025
    assert metadata["admission_years"] == [2020, 2021, 2022, 2023, 2024, 2025]
    assert metadata["doc_type"] == "scores"


def test_infer_document_metadata_keeps_training_regulation_out_of_timeline_doc_type():
    metadata = infer_document_metadata(
        "Quy_che_dao_tao_dai_hoc.pdf",
        heading_text="Quy che dao tao dai hoc",
        content=(
            "Thong tin ve dang ky hoc phan, nhap hoc va cac moc thoi gian lien quan "
            "den quy trinh dao tao."
        ),
    )

    assert metadata["doc_type"] == "general"


def test_filter_chunks_by_metadata_prefers_t04_personnel_document():
    query = "hieu truong hien nay la ai"
    chunks = [
        {
            "source_file": "Co_cau_to_chuc_va_Nhan_su_T04_Cap_nhat_2026.pdf",
            "heading_text": "Co cau to chuc va nhan su",
            "content": "Ban giam hieu va lanh dao nha truong.",
        },
        {
            "source_file": "Bai_phat_bieu_tong_ket_2021.pdf",
            "heading_text": "Phat bieu cua hieu truong",
            "content": "Noi dung tong ket co nhac den ten hieu truong cu.",
        },
    ]

    filtered, info = filter_chunks_by_metadata(query, chunks)

    assert info["applied"] is True
    assert filtered
    assert all(chunk.get("doc_type") == "personnel" for chunk in filtered)
    assert all(chunk.get("school_code") == "T04" for chunk in filtered)


def test_priority_adjustment_prefers_newer_personnel_document_over_older_one():
    query = "hieu truong hien nay la ai"
    current_year = dt.datetime.now().year

    newer_chunk = {
        "source_file": f"Co_cau_to_chuc_va_Nhan_su_T04_Cap_nhat_{current_year}.pdf",
        "content": f"Ban giam hieu va lanh dao nha truong nam {current_year}.",
    }
    older_chunk = {
        "source_file": "Co_cau_to_chuc_va_Nhan_su_T04_2021.pdf",
        "content": "Ban giam hieu va lanh dao nha truong nam 2021.",
    }

    assert compute_priority_adjustment(
        query, newer_chunk
    ) > compute_priority_adjustment(query, older_chunk)


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


def test_priority_adjustment_prefers_timeline_notice_over_training_regulation():
    query = "toi muon biet moc thoi gian dang ky va xac nhan nhap hoc"

    notice_chunk = {
        "source_file": "Thong_bao_tuyen_sinh_T04_2026.pdf",
        "heading_text": "Moc thoi gian dang ky va nhap hoc",
        "content": (
            "Dang ky du tuyen tu 15/3/2026 den 25/4/2026. "
            "Xac nhan nhap hoc truoc 30/8/2026."
        ),
    }
    regulation_chunk = {
        "source_file": "Quy_che_dao_tao_dai_hoc.pdf",
        "heading_text": "Quy che dao tao dai hoc",
        "content": (
            "4. Trieu tap hoc vien trung tuyen va nhap hoc. "
            "a) Giay bao nhap hoc. "
            "Trong thoi gian khong qua 05 ngay lam viec, Hieu truong ban hanh quyet dinh."
        ),
    }

    assert compute_priority_adjustment(query, notice_chunk) > compute_priority_adjustment(
        query, regulation_chunk
    )


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


def test_eligibility_query_maps_to_eligibility_not_timeline():
    query = "tieu chuan suc khoe, chinh tri hoac do tuoi"

    assert infer_query_doc_type(query) == "eligibility"


def test_exam_schedule_query_maps_to_exam_before_timeline():
    query = "ngay thi va thoi gian lam bai cu the ra sao"

    assert infer_query_doc_type(query) == "exam"


def test_filter_chunks_by_metadata_prefers_eligibility_docs_over_timeline_docs():
    query = "tieu chuan suc khoe, chinh tri hoac do tuoi"
    chunks = [
        {
            "source_file": "Thong_bao_tuyen_sinh_T04_2026.pdf",
            "content": "Tieu chuan suc khoe, ly lich chinh tri va do tuoi doi voi thi sinh du tuyen.",
            "school_code": "T04",
            "admission_cycle": dt.datetime.now().year,
            "doc_type": "eligibility",
            "scope": "school_specific",
        },
        {
            "source_file": "Thong_bao_tuyen_sinh_T04_2026.pdf",
            "content": "Moc thoi gian dang ky, xac nhan nhap hoc va nhap hoc.",
            "school_code": "T04",
            "admission_cycle": dt.datetime.now().year,
            "doc_type": "timeline",
            "scope": "school_specific",
        },
    ]

    filtered, metadata = filter_chunks_by_metadata(query, chunks)

    assert metadata["applied"] is True
    assert all(chunk.get("doc_type") == "eligibility" for chunk in filtered)


def test_filter_chunks_by_metadata_matches_multi_year_score_doc_for_requested_year():
    query = "diem chuan truong dai hoc an ninh nhan dan 2024"
    chunks = [
        {
            "source_file": "Tong_hop_diem_chuan_T04_2020_2025.pdf",
            "school_code": "T04",
            "doc_type": "scores",
            "scope": "school_specific",
            "admission_cycle": 2025,
            "admission_years": [2020, 2021, 2022, 2023, 2024, 2025],
            "content": "Du lieu diem chuan 2020-2025.",
        },
        {
            "source_file": "Thong_bao_tuyen_sinh_T04_2026.pdf",
            "school_code": "T04",
            "doc_type": "methods",
            "scope": "school_specific",
            "admission_cycle": 2026,
            "content": "Phuong thuc tuyen sinh 2026.",
        },
    ]

    filtered, metadata = filter_chunks_by_metadata(query, chunks)

    assert metadata["applied"] is True
    assert metadata["stage"] == "strict_school_cycle_doc_type"
    assert [chunk["source_file"] for chunk in filtered] == [
        "Tong_hop_diem_chuan_T04_2020_2025.pdf"
    ]


def test_filter_chunks_by_metadata_prefers_t04_general_doc_before_wrong_school_doc_type_match():
    query = "diem chuan truong dai hoc an ninh nhan dan 2026"
    chunks = [
        {
            "source_file": "wrong_school_scores.pdf",
            "school_code": "T05",
            "doc_type": "scores",
            "scope": "school_specific",
            "content": "Diem chuan cua truong khac.",
        },
        {
            "source_file": "t04_general.pdf",
            "school_code": "T04",
            "doc_type": "general",
            "scope": "school_specific",
            "content": "Thong tin tong hop cua T04.",
        },
    ]

    filtered, metadata = filter_chunks_by_metadata(query, chunks)

    assert metadata["applied"] is True
    assert metadata["stage"] in {"school_only_non_score", "school_only"}
    assert [chunk["source_file"] for chunk in filtered] == ["t04_general.pdf"]


def test_priority_adjustment_treats_multi_year_doc_as_exact_match_for_requested_year():
    query = "diem chuan truong dai hoc an ninh nhan dan 2024"
    multi_year_chunk = {
        "source_file": "Tong_hop_diem_chuan_T04_2020_2025.pdf",
        "content": "Du lieu diem chuan 2020-2025.",
        "document_year": 2025,
        "admission_years": [2020, 2021, 2022, 2023, 2024, 2025],
    }
    unrelated_newer_chunk = {
        "source_file": "Thong_bao_tuyen_sinh_T04_2026.pdf",
        "content": "Thong bao tuyen sinh nam 2026.",
        "document_year": 2026,
        "doc_type": "methods",
    }

    assert compute_priority_adjustment(
        query, multi_year_chunk
    ) > compute_priority_adjustment(query, unrelated_newer_chunk)
