"""Import embeddings with 768 dimensions"""

import psycopg2
import json
from pathlib import Path
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🧮 Importing embeddings (768 dimensions)...")
conn = psycopg2.connect(SUPABASE_URL)
cur = conn.cursor()

start_time = time.time()

with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

print(f"  Total embeddings to import: {len(embeddings)}")

imported = 0
errors = 0

for i, emb in enumerate(embeddings):
    try:
        cur.execute(
            """
            INSERT INTO embeddings (id, chunk_id, embedding, created_at)
            VALUES (%s, %s, %s::vector(768), %s)
        """,
            (emb["id"], emb["chunk_id"], str(emb["embedding"]), emb["created_at"]),
        )
        imported += 1

        if imported % 50 == 0:
            conn.commit()

        if imported % 200 == 0:
            print(f"  ✓ {imported}/{len(embeddings)} imported")

    except Exception as e:
        errors += 1
        conn.rollback()
        if errors <= 3:
            print(f"  Error: {str(e)[:80]}")

conn.commit()

# Update sequence
try:
    cur.execute(
        "SELECT setval('embeddings_id_seq', (SELECT MAX(id) FROM embeddings), true)"
    )
    conn.commit()
except:
    pass

print(f"\n✅ Embeddings imported: {imported}")
print(f"   Errors: {errors}")

# Also import conversations
print("\n💬 Importing conversations...")
with open(EXPORT_DIR / "conversations.json", "r", encoding="utf-8") as f:
    conversations = json.load(f)

conv_imported = 0
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
            )
        """,
            conv,
        )
        conv_imported += 1
    except Exception:
        conn.rollback()

conn.commit()

try:
    cur.execute(
        "SELECT setval('conversations_id_seq', (SELECT MAX(id) FROM conversations), true)"
    )
    conn.commit()
except:
    pass

print(f"✅ Conversations imported: {conv_imported}")

# Final summary
print("\n" + "=" * 50)
print("📊 FINAL STATUS")
cur.execute("SELECT COUNT(*) FROM chunks")
print(f"  Chunks: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM embeddings")
print(f"  Embeddings: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM conversations")
print(f"  Conversations: {cur.fetchone()[0]}")

elapsed = time.time() - start_time
print(f"\n✅ Done in {elapsed:.1f}s")
print("🎉 Supabase ready!")

cur.close()
conn.close()
