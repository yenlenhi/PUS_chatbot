import sys
import types
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


try:
    import PyPDF2  # noqa: F401
except ModuleNotFoundError:
    pypdf2_stub = types.ModuleType("PyPDF2")
    pypdf2_stub.PdfReader = object
    sys.modules["PyPDF2"] = pypdf2_stub

try:
    import pdfplumber  # noqa: F401
except ModuleNotFoundError:
    pdfplumber_stub = types.ModuleType("pdfplumber")
    pdfplumber_stub.open = lambda *args, **kwargs: None
    sys.modules["pdfplumber"] = pdfplumber_stub

try:
    import pymupdf  # noqa: F401
except ModuleNotFoundError:
    pymupdf_stub = types.ModuleType("pymupdf")
    pymupdf_stub.open = lambda *args, **kwargs: None
    pymupdf_stub.Matrix = lambda x, y: (x, y)
    sys.modules["pymupdf"] = pymupdf_stub

try:
    import PIL  # noqa: F401
except ModuleNotFoundError:
    pil_package = types.ModuleType("PIL")
    image_module = types.ModuleType("PIL.Image")
    image_module.Image = type("Image", (), {})
    image_filter_module = types.ModuleType("PIL.ImageFilter")
    image_filter_module.SHARPEN = "SHARPEN"
    image_ops_module = types.ModuleType("PIL.ImageOps")
    image_ops_module.exif_transpose = lambda image: image
    image_ops_module.grayscale = lambda image: image
    image_ops_module.autocontrast = lambda image: image

    pil_package.Image = image_module
    pil_package.ImageFilter = image_filter_module
    pil_package.ImageOps = image_ops_module

    sys.modules["PIL"] = pil_package
    sys.modules["PIL.Image"] = image_module
    sys.modules["PIL.ImageFilter"] = image_filter_module
    sys.modules["PIL.ImageOps"] = image_ops_module


from src.services.gemini_pdf_service import GeminiPDFService
from src.services.pdf_processor import PDFProcessor


class _FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def _build_gemini_service() -> GeminiPDFService:
    service = GeminiPDFService.__new__(GeminiPDFService)
    service.api_key = "test-key"
    service.api_url = "https://example.com/generateContent"
    service.max_retries = 2
    service.retry_delay = 0
    service.page_delay = 0
    service.request_timeout = 1
    service.max_output_tokens = 8192
    return service


def test_extract_text_from_image_uses_image_first_json_mode(monkeypatch):
    service = _build_gemini_service()
    captured_request = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured_request["url"] = url
        captured_request["headers"] = headers
        captured_request["json"] = json
        captured_request["timeout"] = timeout
        return _FakeResponse(
            200,
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": '{"has_text": true, "text": "Trang 1\\nNoi dung OCR"}'
                                }
                            ]
                        }
                    }
                ]
            },
        )

    monkeypatch.setattr("src.services.gemini_pdf_service.requests.post", fake_post)

    extracted_text = service._extract_text_from_image("ZmFrZV9pbWFnZQ==", 1)

    assert extracted_text == "Trang 1\nNoi dung OCR"
    assert captured_request["headers"] == {"Content-Type": "application/json"}
    assert captured_request["timeout"] == 1

    parts = captured_request["json"]["contents"][0]["parts"]
    assert "inline_data" in parts[0]
    assert parts[0]["inline_data"]["data"] == "ZmFrZV9pbWFnZQ=="
    assert parts[1]["text"].startswith("Extract all visible text")
    assert (
        captured_request["json"]["generationConfig"]["responseMimeType"]
        == "application/json"
    )


def test_extract_text_from_image_retries_transient_errors(monkeypatch):
    service = _build_gemini_service()
    responses = iter(
        [
            _FakeResponse(503, text="temporarily unavailable"),
            _FakeResponse(
                200,
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "text": '{"has_text": true, "text": "Du lieu OCR sau retry"}'
                                    }
                                ]
                            }
                        }
                    ]
                },
            ),
        ]
    )
    call_count = {"value": 0}

    def fake_post(url, headers=None, json=None, timeout=None):
        call_count["value"] += 1
        return next(responses)

    monkeypatch.setattr("src.services.gemini_pdf_service.requests.post", fake_post)

    extracted_text = service._extract_text_from_image("ZmFrZQ==", 2)

    assert extracted_text == "Du lieu OCR sau retry"
    assert call_count["value"] == 2


def test_pdf_processor_flags_garbage_native_text_for_ocr():
    processor = PDFProcessor.__new__(PDFProcessor)

    assert processor._looks_like_extraction_garbage("cid:123 cid:456 cid:789")
    assert processor._looks_like_extraction_garbage("a b c d e f g h i")
    assert not processor._looks_like_extraction_garbage(
        "Thong bao tuyen sinh dai hoc he chinh quy nam 2026"
    )
    assert not processor._has_meaningful_text("a b c d e f g h i")
    assert processor._has_meaningful_text(
        "Thong bao tuyen sinh dai hoc he chinh quy nam 2026"
    )


def test_pdf_processor_prefers_clean_ocr_result_over_garbage_native_text():
    processor = PDFProcessor.__new__(PDFProcessor)

    merged_pages = processor._merge_page_results(
        {1: "cid:123 cid:456 cid:789 cid:321"},
        {1: "Thong bao tuyen sinh dai hoc he chinh quy nam 2026"},
    )

    assert merged_pages[1] == "Thong bao tuyen sinh dai hoc he chinh quy nam 2026"
