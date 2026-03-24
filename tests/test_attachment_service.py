import sys
import types


if "sqlalchemy" not in sys.modules:
    sqlalchemy_stub = types.ModuleType("sqlalchemy")
    sqlalchemy_stub.text = lambda query: query
    sys.modules["sqlalchemy"] = sqlalchemy_stub

if "src.services.postgres_database_service" not in sys.modules:
    postgres_stub = types.ModuleType("src.services.postgres_database_service")
    postgres_stub.PostgresDatabaseService = type("PostgresDatabaseService", (), {})
    sys.modules["src.services.postgres_database_service"] = postgres_stub

if "src.services.supabase_storage_service" not in sys.modules:
    supabase_stub = types.ModuleType("src.services.supabase_storage_service")
    supabase_stub.get_supabase_storage_service = lambda: types.SimpleNamespace(
        get_public_url=lambda path: f"https://files.example/{path}"
    )
    sys.modules["src.services.supabase_storage_service"] = supabase_stub

from src.services.attachment_service import AttachmentService


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return list(self._rows)

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def __iter__(self):
        return iter(self._rows)


class _FakeConnection:
    def __init__(self):
        self.executed_queries = []
        self.commit_called = False

    def execute(self, statement, params=None):
        query = str(statement)
        self.executed_queries.append(query)

        if "information_schema.columns" in query:
            return _FakeResult(
                [("chunk_id",), ("document_attachment_id",), ("relevance_score",)]
            )

        if "FROM document_attachments a" in query:
            return _FakeResult(
                [
                    (
                        7,
                        "mau-don.pdf",
                        "application/pdf",
                        "forms/mau-don.pdf",
                        12345,
                        "Mau don dang ky",
                        ["tuyen sinh"],
                        "Tuyen sinh",
                    )
                ]
            )

        if "INSERT INTO chunk_attachments" in query:
            return _FakeResult([])

        raise AssertionError(f"Unexpected query: {query}")

    def commit(self):
        self.commit_called = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_get_attachments_by_chunk_ids_supports_legacy_attachment_fk_column():
    connection = _FakeConnection()
    service = AttachmentService.__new__(AttachmentService)
    service.db = types.SimpleNamespace(
        engine=types.SimpleNamespace(connect=lambda: connection)
    )
    service.supabase = types.SimpleNamespace(
        get_public_url=lambda path: f"https://files.example/{path}"
    )
    service._chunk_attachment_fk_column = None
    service._chunk_attachment_fk_column_checked = False

    attachments = service.get_attachments_by_chunk_ids([101, 102], limit=1)

    assert len(attachments) == 1
    assert attachments[0].id == 7
    assert attachments[0].download_url == "/api/v1/attachments/download/7"
    assert attachments[0].public_url == "https://files.example/forms/mau-don.pdf"
    assert any(
        "ca.document_attachment_id" in query
        for query in connection.executed_queries
        if "FROM document_attachments a" in query
    )


def test_link_attachment_to_chunks_supports_legacy_attachment_fk_column():
    connection = _FakeConnection()
    service = AttachmentService.__new__(AttachmentService)
    service.db = types.SimpleNamespace(
        engine=types.SimpleNamespace(connect=lambda: connection)
    )
    service.supabase = types.SimpleNamespace(
        get_public_url=lambda path: f"https://files.example/{path}"
    )
    service._chunk_attachment_fk_column = None
    service._chunk_attachment_fk_column_checked = False

    service.link_attachment_to_chunks(attachment_id=7, chunk_ids=[101, 102])

    assert connection.commit_called is True
    insert_queries = [
        query
        for query in connection.executed_queries
        if "INSERT INTO chunk_attachments" in query
    ]
    assert len(insert_queries) == 2
    assert all("document_attachment_id" in query for query in insert_queries)
