import datetime as dt

from src.utils.admission_document_priority import (
    compute_priority_adjustment,
    infer_target_year,
    is_admission_query,
)


def test_infer_target_year_defaults_to_current_cycle_for_admission_queries():
    assert is_admission_query("chi tieu tuyen sinh la bao nhieu")
    assert (
        infer_target_year("chi tieu tuyen sinh la bao nhieu") == dt.datetime.now().year
    )


def test_explicit_year_query_keeps_requested_year():
    assert infer_target_year("diem chuan tuyen sinh 2025") == 2025


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
