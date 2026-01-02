"""Quick import data to Supabase with batch processing"""

import json
from pathlib import Path
from sqlalchemy import create_engine, text

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🔄 Connecting to Supabase...")
engine = create_engine(SUPABASE_URL)
conn = engine.connect()

# Import chunks
print("📦 Importing chunks...")
with open(EXPORT_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

for i, chunk in enumerate(chunks):
    if i % 100 == 0:
        print(f"  Progress: {i}/{len(chunks)}")
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
conn.commit()
print(f"✅ Imported {len(chunks)} chunks")

# Update sequence
result = conn.execute(text("SELECT MAX(id) FROM chunks"))
max_id = result.scalar() or 0
conn.execute(text(f"SELECT setval('chunks_id_seq', {max_id}, true)"))
conn.commit()

# Import embeddings
print("🧮 Importing embeddings...")
with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

for i, emb in enumerate(embeddings):
    if i % 100 == 0:
        print(f"  Progress: {i}/{len(embeddings)}")
    embedding_list = emb["embedding"]
    conn.execute(
        text(
            """
            INSERT INTO embeddings (id, chunk_id, embedding, created_at)
            VALUES (:id, :chunk_id, :embedding::vector, :created_at)
            ON CONFLICT (chunk_id) DO NOTHING
        """
        ),
        {
            "id": emb["id"],
            "chunk_id": emb["chunk_id"],
            "embedding": str(embedding_list),
            "created_at": emb["created_at"],
        },
    )
conn.commit()
print(f"✅ Imported {len(embeddings)} embeddings")

# Update sequence
result = conn.execute(text("SELECT MAX(id) FROM embeddings"))
max_id = result.scalar() or 0
conn.execute(text(f"SELECT setval('embeddings_id_seq', {max_id}, true)"))
conn.commit()

# Import conversations
print("💬 Importing conversations...")
with open(EXPORT_DIR / "conversations.json", "r", encoding="utf-8") as f:
    conversations = json.load(f)

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
conn.commit()
print(f"✅ Imported {len(conversations)} conversations")

# Update sequence
result = conn.execute(text("SELECT MAX(id) FROM conversations"))
max_id = result.scalar() or 0
conn.execute(text(f"SELECT setval('conversations_id_seq', {max_id}, true)"))
conn.commit()

# Verify
print("\n📊 Verification:")
result = conn.execute(text("SELECT COUNT(*) FROM chunks"))
print(f"  Chunks: {result.scalar()}")
result = conn.execute(text("SELECT COUNT(*) FROM embeddings"))
print(f"  Embeddings: {result.scalar()}")
result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
print(f"  Conversations: {result.scalar()}")

print("\n✅ Import completed successfully!")
conn.close()
