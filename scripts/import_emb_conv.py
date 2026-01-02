"""Import embeddings and conversations only"""

import psycopg2
import json
from pathlib import Path
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🔄 Importing embeddings and conversations...")
conn = psycopg2.connect(SUPABASE_URL)
cur = conn.cursor()

start_time = time.time()

# Import embeddings
print("\n🧮 Importing embeddings...")
with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

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
        conn.commit()
    except Exception as e:
        skipped += 1
        conn.rollback()
        if skipped <= 3:
            print(f"  Skip {emb['id']}: {str(e)[:50]}")
        continue

    if imported % 200 == 0:
        print(f"  ✓ {imported} imported, {skipped} skipped")

# Update sequence if any imported
if imported > 0:
    try:
        cur.execute(
            "SELECT setval('embeddings_id_seq', (SELECT MAX(id) FROM embeddings), true)"
        )
        conn.commit()
    except:
        pass

print(f"\n✅ Embeddings imported: {imported}, skipped: {skipped}")

# Import conversations
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
            ) ON CONFLICT (conversation_id) DO NOTHING
        """,
            conv,
        )
        conv_imported += 1
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"  Skip conv {conv.get('id')}: {str(e)[:50]}")

# Update sequence
try:
    cur.execute(
        "SELECT setval('conversations_id_seq', (SELECT MAX(id) FROM conversations), true)"
    )
    conn.commit()
except:
    pass

print(f"\n✅ Conversations imported: {conv_imported}")

# Final summary
print("\n" + "=" * 50)
print("📊 FINAL STATUS")
print("=" * 50)
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
