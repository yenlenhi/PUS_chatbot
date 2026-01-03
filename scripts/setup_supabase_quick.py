"""Quick Supabase setup"""

from sqlalchemy import create_engine, text

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"

engine = create_engine(SUPABASE_URL)
conn = engine.connect()

print("🔧 Creating tables...")

# Create chunks table
conn.execute(
    text(
        """
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
)
"""
    )
)
conn.commit()
print("✅ chunks table created")

# Create embeddings table
conn.execute(
    text(
        """
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL UNIQUE,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
)
"""
    )
)
conn.commit()
print("✅ embeddings table created")

# Create conversations table
conn.execute(
    text(
        """
CREATE TABLE IF NOT EXISTS conversations (
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
)
conn.commit()
print("✅ conversations table created")

# Create bm25_index table
conn.execute(
    text(
        """
CREATE TABLE IF NOT EXISTS bm25_index (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL UNIQUE,
    bm25_vector TSVECTOR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
)
"""
    )
)
conn.commit()
print("✅ bm25_index table created")

# Create indexes
print("🔧 Creating indexes...")
conn.execute(
    text("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_file)")
)
conn.execute(
    text("CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id)")
)
conn.execute(
    text(
        "CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id)"
    )
)
conn.commit()
print("✅ Indexes created")

print("✅ Schema setup complete!")
conn.close()
