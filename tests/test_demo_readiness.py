import importlib
import datetime as dt
import sys
import types


def _install_rag_import_stubs():
    stubs = {
        "src.services.embedding_service": ("EmbeddingService",),
        "src.services.postgres_database_service": ("PostgresDatabaseService",),
        "src.services.hybrid_retrieval_service": ("HybridRetrievalService",),
        "src.services.ingestion_service": ("IngestionService",),
        "src.services.pdf_processor": ("PDFProcessor",),
        "src.services.memory_service": ("ConversationMemoryService",),
        "src.services.attachment_service": ("AttachmentService",),
    }

    for module_name, class_names in stubs.items():
        if module_name in sys.modules:
            continue

        module = types.ModuleType(module_name)
        for class_name in class_names:
            setattr(module, class_name, type(class_name, (), {}))
        sys.modules[module_name] = module

    if "src.services.gemini_service" not in sys.modules:
        gemini_module = types.ModuleType("src.services.gemini_service")
        gemini_module.normalize_question = lambda query: query
        gemini_module.generate_response = lambda prompt=None, **kwargs: ""
        gemini_module.get_grounding_instruction = (
            lambda query, language="vi": ""
        )
        sys.modules["src.services.gemini_service"] = gemini_module

    if "sentence_transformers" not in sys.modules:
        stub = types.ModuleType("sentence_transformers")

        class _SentenceTransformer:  # pragma: no cover - test stub only
            pass

        class _CrossEncoder:  # pragma: no cover - test stub only
            pass

        stub.SentenceTransformer = _SentenceTransformer
        stub.CrossEncoder = _CrossEncoder
        sys.modules["sentence_transformers"] = stub

    sys.modules.pop("src.services.rag_service", None)


def _load_rag_module():
    _install_rag_import_stubs()
    return importlib.import_module("src.services.rag_service")


def test_chart_requests_do_not_return_placeholder_chart_data():
    rag_module = _load_rag_module()
    service = rag_module.RAGService.__new__(rag_module.RAGService)

    charts = service._detect_chart_request(
        "V\u1ebd bi\u1ec3u \u0111\u1ed3 \u0111i\u1ec3m chu\u1ea9n tuy\u1ec3n sinh c\u00e1c n\u0103m g\u1ea7n \u0111\u00e2y",
        "T\u00f4i \u0111\u00e3 t\u1ed5ng h\u1ee3p th\u00f4ng tin \u0111i\u1ec3m chu\u1ea9n theo t\u00e0i li\u1ec7u.",
    )

    assert charts == []


def test_async_source_references_include_document_metadata():
    async_rag_module = importlib.import_module("src.services.async_rag_service")
    service = async_rag_module.AsyncRAGService.__new__(
        async_rag_module.AsyncRAGService
    )

    refs = service._build_source_references(
        [
            {
                "chunk_id": "chunk-1",
                "source_file": "tuyen_sinh_2026.pdf",
                "page_number": 3,
                "heading_text": "Chi tieu",
                "content": "Chi tieu tuyen sinh nam 2026.",
                "rerank_score": 0.88,
                "document_year": 2026,
                "source_url": "https://example.com/tuyen-sinh-2026",
            }
        ]
    )

    assert len(refs) == 1
    assert refs[0]["document_year"] == 2026
    assert refs[0]["source_url"] == "https://example.com/tuyen-sinh-2026"
    assert "full_content" not in refs[0]


def test_admission_prompt_requires_score_table_formatting(monkeypatch):
    rag_module = _load_rag_module()
    monkeypatch.setattr(rag_module, "ADMISSION_ONLY_MODE", True)
    service = rag_module.RAGService.__new__(rag_module.RAGService)

    prompt = service.create_user_prompt(
        "So s\u00e1nh \u0111i\u1ec3m chu\u1ea9n n\u0103m 2024 v\u00e0 2025",
        "Nguon: thong bao diem chuan",
        language="vi",
    )

    assert (
        "B\u1eaeT BU\u1ed8C d\u00f9ng b\u1ea3ng Markdown" in prompt
    )
    assert (
        "N\u0103m | Ng\u00e0nh/M\u00e3 ng\u00e0nh | \u0110i\u1ec3m | "
        "Ph\u01b0\u01a1ng th\u1ee9c | Xu h\u01b0\u1edbng." in prompt
    )


def test_frontend_next_config_disables_production_browser_source_maps():
    with open("frontend/next.config.ts", "r", encoding="utf-8") as config_file:
        config_text = config_file.read()

    assert "productionBrowserSourceMaps: false" in config_text


def test_personnel_prompt_requires_doc_grounded_table_formatting():
    rag_module = _load_rag_module()
    service = rag_module.RAGService.__new__(rag_module.RAGService)

    prompt = service.create_user_prompt(
        "Hieu truong hien nay la ai",
        "Nguon: Co_cau_to_chuc_va_Nhan_su_T04_Cap_nhat.pdf",
        language="vi",
    )

    assert "HUONG DAN BAT BUOC CHO CAU HOI VE CAN BO / LANH DAO / CO CAU TO CHUC" in prompt
    assert "Khong suy dien cap bac" in prompt
    assert "Ho va ten | Chuc vu | Don vi | Ghi chu" in prompt


def test_implicit_admission_timeline_prompt_defaults_to_current_cycle():
    rag_module = _load_rag_module()
    service = rag_module.RAGService.__new__(rag_module.RAGService)

    prompt = service.create_user_prompt(
        "Tôi muốn biết mốc thời gian đăng ký và xác nhận nhập học",
        "Nguon: thong bao tuyen sinh",
        language="vi",
    )

    assert "MAC DINH THEO CHU KY TUYEN SINH HIEN TAI" in prompt
    assert f"nam {dt.datetime.now().year}" in prompt
    assert "Khong duoc trinh bay thong tin cua nam 2025 tro ve truoc" in prompt
