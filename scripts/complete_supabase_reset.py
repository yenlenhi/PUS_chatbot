"""
Complete Supabase Reset and Import
- Drop all existing tables
- Create fresh schema with all tables
- Import all data from export files
"""

import psycopg2
import json
from pathlib import Path
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("=" * 60)
print("🚀 COMPLETE SUPABASE RESET AND IMPORT")
print("=" * 60)

conn = psycopg2.connect(SUPABASE_URL)
conn.autocommit = True
cur = conn.cursor()

# ============================================
# STEP 1: DROP ALL TABLES
# ============================================
print("\n🗑️ STEP 1: Dropping all existing tables...")

tables_to_drop = [
    "access_logs",
    "bm25_index",
    "chunk_attachments",
    "chunk_performance",
    "conversation_memory",
    "document_attachments",
    "document_history",
    "feedback",
    "memory_summaries",
    "query_document_coverage",
    "query_metrics",
    "token_usage",
    "topic_classifications",
    "unanswered_queries",
    "user_sessions",
    "embeddings",  # Must be after chunk_attachments due to FK
    "conversations",
    "chunks",  # Must be last due to FK dependencies
]

for table in tables_to_drop:
    try:
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        print(f"  ✓ Dropped {table}")
    except Exception as e:
        print(f"  ⚠️ {table}: {e}")

# Also drop views
views_to_drop = ["chunk_statistics", "embedding_statistics"]
for view in views_to_drop:
    try:
        cur.execute(f"DROP VIEW IF EXISTS {view} CASCADE")
    except:
        pass

print("✅ All tables dropped!")

# ============================================
# STEP 2: CREATE FRESH SCHEMA
# ============================================
print("\n📋 STEP 2: Creating fresh schema...")

# Enable pgvector
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
print("  ✓ pgvector extension enabled")

# Create chunks table
cur.execute(
    """
CREATE TABLE chunks (
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
)
"""
)
print("  ✓ chunks table created")

# Create embeddings table
cur.execute(
    """
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL UNIQUE,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
)
"""
)
print("  ✓ embeddings table created")

# Create conversations table
cur.execute(
    """
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    sources TEXT,
    confidence FLOAT,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ conversations table created")

# Create bm25_index table
cur.execute(
    """
CREATE TABLE bm25_index (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL UNIQUE,
    bm25_vector TSVECTOR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
)
"""
)
print("  ✓ bm25_index table created")

# Create additional tables
cur.execute(
    """
CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time FLOAT,
    user_agent TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ access_logs table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS chunk_performance (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER,
    query TEXT,
    relevance_score FLOAT,
    was_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ chunk_performance table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS conversation_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    role VARCHAR(50),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ conversation_memory table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS document_attachments (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    file_path TEXT,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ document_attachments table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS document_history (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(255),
    action VARCHAR(50),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ document_history table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255),
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ feedback table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS memory_summaries (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ memory_summaries table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS query_document_coverage (
    id SERIAL PRIMARY KEY,
    query TEXT,
    documents_used TEXT,
    coverage_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ query_document_coverage table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS query_metrics (
    id SERIAL PRIMARY KEY,
    query TEXT,
    response_time FLOAT,
    chunks_retrieved INTEGER,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ query_metrics table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS token_usage (
    id SERIAL PRIMARY KEY,
    model VARCHAR(100),
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ token_usage table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS topic_classifications (
    id SERIAL PRIMARY KEY,
    query TEXT,
    topic VARCHAR(255),
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ topic_classifications table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS unanswered_queries (
    id SERIAL PRIMARY KEY,
    query TEXT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ unanswered_queries table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    user_agent TEXT,
    ip_address VARCHAR(50),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ user_sessions table created")

cur.execute(
    """
CREATE TABLE IF NOT EXISTS chunk_attachments (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER,
    attachment_type VARCHAR(50),
    attachment_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)
print("  ✓ chunk_attachments table created")

# Create indexes
print("\n  Creating indexes...")
cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_file)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at)")
cur.execute(
    "CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id)"
)
cur.execute(
    "CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id)"
)
cur.execute(
    "CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at)"
)
cur.execute("CREATE INDEX IF NOT EXISTS idx_bm25_chunk_id ON bm25_index(chunk_id)")
print("  ✓ Indexes created")

print("✅ Schema created successfully!")

# ============================================
# STEP 3: IMPORT DATA
# ============================================
print("\n📦 STEP 3: Importing data...")
start_time = time.time()

# Disable autocommit for batch import
conn.autocommit = False

# Import chunks
print("\n  Importing chunks...")
with open(EXPORT_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

batch_count = 0
for i, chunk in enumerate(chunks):
    cur.execute(
        """
        INSERT INTO chunks (
            id, content, source_file, page_number, chunk_index,
            heading_text, heading_level, heading_number, parent_heading,
            is_sub_chunk, sub_chunk_index, total_sub_chunks, chunk_type,
            word_count, char_count, created_at, updated_at
        ) VALUES (
            %(id)s, %(content)s, %(source_file)s, %(page_number)s, %(chunk_index)s,
            %(heading_text)s, %(heading_level)s, %(heading_number)s, %(parent_heading)s,
            %(is_sub_chunk)s, %(sub_chunk_index)s, %(total_sub_chunks)s, %(chunk_type)s,
            %(word_count)s, %(char_count)s, %(created_at)s, %(updated_at)s
        )
    """,
        chunk,
    )

    batch_count += 1
    if batch_count >= 100:
        conn.commit()
        batch_count = 0
        if i % 500 == 0:
            print(f"    ✓ {i}/{len(chunks)} chunks")

conn.commit()
cur.execute(
    "SELECT setval('chunks_id_seq', (SELECT COALESCE(MAX(id), 0) FROM chunks), true)"
)
conn.commit()
print(f"  ✅ Imported {len(chunks)} chunks")

# Import embeddings
print("\n  Importing embeddings...")
with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

imported = 0
skipped = 0

for i, emb in enumerate(embeddings):
    emb_list = emb["embedding"]

    # Only import 384-dim embeddings
    if len(emb_list) != 384:
        skipped += 1
        continue

    try:
        cur.execute(
            """
            INSERT INTO embeddings (id, chunk_id, embedding, created_at)
            VALUES (%s, %s, %s::vector(384), %s)
        """,
            (emb["id"], emb["chunk_id"], str(emb_list), emb["created_at"]),
        )
        imported += 1

        if imported % 100 == 0:
            conn.commit()
            if imported % 500 == 0:
                print(f"    ✓ {imported} embeddings imported")
    except Exception:
        skipped += 1
        conn.rollback()

conn.commit()
cur.execute(
    "SELECT setval('embeddings_id_seq', (SELECT COALESCE(MAX(id), 0) FROM embeddings), true)"
)
conn.commit()
print(f"  ✅ Imported {imported} embeddings ({skipped} skipped - wrong dimension)")

# Import conversations
print("\n  Importing conversations...")
with open(EXPORT_DIR / "conversations.json", "r", encoding="utf-8") as f:
    conversations = json.load(f)

for conv in conversations:
    cur.execute(
        """
        INSERT INTO conversations (
            id, conversation_id, user_message, assistant_response,
            sources, confidence, processing_time, created_at
        ) VALUES (
            %(id)s, %(conversation_id)s, %(user_message)s, %(assistant_response)s,
            %(sources)s, %(confidence)s, %(processing_time)s, %(created_at)s
        )
    """,
        conv,
    )

conn.commit()
cur.execute(
    "SELECT setval('conversations_id_seq', (SELECT COALESCE(MAX(id), 0) FROM conversations), true)"
)
conn.commit()
print(f"  ✅ Imported {len(conversations)} conversations")

# ============================================
# STEP 4: VERIFICATION
# ============================================
print("\n" + "=" * 60)
print("📊 VERIFICATION")
print("=" * 60)

cur.execute("SELECT COUNT(*) FROM chunks")
chunks_count = cur.fetchone()[0]
print(f"  ✅ Chunks: {chunks_count}")

cur.execute("SELECT COUNT(*) FROM embeddings")
emb_count = cur.fetchone()[0]
print(f"  ✅ Embeddings: {emb_count}")

cur.execute("SELECT COUNT(*) FROM conversations")
conv_count = cur.fetchone()[0]
print(f"  ✅ Conversations: {conv_count}")

if chunks_count > 0 and emb_count > 0:
    coverage = (emb_count / chunks_count) * 100
    print(f"  📈 Embedding Coverage: {coverage:.1f}%")

# List all tables
cur.execute(
    """
    SELECT tablename FROM pg_tables 
    WHERE schemaname = 'public' 
    ORDER BY tablename
"""
)
tables = cur.fetchall()
print(f"\n  📋 Total tables created: {len(tables)}")
for t in tables:
    print(f"    - {t[0]}")

cur.close()
conn.close()

elapsed = time.time() - start_time
print("\n" + "=" * 60)
print(f"✅ COMPLETE! Total time: {elapsed:.1f} seconds")
print("🎉 Supabase database is ready!")
print("=" * 60)
