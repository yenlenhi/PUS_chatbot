import datetime as dt

from src.services.async_rag_service import AsyncRAGService
from src.utils.admission_document_priority import enrich_query_for_current_cycle


def test_implicit_admission_timeline_query_is_enriched_to_current_cycle():
    enriched_query, enriched = enrich_query_for_current_cycle(
        "moc thoi gian dang ky va xac nhan nhap hoc"
    )

    assert enriched is True
    assert f"nam {dt.datetime.now().year}" in enriched_query
    assert "ky tuyen sinh hien tai" in enriched_query


def test_explicit_admission_timeline_year_is_preserved():
    original_query = "moc thoi gian dang ky va xac nhan nhap hoc 2025"
    enriched_query, enriched = enrich_query_for_current_cycle(original_query)

    assert enriched is False
    assert enriched_query == original_query


def test_implicit_score_query_is_not_forced_into_current_cycle():
    original_query = "so sanh diem chuan"
    enriched_query, enriched = enrich_query_for_current_cycle(original_query)

    assert enriched is False
    assert enriched_query == original_query


def test_async_retrieval_query_defaults_to_current_cycle_for_implicit_timeline():
    service = AsyncRAGService()

    enriched_query, enriched = service._enrich_retrieval_query(
        "moc thoi gian dang ky va xac nhan nhap hoc",
        "moc thoi gian dang ky va xac nhan nhap hoc",
    )

    assert enriched is True
    assert f"nam {dt.datetime.now().year}" in enriched_query
    assert "ky tuyen sinh hien tai" in enriched_query


def test_async_score_comparison_query_prefers_multi_year_expansion_not_current_cycle():
    service = AsyncRAGService()

    enriched_query, enriched = service._enrich_retrieval_query(
        "so sanh diem chuan",
        "so sanh diem chuan",
    )

    assert enriched is True
    assert "cac nam" in enriched_query
    assert "xu huong" in enriched_query
    assert f"nam {dt.datetime.now().year}" not in enriched_query
    assert "ky tuyen sinh hien tai" not in enriched_query
