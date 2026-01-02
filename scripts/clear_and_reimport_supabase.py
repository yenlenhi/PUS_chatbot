"""Clear all data from Supabase and reimport"""

from sqlalchemy import create_engine, text
import json
from pathlib import Path
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🗑️ Clearing all data from Supabase...")
engine = create_engine(SUPABASE_URL, pool_pre_ping=True)

with engine.begin() as conn:
    # Truncate all tables (CASCADE removes foreign key constraints)
    print("  Truncating bm25_index...")
    conn.execute(text("TRUNCATE TABLE bm25_index CASCADE"))

    print("  Truncating embeddings...")
    conn.execute(text("TRUNCATE TABLE embeddings CASCADE"))

    print("  Truncating conversations...")
    conn.execute(text("TRUNCATE TABLE conversations CASCADE"))

    print("  Truncating chunks...")
    conn.execute(text("TRUNCATE TABLE chunks CASCADE"))

    # Reset sequences
    print("  Resetting sequences...")
    conn.execute(text("SELECT setval('chunks_id_seq', 1, false)"))
    conn.execute(text("SELECT setval('embeddings_id_seq', 1, false)"))
    conn.execute(text("SELECT setval('conversations_id_seq', 1, false)"))
    conn.execute(text("SELECT setval('bm25_index_id_seq', 1, false)"))

print("✅ All data cleared!\n")

# Now reimport
start_time = time.time()

# Import chunks with batch
print("📦 Importing chunks...")
with open(EXPORT_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

batch_size = 100
with engine.begin() as conn:
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        for chunk in batch:
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
                """
                ),
                chunk,
            )
        if (i + batch_size) % 500 == 0 or i + batch_size >= len(chunks):
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

imported_count = 0
skipped_count = 0

for i in range(0, len(embeddings), 20):
    batch = embeddings[i : i + 20]
    with engine.begin() as conn:
        for emb in batch:
            try:
                # Check dimension
                emb_list = emb["embedding"]
                if len(emb_list) != 384:
                    skipped_count += 1
                    print(
                        f"  ⚠️ Skipped embedding {emb['id']} - {len(emb_list)} dimensions"
                    )
                    continue

                conn.execute(
                    text(
                        """
                        INSERT INTO embeddings (id, chunk_id, embedding, created_at)
                        VALUES (:id, :chunk_id, CAST(:embedding AS vector(384)), :created_at)
                    """
                    ),
                    {
                        "id": emb["id"],
                        "chunk_id": emb["chunk_id"],
                        "embedding": str(emb_list),
                        "created_at": emb["created_at"],
                    },
                )
                imported_count += 1
            except Exception as e:
                skipped_count += 1
                if "duplicate" not in str(e).lower():
                    print(f"  ⚠️ Error on embedding {emb['id']}: {str(e)[:100]}")

    if (i + 20) % 200 == 0 or i + 20 >= len(embeddings):
        print(
            f"  ✓ Processed {min(i+20, len(embeddings))}/{len(embeddings)} (imported: {imported_count}, skipped: {skipped_count})"
        )

print(f"✅ Imported {imported_count} embeddings ({skipped_count} skipped)")

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

# Final verification
print("\n📊 Final Verification:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM chunks"))
    chunks_count = result.scalar()
    print(f"  ✅ Chunks: {chunks_count}")

    result = conn.execute(text("SELECT COUNT(*) FROM embeddings"))
    emb_count = result.scalar()
    print(f"  ✅ Embeddings: {emb_count}")

    result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
    conv_count = result.scalar()
    print(f"  ✅ Conversations: {conv_count}")

    if chunks_count > 0 and emb_count > 0:
        coverage = (emb_count / chunks_count) * 100
        print(f"  📈 Embedding Coverage: {coverage:.1f}%")

elapsed = time.time() - start_time
print(f"\n✅ Complete reimport finished in {elapsed:.1f} seconds!")
print("🎉 Supabase database is ready!")
