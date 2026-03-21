import importlib
import sys


def test_school_personnel_query_does_not_force_grounding(monkeypatch):
    sys.modules.pop("src.services.gemini_service", None)
    gemini_module = importlib.import_module("src.services.gemini_service")
    monkeypatch.setattr(gemini_module, "ENABLE_GOOGLE_SEARCH_GROUNDING", True)

    instruction = gemini_module.get_grounding_instruction(
        "Hieu truong hien nay la ai", "vi"
    )

    assert instruction == ""


def test_personnel_news_query_can_still_enable_grounding(monkeypatch):
    sys.modules.pop("src.services.gemini_service", None)
    gemini_module = importlib.import_module("src.services.gemini_service")
    monkeypatch.setattr(gemini_module, "ENABLE_GOOGLE_SEARCH_GROUNDING", True)

    instruction = gemini_module.get_grounding_instruction(
        "Thong bao bo nhiem hieu truong moi nhat", "vi"
    )

    assert instruction != ""
