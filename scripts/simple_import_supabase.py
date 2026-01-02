"""Simple fast import with psycopg2 - no CSV"""

import psycopg2
import json
from pathlib import Path
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🚀 Importing to Supabase...\n")
conn = psycopg2.connect(SUPABASE_URL)
cur = conn.cursor()
start_time = time.time()

# Import chunks
print("📦 Importing chunks...")
with open(EXPORT_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

for i, chunk in enumerate(chunks):
    if i % 500 == 0 and i > 0:
        print(f"  ✓ {i}/{len(chunks)} chunks")

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

    # Commit every 100 records
    if i % 100 == 0:
        conn.commit()

conn.commit()
print(f"✅ Imported {len(chunks)} chunks")

# Update sequence
cur.execute("SELECT setval('chunks_id_seq', (SELECT MAX(id) FROM chunks), true)")
conn.commit()

# Import conversations
print("💬 Importing conversations...")
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
print(f"✅ Imported {len(conversations)} conversations")

# Update sequence
cur.execute(
    "SELECT setval('conversations_id_seq', (SELECT MAX(id) FROM conversations), true)"
)
conn.commit()

# Import embeddings
print("🧮 Importing embeddings...")
with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

imported = 0
skipped = 0

for i, emb in enumerate(embeddings):
    if i % 100 == 0 and i > 0:
        print(
            f"  ✓ {i}/{len(embeddings)} processed (imported: {imported}, skipped: {skipped})"
        )
        conn.commit()

    emb_list = emb["embedding"]
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
    except Exception as e:
        skipped += 1
        if "duplicate" not in str(e).lower() and skipped <= 3:
            print(f"  ⚠️ Error: {str(e)[:60]}")

conn.commit()
print(f"✅ Imported {imported} embeddings ({skipped} skipped)")

# Update sequence
cur.execute(
    "SELECT setval('embeddings_id_seq', (SELECT MAX(id) FROM embeddings), true)"
)
conn.commit()

# Verify
print("\n📊 Verification:")
cur.execute("SELECT COUNT(*) FROM chunks")
print(f"  ✅ Chunks: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM embeddings")
emb_count = cur.fetchone()[0]
print(f"  ✅ Embeddings: {emb_count}")

cur.execute("SELECT COUNT(*) FROM conversations")
print(f"  ✅ Conversations: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM chunks")
chunk_count = cur.fetchone()[0]
if chunk_count > 0 and emb_count > 0:
    coverage = (emb_count / chunk_count) * 100
    print(f"  📈 Coverage: {coverage:.1f}%")

cur.close()
conn.close()

elapsed = time.time() - start_time
print(f"\n✅ Completed in {elapsed:.1f} seconds!")
print("🎉 Supabase ready!")
