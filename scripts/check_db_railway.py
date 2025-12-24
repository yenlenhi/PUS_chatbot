import sys

# Get railway variables as JSON
# If Railway CLI isn't accessible from subprocess, use the known DATABASE_URL
# from Railway variables (extracted via `railway variables --json`).
DATABASE_URL = (
    "postgresql://postgres:LHiKDukuulOBg1ryxvAJU8FjYgT.ZxBA@"
    "joeychilsonrailway-pgvectorscale.railway.internal:5432/railway"
)
print(f"Using DATABASE_URL: {DATABASE_URL}")

# Connect to Postgres
try:
    import psycopg2
except Exception as e:
    print("psycopg2 not available:", e)
    sys.exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # List tables in public schema
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    )
    tables = [row[0] for row in cur.fetchall()]
    print(f"Found {len(tables)} tables in public schema")
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t};")
            cnt = cur.fetchone()[0]
        except Exception as e:
            cnt = f"error: {e}"
        print(f"- {t}: {cnt}")

    cur.close()
    conn.close()
except Exception as e:
    print("Error connecting/querying database:", e)
    sys.exit(1)
