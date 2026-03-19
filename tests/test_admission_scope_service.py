from src.services.admission_scope_service import AdmissionScopeService


def test_classify_admission_query():
    service = AdmissionScopeService()

    decision = service.classify("Điều kiện tuyển sinh và hồ sơ xét tuyển gồm những gì?")

    assert decision.scope == "admission"
    assert "tuyen sinh" in decision.matched_keywords


def test_classify_out_of_scope_query():
    service = AdmissionScopeService()

    decision = service.classify("Viết giúp tôi code Python để đọc file CSV")

    assert decision.scope == "out_of_scope"


def test_classify_ambiguous_image_only_query():
    service = AdmissionScopeService()

    decision = service.classify("", has_images=True)

    assert decision.scope == "ambiguous"


def test_classify_preserves_vietnamese_d_stroke_keywords():
    service = AdmissionScopeService()

    decision = service.classify("Đăng ký xét tuyển cần những gì?")

    assert decision.scope == "admission"
    assert "dang ky" in decision.matched_keywords or "xet tuyen" in decision.matched_keywords


def test_policy_answer_messages_are_defined():
    service = AdmissionScopeService()

    assert "tuyển sinh" in service.build_policy_answer("out_of_scope", "vi").lower()
    assert "official admission" in service.build_policy_answer(
        "insufficient_evidence", "en"
    ).lower()
