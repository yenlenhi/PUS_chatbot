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
    assert "Trường Đại học An ninh Nhân dân" in enriched_query


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
