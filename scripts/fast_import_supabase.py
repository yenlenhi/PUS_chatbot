"""Fast import using PostgreSQL COPY - much faster than INSERT"""

from sqlalchemy import create_engine, text
import json
from pathlib import Path
import csv
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/migration_export")
TEMP_DIR = Path("data/temp_csv")
TEMP_DIR.mkdir(exist_ok=True)

print("🚀 Fast import using PostgreSQL COPY command...\n")
engine = create_engine(SUPABASE_URL, pool_pre_ping=True)
start_time = time.time()

# Import chunks
print("📦 Importing chunks...")
with open(EXPORT_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Write to CSV
csv_file = TEMP_DIR / "chunks.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    if chunks:
        writer = csv.DictWriter(f, fieldnames=chunks[0].keys())
        writer.writeheader()
        writer.writerows(chunks)

# Use COPY command (much faster!)
import psycopg2

conn = psycopg2.connect(SUPABASE_URL)
cur = conn.cursor()

with open(csv_file, "r", encoding="utf-8") as f:
    cur.copy_expert(
        f"""
        COPY chunks (
            id, content, source_file, page_number, chunk_index,
            heading_text, heading_level, heading_number, parent_heading,
            is_sub_chunk, sub_chunk_index, total_sub_chunks, chunk_type,
            word_count, char_count, created_at, updated_at
        ) FROM STDIN WITH CSV HEADER
    """,
        f,
    )
conn.commit()
print(f"✅ Imported {len(chunks)} chunks")

# Update sequence
cur.execute("SELECT setval('chunks_id_seq', (SELECT MAX(id) FROM chunks), true)")
conn.commit()

# Import conversations (smaller dataset, use regular INSERT)
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

# Import embeddings (only valid 384-dim)
print("🧮 Importing embeddings (384-dim only)...")
with open(EXPORT_DIR / "embeddings.json", "r", encoding="utf-8") as f:
    embeddings = json.load(f)

imported = 0
skipped = 0

for i, emb in enumerate(embeddings):
    if i % 100 == 0 and i > 0:
        print(
            f"  Progress: {i}/{len(embeddings)} (imported: {imported}, skipped: {skipped})"
        )

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
        if "duplicate" not in str(e).lower():
            skipped += 1
            if skipped <= 5:  # Only show first 5 errors
                print(f"  ⚠️ Error: {str(e)[:80]}")

conn.commit()
print(
    f"✅ Imported {imported} embeddings ({skipped} skipped due to wrong dimension or errors)"
)

# Update sequence
cur.execute(
    "SELECT setval('embeddings_id_seq', (SELECT MAX(id) FROM embeddings), true)"
)
conn.commit()

# Cleanup
cur.close()
conn.close()
csv_file.unlink(missing_ok=True)

# Final verification
print("\n📊 Final Verification:")
with engine.connect() as db_conn:
    result = db_conn.execute(text("SELECT COUNT(*) FROM chunks"))
    chunks_count = result.scalar()
    print(f"  ✅ Chunks: {chunks_count}")

    result = db_conn.execute(text("SELECT COUNT(*) FROM embeddings"))
    emb_count = result.scalar()
    print(f"  ✅ Embeddings: {emb_count}")

    result = db_conn.execute(text("SELECT COUNT(*) FROM conversations"))
    conv_count = result.scalar()
    print(f"  ✅ Conversations: {conv_count}")

    if chunks_count > 0:
        coverage = (emb_count / chunks_count) * 100 if emb_count > 0 else 0
        print(f"  📈 Embedding Coverage: {coverage:.1f}%")

elapsed = time.time() - start_time
print(f"\n✅ Import completed in {elapsed:.1f} seconds!")
print("🎉 Supabase is ready to use!")
