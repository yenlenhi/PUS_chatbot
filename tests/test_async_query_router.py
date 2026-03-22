import unicodedata

from src.services.async_rag_service import AsyncRAGService


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    normalized = normalized.replace("đ", "d").replace("Đ", "D")
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return normalized.lower()


def test_year_only_follow_up_triggers_rewrite_when_history_exists():
    service = AsyncRAGService()

    intent = service._classify_query("nam 2024", conv_turn_count=1)

    assert intent["needs_rewrite"] is True
    assert intent["needs_memory"] is False


def test_contextual_follow_up_phrase_triggers_rewrite_when_history_exists():
    service = AsyncRAGService()

    intent = service._classify_query("con nam 2024 thi sao", conv_turn_count=1)

    assert intent["needs_rewrite"] is True


def test_long_conversation_short_follow_up_can_load_memory():
    service = AsyncRAGService()

    intent = service._classify_query("nam 2024", conv_turn_count=5)

    assert intent["needs_rewrite"] is True
    assert intent["needs_memory"] is True


def test_self_contained_year_query_does_not_require_rewrite():
    service = AsyncRAGService()

    intent = service._classify_query("diem chuan nam 2024", conv_turn_count=1)

    assert intent["needs_rewrite"] is False


def test_local_follow_up_rewrite_keeps_score_context():
    service = AsyncRAGService()

    rewritten = service._rewrite_context_dependent_followup_locally(
        "nam 2024",
        "nam 2024",
        [{"role": "user", "content": "so sanh diem chuan cac nam"}],
    )

    assert rewritten is not None
    normalized = _normalize_text(rewritten)
    assert "so sanh diem chuan nam 2024 voi nam 2023" in normalized
    assert "t04" in normalized
