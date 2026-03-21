from src.services.async_rag_service import AsyncRAGService


def test_year_only_follow_up_triggers_rewrite_when_history_exists():
    service = AsyncRAGService()

    intent = service._classify_query("năm 2024", conv_turn_count=1)

    assert intent["needs_rewrite"] is True
    assert intent["needs_memory"] is False


def test_contextual_follow_up_phrase_triggers_rewrite_when_history_exists():
    service = AsyncRAGService()

    intent = service._classify_query("còn năm 2024 thì sao", conv_turn_count=1)

    assert intent["needs_rewrite"] is True


def test_long_conversation_short_follow_up_can_load_memory():
    service = AsyncRAGService()

    intent = service._classify_query("nam 2024", conv_turn_count=5)

    assert intent["needs_rewrite"] is True
    assert intent["needs_memory"] is True


def test_self_contained_year_query_does_not_require_rewrite():
    service = AsyncRAGService()

    intent = service._classify_query("điểm chuẩn năm 2024", conv_turn_count=1)

    assert intent["needs_rewrite"] is False
