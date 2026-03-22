from src.services.async_rag_service import AsyncRAGService


def test_score_query_is_enriched_for_retrieval():
    service = AsyncRAGService()

    enriched_query, enriched = service._enrich_retrieval_query(
        "điểm tuyển sinh", "điểm tuyển sinh"
    )

    assert enriched is True
    assert "điểm chuẩn tuyển sinh" in enriched_query
    assert "điểm xét tuyển" in enriched_query
    assert "điểm trúng tuyển" in enriched_query
    assert "Trường Đại Học An Ninh Nhân Dân T04" in enriched_query
    assert "ANS" not in enriched_query


def test_low_context_score_query_returns_clarification():
    service = AsyncRAGService()

    should_clarify = service._should_return_score_clarification(
        "điểm tuyển sinh", "điểm tuyển sinh"
    )

    assert should_clarify is True


def test_specific_score_query_does_not_force_clarification():
    service = AsyncRAGService()

    should_clarify = service._should_return_score_clarification(
        "điểm chuẩn tuyển sinh 2025", "điểm chuẩn tuyển sinh 2025"
    )

    assert should_clarify is False


def test_specific_score_query_with_score_chunks_bypasses_low_confidence_policy():
    service = AsyncRAGService()

    should_bypass = service._should_bypass_low_confidence_policy(
        "điểm chuẩn năm 2024",
        "điểm chuẩn năm 2024",
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
        "điểm tuyển sinh",
        "điểm tuyển sinh",
        [
            {
                "source_file": "iem_Chuan_ai_Hoc_An_Ninh_Nhan_Dan_1_.pdf",
                "heading_text": "Bang diem chuan",
                "content": "Chi tiet diem chuan nam 2024 | Vung 4 | 21.07 | 24.72",
            }
        ],
    )

    assert should_bypass is False
