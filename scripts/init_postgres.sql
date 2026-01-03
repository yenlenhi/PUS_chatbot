-- Initialize PostgreSQL database schema for Uni Bot
-- This script is automatically run when the container starts

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
    embedding vector(384),  -- Vietnamese embedding v1 uses 384 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
);

-- Create conversations table for storing chat history
-- Note: conversation_id is NOT UNIQUE because a single conversation can have multiple messages
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    sources TEXT,  -- JSON array of sources
    confidence FLOAT,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create BM25 index table for sparse retrieval
CREATE TABLE IF NOT EXISTS bm25_index (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL UNIQUE,
    bm25_vector TSVECTOR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_file);
CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at);
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_bm25_chunk_id ON bm25_index(chunk_id);

-- Create vector index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create HNSW index as alternative (faster for large datasets)
-- Uncomment if you want to use HNSW instead of IVFFlat
-- CREATE INDEX IF NOT EXISTS idx_embeddings_vector_hnsw ON embeddings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Create full-text search index for BM25
CREATE INDEX IF NOT EXISTS idx_bm25_vector ON bm25_index USING gin(bm25_vector);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for chunks table
CREATE TRIGGER update_chunks_updated_at BEFORE UPDATE ON chunks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for chunk statistics
CREATE OR REPLACE VIEW chunk_statistics AS
SELECT 
    source_file,
    COUNT(*) as total_chunks,
    SUM(word_count) as total_words,
    SUM(char_count) as total_chars,
    COUNT(DISTINCT heading_text) as unique_headings,
    MIN(created_at) as first_created,
    MAX(created_at) as last_created
FROM chunks
GROUP BY source_file;

-- Create view for embedding statistics
CREATE OR REPLACE VIEW embedding_statistics AS
SELECT 
    COUNT(*) as total_embeddings,
    COUNT(DISTINCT chunk_id) as unique_chunks,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM chunks) as embedding_coverage_percent
FROM embeddings;

