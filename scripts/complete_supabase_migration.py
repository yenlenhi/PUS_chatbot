"""Complete migration script: Create all tables + Import all data to Supabase"""

import psycopg2
import json
from pathlib import Path
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/full_migration_export")

print("🚀 Complete Database Migration to Supabase")
print("=" * 60)

conn = psycopg2.connect(SUPABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# ============================================
# STEP 1: Create all missing tables
# ============================================
print("\n📋 STEP 1: Creating missing tables...")

create_tables_sql = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create chunks table
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    page_number INTEGER,
    chunk_index INTEGER NOT NULL,
    heading_text TEXT,
    heading_level INTEGER,
    heading_number VARCHAR(50),
    parent_heading TEXT,
    is_sub_chunk BOOLEAN DEFAULT FALSE,
    sub_chunk_index INTEGER,
    total_sub_chunks INTEGER,
    chunk_type VARCHAR(50) DEFAULT 'content',
    word_count INTEGER,
    char_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create embeddings table with pgvector
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL UNIQUE,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
);

-- Create conversations table (conversation_id is NOT UNIQUE because one conversation can have multiple messages)
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    sources TEXT,
    confidence FLOAT,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create BM25 index table
CREATE TABLE IF NOT EXISTS bm25_index (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL UNIQUE,
    bm25_vector TSVECTOR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
);

-- Create conversation_memory table
CREATE TABLE IF NOT EXISTS conversation_memory (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

-- Create document_attachments table
CREATE TABLE IF NOT EXISTS document_attachments (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR(255) NOT NULL UNIQUE,
    file_type VARCHAR(50),
    file_size INTEGER,
    page_count INTEGER,
    attachment_data BYTEA,
    preview_data BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chunk_attachments table
CREATE TABLE IF NOT EXISTS chunk_attachments (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL,
    attachment_type VARCHAR(50) NOT NULL,
    attachment_data BYTEA,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
);

-- Create document_history table
CREATE TABLE IF NOT EXISTS document_history (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chunk_performance table
CREATE TABLE IF NOT EXISTS chunk_performance (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL,
    query_text TEXT,
    was_retrieved BOOLEAN DEFAULT FALSE,
    was_helpful BOOLEAN,
    retrieval_rank INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
);

-- Create query_document_coverage table
CREATE TABLE IF NOT EXISTS query_document_coverage (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    documents_retrieved TEXT,
    total_documents INTEGER,
    coverage_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create query_metrics table
CREATE TABLE IF NOT EXISTS query_metrics (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    response_time FLOAT,
    chunks_retrieved INTEGER,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255),
    rating INTEGER,
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create token_usage table
CREATE TABLE IF NOT EXISTS token_usage (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255),
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    model VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create access_logs table
CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    user_ip VARCHAR(50),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    response_status INTEGER,
    response_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_ip VARCHAR(50),
    user_agent TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

-- Create topic_classifications table
CREATE TABLE IF NOT EXISTS topic_classifications (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    topic VARCHAR(100),
    subtopic VARCHAR(100),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create unanswered_queries table
CREATE TABLE IF NOT EXISTS unanswered_queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    reason VARCHAR(255),
    suggested_sources TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create memory_summaries table
CREATE TABLE IF NOT EXISTS memory_summaries (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    message_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);
"""

# Execute each statement separately
statements = [
    s.strip()
    for s in create_tables_sql.split(";")
    if s.strip() and not s.strip().startswith("--")
]
for stmt in statements:
    try:
        cur.execute(stmt)
        print(f"  ✅ Executed: {stmt[:50]}...")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"  ⏭️  Already exists: {stmt[:40]}...")
        else:
            print(f"  ⚠️  Warning: {str(e)[:60]}")

# Verify tables
cur.execute(
    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
)
tables = [r[0] for r in cur.fetchall()]
print(f"\n  📊 Total tables: {len(tables)}")

# ============================================
# STEP 2: Clear existing data
# ============================================
print("\n🗑️  STEP 2: Clearing existing data...")

# Delete in reverse order (respecting FK constraints)
tables_to_clear = [
    "memory_summaries",
    "unanswered_queries",
    "topic_classifications",
    "user_sessions",
    "access_logs",
    "token_usage",
    "feedback",
    "query_metrics",
    "query_document_coverage",
    "chunk_performance",
    "document_history",
    "chunk_attachments",
    "document_attachments",
    "conversation_memory",
    "bm25_index",
    "embeddings",
    "conversations",
    "chunks",
]

for table in tables_to_clear:
    try:
        cur.execute(f"DELETE FROM {table}")
        print(f"  ✅ Cleared {table}")
    except Exception as e:
        print(f"  ⏭️  Skipped {table}: {str(e)[:40]}")

# ============================================
# STEP 3: Import all data
# ============================================
print("\n📦 STEP 3: Importing data from export files...")

# Import order (respecting foreign keys)
import_order = [
    "chunks",
    "embeddings",
    "bm25_index",
    "conversations",
    "conversation_memory",
    "document_attachments",
    "chunk_attachments",
    "document_history",
    "chunk_performance",
    "query_document_coverage",
    "query_metrics",
    "feedback",
    "token_usage",
    "access_logs",
    "user_sessions",
    "topic_classifications",
    "unanswered_queries",
    "memory_summaries",
]

results = {}
start_time = time.time()

for table_name in import_order:
    file_path = EXPORT_DIR / f"{table_name}.json"
    if not file_path.exists():
        print(f"  ⏭️  Skipping {table_name} (file not found)")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print(f"  ⏭️  Skipping {table_name} (empty data)")
        results[table_name] = 0
        continue

    print(f"\n  📥 Importing {table_name} ({len(data)} records)...")

    imported = 0
    skipped = 0

    try:
        columns = list(data[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        column_str = ", ".join(columns)

        # Special handling for embeddings
        if table_name == "embeddings" and "embedding" in columns:
            for i, row in enumerate(data):
                if i % 200 == 0 and i > 0:
                    print(f"    ✓ {i}/{len(data)}")

                emb_list = row["embedding"]
                if len(emb_list) != 384:
                    skipped += 1
                    continue

                try:
                    emb_str = "[" + ",".join(str(x) for x in emb_list) + "]"
                    cur.execute(
                        """
                        INSERT INTO embeddings (id, chunk_id, embedding, created_at)
                        VALUES (%s, %s, %s::vector(384), %s)
                    """,
                        (row["id"], row["chunk_id"], emb_str, row["created_at"]),
                    )
                    imported += 1
                except Exception as e:
                    if "duplicate" not in str(e).lower():
                        skipped += 1
        else:
            # Regular import
            for i, row in enumerate(data):
                if i % 500 == 0 and i > 0:
                    print(f"    ✓ {i}/{len(data)}")

                try:
                    values = [row.get(col) for col in columns]
                    sql = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
                    cur.execute(sql, values)
                    imported += 1
                except Exception as e:
                    if "duplicate" not in str(e).lower():
                        skipped += 1
                        if skipped <= 2:
                            print(f"    ⚠️  Error: {str(e)[:80]}")

        print(
            f"    ✅ Imported {imported} records"
            + (f" ({skipped} skipped)" if skipped > 0 else "")
        )
        results[table_name] = imported

        # Update sequence
        if "id" in columns:
            try:
                cur.execute(
                    f"SELECT setval('{table_name}_id_seq', (SELECT COALESCE(MAX(id), 0) FROM {table_name}), true)"
                )
            except:
                pass

    except Exception as e:
        print(f"    ❌ Error: {str(e)[:100]}")
        results[table_name] = f"ERROR: {str(e)[:50]}"

# ============================================
# STEP 4: Final verification
# ============================================
print("\n" + "=" * 60)
print("📊 FINAL VERIFICATION:")
print("=" * 60)

cur.execute(
    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
)
tables = [r[0] for r in cur.fetchall()]

total_records = 0
for table in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        total_records += count
        print(f"  ✅ {table}: {count} records")
    except:
        print(f"  ⚠️  {table}: could not count")

print("=" * 60)
print(f"📈 Total: {len(tables)} tables, {total_records} records")
print(f"⏱️  Completed in {time.time() - start_time:.1f} seconds")
print("=" * 60)

conn.close()
print("\n✅ Migration completed!")
