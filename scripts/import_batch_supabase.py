"""Fast batch import to Supabase"""

import json
from pathlib import Path
from sqlalchemy import create_engine, text

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")
BATCH_SIZE = 100

print("🔄 Connecting to Supabase...")
engine = create_engine(SUPABASE_URL, pool_pre_ping=True)

# Import chunks
print("📦 Importing chunks...")
with open(EXPORT_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

with engine.begin() as conn:
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}/{(len(chunks)-1)//BATCH_SIZE + 1}")

        # Build values for batch insert
        values_parts = []
        params = {}
        for j, chunk in enumerate(batch):
            idx = i + j
            values_parts.append(
                f"""(
                :id_{idx}, :content_{idx}, :source_file_{idx}, :page_number_{idx}, :chunk_index_{idx},
                :heading_text_{idx}, :heading_level_{idx}, :heading_number_{idx}, :parent_heading_{idx},
                :is_sub_chunk_{idx}, :sub_chunk_index_{idx}, :total_sub_chunks_{idx}, :chunk_type_{idx},
                :word_count_{idx}, :char_count_{idx}, :created_at_{idx}, :updated_at_{idx}
            )"""
            )
            for key, value in chunk.items():
                params[f"{key}_{idx}"] = value

        sql = f"""
            INSERT INTO chunks (
                id, content, source_file, page_number, chunk_index,
                heading_text, heading_level, heading_number, parent_heading,
                is_sub_chunk, sub_chunk_index, total_sub_chunks, chunk_type,
                word_count, char_count, created_at, updated_at
            ) VALUES {', '.join(values_parts)}
            ON CONFLICT (id) DO NOTHING
        """
        conn.execute(text(sql), params)

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

with engine.begin() as conn:
    for i in range(0, len(embeddings), BATCH_SIZE):
        batch = embeddings[i : i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}/{(len(embeddings)-1)//BATCH_SIZE + 1}")

        values_parts = []
        params = {}
        for j, emb in enumerate(batch):
            idx = i + j
            values_parts.append(
                f"(:id_{idx}, :chunk_id_{idx}, CAST(:embedding_{idx} AS vector), :created_at_{idx})"
            )
            params[f"id_{idx}"] = emb["id"]
            params[f"chunk_id_{idx}"] = emb["chunk_id"]
            params[f"embedding_{idx}"] = str(emb["embedding"])
            params[f"created_at_{idx}"] = emb["created_at"]

        sql = f"""
            INSERT INTO embeddings (id, chunk_id, embedding, created_at)
            VALUES {', '.join(values_parts)}
            ON CONFLICT (chunk_id) DO NOTHING
        """
        conn.execute(text(sql), params)

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
    for i in range(0, len(conversations), BATCH_SIZE):
        batch = conversations[i : i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}/{(len(conversations)-1)//BATCH_SIZE + 1}")

        values_parts = []
        params = {}
        for j, conv in enumerate(batch):
            idx = i + j
            values_parts.append(
                f"""(
                :id_{idx}, :conversation_id_{idx}, :user_message_{idx}, :assistant_response_{idx},
                :sources_{idx}, :confidence_{idx}, :processing_time_{idx}, :created_at_{idx}
            )"""
            )
            for key, value in conv.items():
                params[f"{key}_{idx}"] = value

        sql = f"""
            INSERT INTO conversations (
                id, conversation_id, user_message, assistant_response,
                sources, confidence, processing_time, created_at
            ) VALUES {', '.join(values_parts)}
            ON CONFLICT (conversation_id) DO NOTHING
        """
        conn.execute(text(sql), params)

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

print("\n✅ Import completed successfully!")
