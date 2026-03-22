from src.services.async_rag_service import AsyncRAGService


def test_score_query_is_enriched_for_retrieval():
    service = AsyncRAGService()

    enriched_query, enriched = service._enrich_retrieval_query(
        "diem tuyen sinh", "diem tuyen sinh"
    )

    assert enriched is True
    assert "diem chuan tuyen sinh" in enriched_query
    assert "diem xet tuyen" in enriched_query
    assert "diem trung tuyen" in enriched_query
    assert "T04" in enriched_query
    assert "ANS" not in enriched_query


def test_score_comparison_query_expands_to_multi_year_terms_without_current_cycle_bias():
    service = AsyncRAGService()

    enriched_query, enriched = service._enrich_retrieval_query(
        "so sanh diem chuan", "so sanh diem chuan"
    )

    assert enriched is True
    assert "cac nam" in enriched_query
    assert "xu huong" in enriched_query
    assert "ky tuyen sinh hien tai" not in enriched_query


def test_low_context_score_query_returns_clarification():
    service = AsyncRAGService()

    should_clarify = service._should_return_score_clarification(
        "diem tuyen sinh", "diem tuyen sinh"
    )

    assert should_clarify is True


def test_specific_score_query_does_not_force_clarification():
    service = AsyncRAGService()

    should_clarify = service._should_return_score_clarification(
        "diem chuan tuyen sinh 2025", "diem chuan tuyen sinh 2025"
    )

    assert should_clarify is False


def test_specific_score_query_with_score_chunks_bypasses_low_confidence_policy():
    service = AsyncRAGService()

    should_bypass = service._should_bypass_low_confidence_policy(
        "diem chuan nam 2024",
        "diem chuan nam 2024",
        [
            {
                "source_file": "iem_Chuan_ai_Hoc_An_Ninh_Nhan_Dan_1_.pdf",
                "heading_text": "Bang diem chuan",
                "content": "Chi tiet diem chuan nam 2024 | Vung 4 | 21.07 | 24.72",
            }
        ],
    )

    assert should_bypass is True


def test_under_specified_score_query_does_not_bypass_low_confidence_policy():
    service = AsyncRAGService()

    should_bypass = service._should_bypass_low_confidence_policy(
        "diem tuyen sinh",
        "diem tuyen sinh",
        [
            {
                "source_file": "iem_Chuan_ai_Hoc_An_Ninh_Nhan_Dan_1_.pdf",
                "heading_text": "Bang diem chuan",
                "content": "Chi tiet diem chuan nam 2024 | Vung 4 | 21.07 | 24.72",
            }
        ],
    )

    assert should_bypass is False


def test_personnel_query_is_enriched_for_org_structure_retrieval():
    service = AsyncRAGService()

    enriched_query, enriched = service._enrich_retrieval_query(
        "ai la hieu truong", "ai la hieu truong"
    )

    assert enriched is True
    assert "co cau to chuc" in enriched_query
    assert "nhan su" in enriched_query
    assert "ban giam hieu" in enriched_query


def test_personnel_query_requires_authoritative_personnel_chunk():
    service = AsyncRAGService()

    filtered_chunks, required = service._filter_authoritative_personnel_chunks(
        "ai la hieu truong",
        "ai la hieu truong",
        [
            {
                "source_file": "Quy_che_dao_tao_dai_hoc.pdf",
                "heading_text": "Quy che dao tao",
                "content": "Mot doan van ban cu co nhac den ten hieu truong.",
                "doc_type": "general",
            }
        ],
    )

    assert required is True
    assert filtered_chunks == []


def test_personnel_query_with_org_structure_chunk_bypasses_low_confidence_policy():
    service = AsyncRAGService()

    should_bypass = service._should_bypass_low_confidence_policy(
        "ai la hieu truong",
        "ai la hieu truong",
        [
            {
                "source_file": "Co_cau_to_chuc_va_Nhan_su_T04_Cap_nhat_2026.pdf",
                "heading_text": "Co cau to chuc va nhan su",
                "content": "Ban giam hieu va lanh dao nha truong.",
                "doc_type": "personnel",
                "school_code": "T04",
            }
        ],
    )

    assert should_bypass is True


def test_timeline_query_with_grounded_timeline_chunk_bypasses_low_confidence_policy():
    service = AsyncRAGService()

    should_bypass = service._should_bypass_low_confidence_policy(
        "toi muon biet moc thoi gian dang ky va xac nhan nhap hoc",
        "toi muon biet moc thoi gian dang ky va xac nhan nhap hoc",
        [
            {
                "source_file": "Thong_bao_tuyen_sinh_T04_2026.pdf",
                "heading_text": "Moc thoi gian dang ky va nhap hoc",
                "content": (
                    "Dang ky du tuyen tu 15/3/2026 den 25/4/2026. "
                    "Xac nhan nhap hoc truoc 30/8/2026."
                ),
                "doc_type": "timeline",
                "school_code": "T04",
            }
        ],
    )

    assert should_bypass is True
