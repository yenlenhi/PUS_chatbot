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
from src.models.schemas import DocumentChunk


def _build_gemini_service() -> GeminiPDFService:
    service = GeminiPDFService.__new__(GeminiPDFService)
    GeminiPDFService._global_next_request_at = 0.0
    GeminiPDFService._global_cooldown_until = 0.0
    service.auth_configs = []
    service.max_retries = 2
    service.retry_delay = 0
    service.page_delay = 0
    service.min_request_interval = 0
    service.rate_limit_cooldown = 0
    service.max_backoff_seconds = 60
    service.request_timeout = 1
    service.max_output_tokens = 8192
    service.render_scale = 3.0
    service.had_rate_limit_errors = False
    service.rate_limited_pages = set()
    return service


def test_extract_text_from_image_uses_image_first_json_mode(monkeypatch):
    service = _build_gemini_service()
    captured = {}

    def fake_invoke(image_base64, page_num):
        captured["image_base64"] = image_base64
        captured["page_num"] = page_num
        return {
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
        }

    monkeypatch.setattr(service, "_invoke_ocr_model", fake_invoke)

    extracted_text = service._extract_text_from_image("ZmFrZV9pbWFnZQ==", 1)

    assert extracted_text == "Trang 1\nNoi dung OCR"
    assert captured["image_base64"] == "ZmFrZV9pbWFnZQ=="
    assert captured["page_num"] == 1
    assert service.render_scale >= 1.0

    payload = service._build_ocr_request("ZmFrZV9pbWFnZQ==")
    parts = payload["contents"][0]["parts"]
    assert "inline_data" in parts[0]
    assert parts[0]["inline_data"]["data"] == "ZmFrZV9pbWFnZQ=="
    assert parts[1]["text"].startswith(
        "Extract every visible character from this Vietnamese administrative/legal PDF page image."
    )
    assert "GitHub-flavored Markdown table format" in parts[1]["text"]
    assert "articles (Dieu), clauses (Khoan), points (Diem)" in parts[1]["text"]
    assert "Keep quoted passages intact" in parts[1]["text"]
    assert payload["generationConfig"]["responseMimeType"] == "application/json"


def test_extract_text_from_image_retries_transient_errors(monkeypatch):
    service = _build_gemini_service()
    responses = iter(
        [
            RuntimeError("503 temporarily unavailable"),
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
        ]
    )
    call_count = {"value": 0}

    def fake_invoke(image_base64, page_num):
        call_count["value"] += 1
        result = next(responses)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(service, "_invoke_ocr_model", fake_invoke)

    extracted_text = service._extract_text_from_image("ZmFrZQ==", 2)

    assert extracted_text == "Du lieu OCR sau retry"
    assert call_count["value"] == 2


def test_extract_text_from_image_429_respects_cooldown_without_extra_final_sleep(
    monkeypatch,
):
    service = _build_gemini_service()
    service.max_retries = 2
    service.rate_limit_cooldown = 7
    responses = iter([RuntimeError("429 rate limit"), RuntimeError("429 rate limit")])
    sleep_calls = []

    def fake_invoke(image_base64, page_num):
        raise next(responses)

    monkeypatch.setattr(service, "_invoke_ocr_model", fake_invoke)
    monkeypatch.setattr(
        "src.services.gemini_pdf_service.time.sleep",
        lambda seconds: sleep_calls.append(seconds),
    )

    extracted_text = service._extract_text_from_image("ZmFrZQ==", 9)

    assert extracted_text is None
    assert service.had_rate_limit_errors is True
    assert service.rate_limited_pages == {9}
    assert len(sleep_calls) == 1
    assert 6.9 <= sleep_calls[0] <= 7


def test_parse_text_payload_salvages_truncated_json_payload():
    service = _build_gemini_service()

    payload = (
        '{"has_text":true,"text":"5\\n\\nNoi dung trang dang bi cat giua chung'
    )

    extracted_text = service._parse_text_payload(payload)

    assert extracted_text == "5\n\nNoi dung trang dang bi cat giua chung"


def test_extract_text_from_response_handles_split_json_parts_without_storing_raw_json():
    service = _build_gemini_service()

    result = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": '{"has_text": true, "text": "Dong 1\\n'},
                        {"text": 'Dong 2"}'},
                    ]
                }
            }
        ]
    }

    extracted_text = service._extract_text_from_response(result, 1)

    assert extracted_text == "Dong 1\nDong 2"


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


def test_pdf_processor_normalize_page_text_reflows_broken_lines():
    processor = PDFProcessor.__new__(PDFProcessor)

    raw_text = (
        "1.4. Lich trinh to chuc tuyen sinh\n"
        "\n"
        "Cong an cac don vi, dia phuong co tuyen CAND to chuc xet tuyen\n"
        "dam bao thoi gian, ke hoach theo lich trinh chung cua Bo Cong an.\n"
    )

    normalized = processor._normalize_page_text(raw_text)

    assert "1.4. Lich trinh to chuc tuyen sinh" in normalized
    assert (
        "Cong an cac don vi, dia phuong co tuyen CAND to chuc xet tuyen dam bao thoi gian, "
        "ke hoach theo lich trinh chung cua Bo Cong an."
    ) in normalized


def test_pdf_processor_normalize_page_text_preserves_markdown_tables():
    processor = PDFProcessor.__new__(PDFProcessor)

    raw_text = (
        "Bang diem tham khao\n"
        "| Ma to hop | Diem |\n"
        "| --- | --- |\n"
        "| CA1 | 18.25 |\n"
        "| CA2 | 19.00 |\n"
        "Ghi chu bo sung\n"
    )

    normalized = processor._normalize_page_text(raw_text)

    assert "| Ma to hop | Diem |" in normalized
    assert "| --- | --- |" in normalized
    assert "| CA1 | 18.25 |" in normalized
    assert "| CA2 | 19.00 |" in normalized
    assert "Bang diem tham khao" in normalized
    assert "Ghi chu bo sung" in normalized
    assert "| CA1 | 18.25 | | CA2 | 19.00 |" not in normalized


def test_pdf_processor_extract_text_from_pdf_uses_gemini_for_all_pages():
    processor = PDFProcessor.__new__(PDFProcessor)
    processor.extraction_mode = "gemini_only"
    processor.use_gemini = True
    processor._get_page_count = lambda pdf_path: 3

    class _FakeGeminiService:
        def __init__(self):
            self.calls = []

        def extract_text_from_pdf(self, pdf_path, page_numbers=None):
            self.calls.append(page_numbers)
            if page_numbers is None:
                return [(1, "Trang 1"), (3, "Trang 3")]
            return [(2, "Trang 2 bang du lieu")]

    fake_service = _FakeGeminiService()
    processor.gemini_service = fake_service

    pages = processor.extract_text_from_pdf(Path("test.pdf"))

    assert pages == [(1, "Trang 1"), (2, "Trang 2 bang du lieu"), (3, "Trang 3")]
    assert fake_service.calls == [None, [2]]


def test_pdf_processor_skips_missing_page_retry_when_initial_pass_hits_rate_limit():
    processor = PDFProcessor.__new__(PDFProcessor)
    processor.extraction_mode = "gemini_only"
    processor.use_gemini = True
    processor._get_page_count = lambda pdf_path: 3

    class _FakeGeminiService:
        def __init__(self):
            self.calls = []
            self.had_rate_limit_errors = True

        def extract_text_from_pdf(self, pdf_path, page_numbers=None):
            self.calls.append(page_numbers)
            return [(1, "Trang 1")]

    fake_service = _FakeGeminiService()
    processor.gemini_service = fake_service

    pages = processor.extract_text_from_pdf(Path("test.pdf"))

    assert pages == [(1, "Trang 1")]
    assert fake_service.calls == [None]


def test_process_pdf_with_headings_reindexes_chunks_across_pages():
    processor = PDFProcessor.__new__(PDFProcessor)

    class _FakeHeadingChunker:
        def chunk_by_headings(self, text, source_file, page_number=None):
            assert page_number is None
            assert "Page 1 content" in text
            assert "Page 2 content" in text
            return [
                DocumentChunk(
                    content="Page 1 content",
                    source_file=source_file,
                    page_number=None,
                    chunk_index=0,
                ),
                DocumentChunk(
                    content="Page 2 content",
                    source_file=source_file,
                    page_number=None,
                    chunk_index=1,
                )
            ]

    processor.heading_chunker = _FakeHeadingChunker()
    processor.extract_text_from_pdf = lambda pdf_path: [
        (1, "Page 1 content"),
        (2, "Page 2 content"),
    ]

    chunks = processor.process_pdf_with_headings(Path("test.pdf"))

    assert [chunk.chunk_index for chunk in chunks] == [0, 1]
    assert [chunk.page_number for chunk in chunks] == [1, 2]
