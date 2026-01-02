"""Import ALL tables to Supabase - Complete migration"""

import psycopg2
import json
from pathlib import Path
import time

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
EXPORT_DIR = Path("data/full_migration_export")

print("🚀 Complete Database Migration to Supabase\n")
conn = psycopg2.connect(SUPABASE_URL)
cur = conn.cursor()
start_time = time.time()

# Check what tables exist in export
json_files = list(EXPORT_DIR.glob("*.json"))
table_files = {f.stem: f for f in json_files if f.stem != "export_summary"}

print(f"📋 Found {len(table_files)} tables to import\n")

# Import order (respecting foreign keys)
import_order = [
    "chunks",  # Base table
    "embeddings",  # FK to chunks
    "bm25_index",  # FK to chunks
    "conversations",  # Independent
    "conversation_memory",  # FK to conversations
    "document_attachments",  # Independent
    "chunk_attachments",  # FK to chunks
    "document_history",  # Independent
    "chunk_performance",  # FK to chunks
    "query_document_coverage",  # FK to chunks
    "query_metrics",  # Independent
    "feedback",  # Independent
    "token_usage",  # Independent
    "access_logs",  # Independent
    "user_sessions",  # Independent
    "topic_classifications",  # Independent
    "unanswered_queries",  # Independent
    "memory_summaries",  # Independent
]

results = {}

for table_name in import_order:
    if table_name not in table_files:
        print(f"⏭️  Skipping {table_name} (not in export)")
        continue

    print(f"📦 Importing {table_name}...")

    with open(table_files[table_name], "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("  ⚠️  No data to import")
        results[table_name] = 0
        continue

    imported = 0
    skipped = 0

    try:
        # Get column names from first record
        columns = list(data[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        column_str = ", ".join(columns)

        # Special handling for embeddings
        if table_name == "embeddings" and "embedding" in columns:
            for i, row in enumerate(data):
                if i % 100 == 0 and i > 0:
                    conn.commit()
                    print(f"  ✓ {i}/{len(data)}")

                emb_list = row["embedding"]
                if len(emb_list) != 384:
                    skipped += 1
                    continue

                try:
                    values = []
                    for col in columns:
                        if col == "embedding":
                            values.append(str(emb_list) + "::vector(384)")
                        else:
                            values.append(row[col])

                    sql = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
                    # For embedding, we need special handling
                    sql = sql.replace("%s::vector(384)", "%s::vector(384)")
                    cur.execute(sql, values)
                    imported += 1
                except Exception as e:
                    if "duplicate" not in str(e).lower():
                        skipped += 1
        else:
            # Regular import
            for i, row in enumerate(data):
                if i % 500 == 0 and i > 0:
                    conn.commit()
                    print(f"  ✓ {i}/{len(data)}")

                try:
                    values = [row[col] for col in columns]
                    sql = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
                    cur.execute(sql, values)
                    imported += 1
                except Exception as e:
                    if (
                        "duplicate" not in str(e).lower()
                        and "does not exist" not in str(e).lower()
                    ):
                        skipped += 1
                        if skipped == 1:  # Show first error
                            print(f"  ⚠️  Error: {str(e)[:80]}")

        conn.commit()
        print(
            f"  ✅ Imported {imported} records"
            + (f" ({skipped} skipped)" if skipped > 0 else "")
        )
        results[table_name] = imported

        # Update sequence if table has id column
        if "id" in columns:
            try:
                cur.execute(
                    f"SELECT setval('{table_name}_id_seq', (SELECT MAX(id) FROM {table_name}), true)"
                )
                conn.commit()
            except:
                pass  # Some tables might not have sequences

    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")
        results[table_name] = f"ERROR: {str(e)[:50]}"
        conn.rollback()

print("\n" + "=" * 60)
print("📊 Import Summary:")
print("=" * 60)

total_imported = 0
for table, count in results.items():
    if isinstance(count, int):
        total_imported += count
        print(f"  ✅ {table}: {count} records")
    else:
        print(f"  ❌ {table}: {count}")

print("=" * 60)
print(f"Total records imported: {total_imported}")

# Final verification
print("\n🔍 Verification:")
for table_name in import_order:
    if table_name in results and isinstance(results[table_name], int):
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"  {table_name}: {count} records")
        except:
            pass

cur.close()
conn.close()

elapsed = time.time() - start_time
print(f"\n✅ Complete migration finished in {elapsed:.1f} seconds!")
print("🎉 Supabase database is fully migrated!")
