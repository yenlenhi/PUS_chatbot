from src.services import gemini_key_fallback as fallback


def test_candidate_auth_configs_prefer_vertex_then_gemini(monkeypatch):
    monkeypatch.setattr(fallback, "VERTEX_AI_API_KEYS", ["vertex-key"], raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_API_KEY", None, raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_USE_ADC", False, raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_PROJECT", "", raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_LOCATION", "global", raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_API_VERSION", "v1", raising=False)
    monkeypatch.setattr(fallback, "GEMINI_API_KEYS", ["gemini-key"], raising=False)
    monkeypatch.setattr(fallback, "GEMINI_API_KEY", None, raising=False)
    monkeypatch.setattr(fallback, "GEMINI_DEVELOPER_API_VERSION", "v1beta", raising=False)
    monkeypatch.setattr(fallback, "GENAI_PROVIDER_PRIORITY", ["vertex", "gemini"], raising=False)

    configs = fallback.get_candidate_genai_auth_configs()

    assert [config.provider for config in configs] == ["vertex", "gemini"]
    assert configs[0].api_key == "vertex-key"
    assert configs[1].api_key == "gemini-key"


def test_candidate_auth_configs_can_include_vertex_adc(monkeypatch):
    monkeypatch.setattr(fallback, "VERTEX_AI_API_KEYS", [], raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_API_KEY", None, raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_USE_ADC", True, raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_PROJECT", "demo-project", raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_LOCATION", "us-central1", raising=False)
    monkeypatch.setattr(fallback, "VERTEX_AI_API_VERSION", "v1", raising=False)
    monkeypatch.setattr(fallback, "GEMINI_API_KEYS", [], raising=False)
    monkeypatch.setattr(fallback, "GEMINI_API_KEY", None, raising=False)
    monkeypatch.setattr(fallback, "GENAI_PROVIDER_PRIORITY", ["vertex"], raising=False)

    configs = fallback.get_candidate_genai_auth_configs()

    assert len(configs) == 1
    assert configs[0].provider == "vertex"
    assert configs[0].use_adc is True
    assert configs[0].project == "demo-project"
    assert configs[0].location == "us-central1"
