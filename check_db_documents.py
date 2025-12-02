"""Script to check documents stored in PostgreSQL database"""

import psycopg2
from config.settings import (
    POSTGRES_HOST,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
)


def check_documents():
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT,
        )
        cur = conn.cursor()

        # List all tables
        print("=" * 60)
        print("TABLES IN DATABASE:")
        print("=" * 60)
        cur.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        )
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            print(f"  - {t}")

        # Check documents table
        print("\n" + "=" * 60)
        print("DOCUMENTS IN DATABASE:")
        print("=" * 60)

        # Try different possible table names
        possible_tables = [
            "documents",
            "document",
            "pdf_documents",
            "chunks",
            "document_chunks",
        ]

        for table in possible_tables:
            if table in tables:
                print(f"\nTable: {table}")
                cur.execute(f"SELECT * FROM {table} LIMIT 5")
                columns = [desc[0] for desc in cur.description]
                print(f"Columns: {columns}")
                rows = cur.fetchall()
                for row in rows:
                    print(f"  {row}")

        # Get unique source files from chunks or embeddings
        print("\n" + "=" * 60)
        print("UNIQUE SOURCE FILES (from chunks/embeddings):")
        print("=" * 60)

        for table in tables:
            cur.execute(
                f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"
            )
            columns = [r[0] for r in cur.fetchall()]

            # Look for source file columns
            source_cols = [
                c
                for c in columns
                if "source" in c.lower()
                or "file" in c.lower()
                or "doc" in c.lower()
                or "pdf" in c.lower()
            ]
            if source_cols:
                print(f"\nTable '{table}' has columns: {source_cols}")
                for col in source_cols:
                    try:
                        cur.execute(f"SELECT DISTINCT {col} FROM {table}")
                        values = [r[0] for r in cur.fetchall()]
                        print(f"  Distinct values in '{col}':")
                        for v in values[:20]:  # Limit to 20
                            print(f"    - {v}")
                    except Exception as e:
                        print(f"  Error reading {col}: {e}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"PostgreSQL Error: {e}")
        print("\nTrying SQLite instead...")
        check_sqlite()


def check_sqlite():
    import sqlite3
    from config.settings import DATABASE_PATH

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()

        print("=" * 60)
        print(f"SQLITE DATABASE: {DATABASE_PATH}")
        print("=" * 60)

        # List all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"Tables: {tables}")

        for table in tables:
            print(f"\n--- Table: {table} ---")
            cur.execute(f"PRAGMA table_info({table})")
            columns = [(r[1], r[2]) for r in cur.fetchall()]
            print(f"Columns: {columns}")

            # Look for source-related columns
            source_cols = [
                c[0]
                for c in columns
                if "source" in c[0].lower()
                or "file" in c[0].lower()
                or "doc" in c[0].lower()
            ]
            if source_cols:
                for col in source_cols:
                    cur.execute(f"SELECT DISTINCT {col} FROM {table}")
                    values = [r[0] for r in cur.fetchall()]
                    print(f"Distinct '{col}' values:")
                    for v in values[:20]:
                        print(f"  - {v}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"SQLite Error: {e}")


if __name__ == "__main__":
    check_documents()
