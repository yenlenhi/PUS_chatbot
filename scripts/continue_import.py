"""Continue import - import remaining data"""

import psycopg2
import json
from pathlib import Path
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🔄 Continuing import...")
conn = psycopg2.connect(SUPABASE_URL)
cur = conn.cursor()

# Check current state
cur.execute("SELECT COUNT(*) FROM chunks")
existing_chunks = cur.fetchone()[0]
cur.execute("SELECT MAX(id) FROM chunks")
max_chunk_id = cur.fetchone()[0] or 0
print(f"  Current chunks: {existing_chunks}, max_id: {max_chunk_id}")

cur.execute("SELECT COUNT(*) FROM embeddings")
existing_emb = cur.fetchone()[0]
print(f"  Current embeddings: {existing_emb}")

cur.execute("SELECT COUNT(*) FROM conversations")
existing_conv = cur.fetchone()[0]
print(f"  Current conversations: {existing_conv}")

start_time = time.time()

# Load data
with open(EXPORT_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

with open(EXPORT_DIR / "conversations.json", "r", encoding="utf-8") as f:
    conversations = json.load(f)

# Import remaining chunks
chunks_to_import = [c for c in chunks if c["id"] > max_chunk_id]
print(f"\n📦 Importing {len(chunks_to_import)} remaining chunks...")

for i, chunk in enumerate(chunks_to_import):
    try:
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
            ) ON CONFLICT (id) DO NOTHING
        """,
            chunk,
        )
    except:
        pass

    if i % 100 == 0:
        conn.commit()
        if i % 500 == 0 and i > 0:
            print(f"  ✓ {i}/{len(chunks_to_import)}")

conn.commit()
cur.execute(
    "SELECT setval('chunks_id_seq', (SELECT COALESCE(MAX(id), 0) FROM chunks), true)"
)
conn.commit()

cur.execute("SELECT COUNT(*) FROM chunks")
final_chunks = cur.fetchone()[0]
print(f"✅ Chunks: {final_chunks}")

# Import embeddings
print("\n🧮 Importing embeddings...")
imported = 0
skipped = 0

for i, emb in enumerate(embeddings):
    emb_list = emb["embedding"]

    if len(emb_list) != 384:
        skipped += 1
        continue

    try:
        cur.execute(
            """
            INSERT INTO embeddings (id, chunk_id, embedding, created_at)
            VALUES (%s, %s, %s::vector(384), %s)
            ON CONFLICT (chunk_id) DO NOTHING
        """,
            (emb["id"], emb["chunk_id"], str(emb_list), emb["created_at"]),
        )
        imported += 1
    except Exception:
        skipped += 1
        conn.rollback()
        continue

    if imported % 100 == 0:
        conn.commit()
        if imported % 500 == 0:
            print(f"  ✓ {imported} imported")

conn.commit()
cur.execute(
    "SELECT setval('embeddings_id_seq', (SELECT COALESCE(MAX(id), 0) FROM embeddings), true)"
)
conn.commit()

cur.execute("SELECT COUNT(*) FROM embeddings")
final_emb = cur.fetchone()[0]
print(f"✅ Embeddings: {final_emb} (skipped: {skipped})")

# Import conversations
print("\n💬 Importing conversations...")
for conv in conversations:
    try:
        cur.execute(
            """
            INSERT INTO conversations (
                id, conversation_id, user_message, assistant_response,
                sources, confidence, processing_time, created_at
            ) VALUES (
                %(id)s, %(conversation_id)s, %(user_message)s, %(assistant_response)s,
                %(sources)s, %(confidence)s, %(processing_time)s, %(created_at)s
            ) ON CONFLICT (conversation_id) DO NOTHING
        """,
            conv,
        )
    except:
        pass

conn.commit()
cur.execute(
    "SELECT setval('conversations_id_seq', (SELECT COALESCE(MAX(id), 0) FROM conversations), true)"
)
conn.commit()

cur.execute("SELECT COUNT(*) FROM conversations")
final_conv = cur.fetchone()[0]
print(f"✅ Conversations: {final_conv}")

# Final summary
print("\n" + "=" * 50)
print("📊 FINAL SUMMARY")
print("=" * 50)
cur.execute("SELECT COUNT(*) FROM chunks")
print(f"  Chunks: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM embeddings")
print(f"  Embeddings: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM conversations")
print(f"  Conversations: {cur.fetchone()[0]}")

elapsed = time.time() - start_time
print(f"\n✅ Done in {elapsed:.1f}s")

cur.close()
conn.close()
