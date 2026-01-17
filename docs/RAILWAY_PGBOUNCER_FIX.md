# Railway PGBouncer Compatibility Fix

## Vấn đề
Khi deploy trên Railway, hệ thống gặp lỗi:
```
DuplicatePreparedStatementError: prepared statement "__asyncpg_stmt_b__" already exists
```

## Nguyên nhân
Railway sử dụng **PGBouncer** cho connection pooling với `pool_mode` được đặt là `"transaction"` hoặc `"statement"`. Các pool mode này **KHÔNG hỗ trợ prepared statements** của asyncpg/SQLAlchemy đúng cách.

## Giải pháp đã áp dụng

### 1. Disable Prepared Statements trong Engine
Trong file `src/services/async_postgres_database_service.py`:

```python
self.engine = create_async_engine(
    self.database_url,
    echo=False,
    poolclass=NullPool,  # Use NullPool for pgbouncer compatibility
    connect_args={
        "statement_cache_size": 0,  # Disable statement cache
        "prepared_statement_cache_size": 0,  # Disable prepared statement cache
    },
    # Disable SQLAlchemy's use of prepared statements
    execution_options={
        "compiled_cache": None,
    },
)
```

### 2. Disable Compiled Cache cho từng query
Thêm `execution_options(compiled_cache=None)` cho tất cả các câu lệnh SQL:

```python
await conn.execute(
    text("SELECT 1").execution_options(compiled_cache=None)
)
```

### 3. Gộp DDL Statements
Thay vì thực thi nhiều câu lệnh CREATE TABLE/INDEX riêng lẻ, gộp chúng thành một script duy nhất:

```python
ddl_script = """
    CREATE TABLE IF NOT EXISTS chunks (...);
    CREATE TABLE IF NOT EXISTS embeddings (...);
    CREATE INDEX IF NOT EXISTS idx_chunks_source_file ON chunks(source_file);
    ...
"""

await conn.execute(text(ddl_script).execution_options(compiled_cache=None))
```

## Tài liệu tham khảo
- [asyncpg PGBouncer documentation](https://magicstack.github.io/asyncpg/current/faq.html#pgbouncer)
- [SQLAlchemy asyncpg dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.asyncpg)
- [Railway PGBouncer configuration](https://docs.railway.app/databases/postgresql)

## Kiểm tra
Sau khi deploy, kiểm tra logs để đảm bảo không còn lỗi `DuplicatePreparedStatementError`.

✅ Database initialization phải thành công  
✅ Các bảng và index được tạo thành công  
✅ Không có warning về pgbouncer  

## Ngày cập nhật
2026-01-17
