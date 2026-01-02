"""Simple import - one by one with progress"""

import json
from pathlib import Path
from sqlalchemy import create_engine, text
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🔄 Connecting to Supabase...")
engine = create_engine(SUPABASE_URL, pool_size=20)

start_time = time.time()

# Import chunks
print("📦 Importing chunks...")
with open(EXPORT_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

batch_size = 50
for i in range(0, len(chunks), batch_size):
    with engine.begin() as conn:
        for chunk in chunks[i : i + batch_size]:
            conn.execute(
                text(
                    """
                    INSERT INTO chunks (
                        id, content, source_file, page_number, chunk_index,
                        heading_text, heading_level, heading_number, parent_heading,
                        is_sub_chunk, sub_chunk_index, total_sub_chunks, chunk_type,
                        word_count, char_count, created_at, updated_at
                    ) VALUES (
                        :id, :content, :source_file, :page_number, :chunk_index,
                        :heading_text, :heading_level, :heading_number, :parent_heading,
                        :is_sub_chunk, :sub_chunk_index, :total_sub_chunks, :chunk_type,
                        :word_count, :char_count, :created_at, :updated_at
                    )
                    ON CONFLICT (id) DO NOTHING
                """
                ),
                chunk,
            )
    if (i + batch_size) % 200 == 0 or i + batch_size >= len(chunks):
        print(f"  ✓ {min(i+batch_size, len(chunks))}/{len(chunks)} chunks")

print(f"✅ Imported {len(chunks)} chunks")

# Update sequence
with engine.begin() as conn:
    result = conn.execute(text("SELECT MAX(id) FROM chunks"))
    max_id = result.scalar() or 0
    conn.execute(text(f"SELECT setval('chunks_id_seq', {max_id}, true)"))

# Import embeddings
print("🧮 Importing embeddings...")
with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

for i in range(0, len(embeddings), batch_size):
    with engine.begin() as conn:
        for emb in embeddings[i : i + batch_size]:
            embedding_str = str(emb["embedding"])
            conn.execute(
                text(
                    """
                    INSERT INTO embeddings (id, chunk_id, embedding, created_at)
                    VALUES (:id, :chunk_id, CAST(:embedding AS vector(384)), :created_at)
                    ON CONFLICT (chunk_id) DO NOTHING
                """
                ),
                {
                    "id": emb["id"],
                    "chunk_id": emb["chunk_id"],
                    "embedding": embedding_str,
                    "created_at": emb["created_at"],
                },
            )
    if (i + batch_size) % 200 == 0 or i + batch_size >= len(embeddings):
        print(f"  ✓ {min(i+batch_size, len(embeddings))}/{len(embeddings)} embeddings")

print(f"✅ Imported {len(embeddings)} embeddings")

# Update sequence
with engine.begin() as conn:
    result = conn.execute(text("SELECT MAX(id) FROM embeddings"))
    max_id = result.scalar() or 0
    conn.execute(text(f"SELECT setval('embeddings_id_seq', {max_id}, true)"))

# Import conversations
print("💬 Importing conversations...")
with open(EXPORT_DIR / "conversations.json", "r", encoding="utf-8") as f:
    conversations = json.load(f)

with engine.begin() as conn:
    for conv in conversations:
        conn.execute(
            text(
                """
                INSERT INTO conversations (
                    id, conversation_id, user_message, assistant_response,
                    sources, confidence, processing_time, created_at
                ) VALUES (
                    :id, :conversation_id, :user_message, :assistant_response,
                    :sources, :confidence, :processing_time, :created_at
                )
                ON CONFLICT (conversation_id) DO NOTHING
            """
            ),
            conv,
        )
print(f"✅ Imported {len(conversations)} conversations")

# Update sequence
with engine.begin() as conn:
    result = conn.execute(text("SELECT MAX(id) FROM conversations"))
    max_id = result.scalar() or 0
    conn.execute(text(f"SELECT setval('conversations_id_seq', {max_id}, true)"))

# Verify
print("\n📊 Verification:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM chunks"))
    print(f"  Chunks: {result.scalar()}")
    result = conn.execute(text("SELECT COUNT(*) FROM embeddings"))
    print(f"  Embeddings: {result.scalar()}")
    result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
    print(f"  Conversations: {result.scalar()}")

elapsed = time.time() - start_time
print(f"\n✅ Import completed in {elapsed:.1f} seconds!")
