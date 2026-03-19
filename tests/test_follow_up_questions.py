import pytest

pytest.importorskip("numpy")
pytest.importorskip("sentence_transformers")

from src.services.rag_service import RAGService


def _make_service() -> RAGService:
    return RAGService.__new__(RAGService)


def test_structured_follow_ups_for_score_answer_are_contextual():
    service = _make_service()

    questions = service.generate_structured_follow_up_questions(
        user_query="Điểm chuẩn tuyển sinh 2025 là bao nhiêu?",
        answer="Điểm chuẩn tuyển sinh năm 2025 đã được công bố cho từng ngành.",
        language="vi",
        sources=["Thong bao tuyen sinh 2025", "Diem chuan 2025"],
        attachments=[],
    )

    assert len(questions) >= 2
    assert any("điểm chuẩn theo từng ngành năm 2025" in q.lower() for q in questions)
    assert any("so sánh điểm chuẩn năm 2025" in q.lower() for q in questions)
    assert all(not q.lower().startswith("bạn muốn") for q in questions)


def test_structured_follow_ups_for_document_answer_surface_download_help():
    service = _make_service()

    questions = service.generate_structured_follow_up_questions(
        user_query="Hồ sơ xét tuyển gồm những gì?",
        answer="Hồ sơ xét tuyển gồm phiếu đăng ký, sơ yếu lý lịch và giấy tờ minh chứng.",
        language="vi",
        sources=["Huong dan tuyen sinh 2025"],
        attachments=[
            {
                "file_name": "Mau dang ky xet tuyen.pdf",
                "description": "Biểu mẫu đăng ký xét tuyển",
            }
        ],
    )

    assert any("tải xuống" in q.lower() for q in questions)
    assert any("hồ sơ nào bắt buộc" in q.lower() for q in questions)
    assert all(not q.lower().startswith("bạn muốn") for q in questions)
