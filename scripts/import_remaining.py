"""Import only embeddings and conversations"""

import json
from pathlib import Path
from sqlalchemy import create_engine, text
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🔄 Connecting to Supabase...")
engine = create_engine(SUPABASE_URL, pool_size=20, pool_pre_ping=True)

start_time = time.time()

# Import embeddings
print("🧮 Importing embeddings...")
with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

batch_size = 20  # Smaller batch for large embedding data
total = len(embeddings)

for i in range(0, total, batch_size):
    with engine.begin() as conn:
        for emb in embeddings[i : i + batch_size]:
            try:
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
            except Exception as e:
                print(f"Error on embedding {emb['id']}: {e}")

    progress = min(i + batch_size, total)
    if progress % 100 == 0 or progress == total:
        elapsed = time.time() - start_time
        print(f"  ✓ {progress}/{total} embeddings ({elapsed:.1f}s)")

print("✅ Imported embeddings")

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
print("\n📊 Final Verification:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM chunks"))
    print(f"  Chunks: {result.scalar()}")
    result = conn.execute(text("SELECT COUNT(*) FROM embeddings"))
    print(f"  Embeddings: {result.scalar()}")
    result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
    print(f"  Conversations: {result.scalar()}")

elapsed = time.time() - start_time
print(f"\n✅ Import completed in {elapsed:.1f} seconds!")
print("🎉 Database migration to Supabase successful!")
