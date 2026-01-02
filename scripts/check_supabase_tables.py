"""Check Supabase tables"""

import psycopg2

SUPABASE_URL = "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"

print("🔍 Checking Supabase tables...")
conn = psycopg2.connect(SUPABASE_URL)
cur = conn.cursor()

cur.execute(
    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
)
tables = [r[0] for r in cur.fetchall()]

print(f"\n📋 Found {len(tables)} tables:")
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    count = cur.fetchone()[0]
    print(f"  - {t}: {count} records")

conn.close()
print("\n✅ Done!")
