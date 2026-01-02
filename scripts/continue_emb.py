"""Continue import remaining embeddings"""

import psycopg2
import json
from pathlib import Path

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")

print("🔄 Continuing embeddings import...")
conn = psycopg2.connect(SUPABASE_URL)
cur = conn.cursor()

# Check current state
cur.execute("SELECT MAX(id) FROM embeddings")
max_id = cur.fetchone()[0] or 0
cur.execute("SELECT COUNT(*) FROM embeddings")
current = cur.fetchone()[0]
print(f"  Current: {current} embeddings, max_id: {max_id}")

with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

# Filter remaining
remaining = [e for e in embeddings if e["id"] > max_id]
print(f"  Remaining to import: {len(remaining)}")

imported = 0
for i, emb in enumerate(remaining):
    try:
        cur.execute(
            """
            INSERT INTO embeddings (id, chunk_id, embedding, created_at)
            VALUES (%s, %s, %s::vector(768), %s)
            ON CONFLICT (chunk_id) DO NOTHING
        """,
            (emb["id"], emb["chunk_id"], str(emb["embedding"]), emb["created_at"]),
        )
        imported += 1

        if imported % 50 == 0:
            conn.commit()
        if imported % 200 == 0:
            print(f"  ✓ {imported}/{len(remaining)}")
    except:
        conn.rollback()

conn.commit()

cur.execute("SELECT COUNT(*) FROM embeddings")
total = cur.fetchone()[0]
print(f"\n✅ Total embeddings now: {total}")

# Check conversations
cur.execute("SELECT COUNT(*) FROM conversations")
conv = cur.fetchone()[0]
if conv == 0:
    print("\n💬 Importing conversations...")
    with open(EXPORT_DIR / "conversations.json", "r", encoding="utf-8") as f:
        conversations = json.load(f)

    for c in conversations:
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
                c,
            )
        except:
            conn.rollback()
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM conversations")
    print(f"✅ Conversations: {cur.fetchone()[0]}")

print("\n🎉 Done!")
cur.close()
conn.close()
