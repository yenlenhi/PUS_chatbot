#!/usr/bin/env python3
"""
Check data integrity between SQLite and PostgreSQL
"""
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL connection
DB_USER = os.getenv("POSTGRES_USER", "uni_bot_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "uni_bot_password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "uni_bot_db")

POSTGRES_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLite path
SQLITE_PATH = Path("data/embeddings/chatbot.db")


def check_postgresql():
    """Check PostgreSQL data"""
    print("\n" + "=" * 60)
    print("📊 CHECKING POSTGRESQL DATA")
    print("=" * 60)

    try:
        engine = create_engine(POSTGRES_URL)
        with engine.connect() as conn:
            # Check chunks
            result = conn.execute(text("SELECT COUNT(*) as count FROM chunks"))
            chunks_count = result.scalar()
            print(f"✅ Chunks table: {chunks_count} records")

            # Check embeddings
            result = conn.execute(text("SELECT COUNT(*) as count FROM embeddings"))
            embeddings_count = result.scalar()
            print(f"✅ Embeddings table: {embeddings_count} records")

            # Check conversations
            result = conn.execute(text("SELECT COUNT(*) as count FROM conversations"))
            conversations_count = result.scalar()
            print(f"✅ Conversations table: {conversations_count} records")

            # Check unique files
            result = conn.execute(
                text("SELECT COUNT(DISTINCT source_file) as count FROM chunks")
            )
            unique_files = result.scalar()
            print(f"✅ Unique files: {unique_files}")

            # Sample chunk
            result = conn.execute(
                text("SELECT id, source_file, content FROM chunks LIMIT 1")
            )
            row = result.fetchone()
            if row:
                print("\n📝 Sample chunk:")
                print(f"   ID: {row[0]}")
                print(f"   Source: {row[1]}")
                print(f"   Content: {row[2][:100]}...")

            return {
                "chunks": chunks_count,
                "embeddings": embeddings_count,
                "conversations": conversations_count,
                "unique_files": unique_files,
            }
    except Exception as e:
        print(f"❌ Error checking PostgreSQL: {e}")
        return None


def check_sqlite():
    """Check SQLite data"""
    print("\n" + "=" * 60)
    print("📊 CHECKING SQLITE DATA")
    print("=" * 60)

    if not SQLITE_PATH.exists():
        print(f"❌ SQLite file not found: {SQLITE_PATH}")
        return None

    try:
        conn = sqlite3.connect(SQLITE_PATH)
        cursor = conn.cursor()

        # Check chunks
        cursor.execute("SELECT COUNT(*) FROM chunks")
        chunks_count = cursor.fetchone()[0]
        print(f"✅ Chunks table: {chunks_count} records")

        # Check embeddings
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        embeddings_count = cursor.fetchone()[0]
        print(f"✅ Embeddings table: {embeddings_count} records")

        # Check conversations (may not exist in SQLite)
        try:
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conversations_count = cursor.fetchone()[0]
            print(f"✅ Conversations table: {conversations_count} records")
        except sqlite3.OperationalError:
            conversations_count = None
            print("⚠️ Conversations table: Not found in SQLite (expected)")

        # Check unique files
        cursor.execute("SELECT COUNT(DISTINCT source_file) FROM chunks")
        unique_files = cursor.fetchone()[0]
        print(f"✅ Unique files: {unique_files}")

        # Sample chunk
        cursor.execute("SELECT id, source_file, content FROM chunks LIMIT 1")
        row = cursor.fetchone()
        if row:
            print("\n📝 Sample chunk:")
            print(f"   ID: {row[0]}")
            print(f"   Source: {row[1]}")
            print(f"   Content: {row[2][:100]}...")

        conn.close()

        return {
            "chunks": chunks_count,
            "embeddings": embeddings_count,
            "conversations": conversations_count,
            "unique_files": unique_files,
        }
    except Exception as e:
        print(f"❌ Error checking SQLite: {e}")
        return None


def compare_data(pg_data, sqlite_data):
    """Compare PostgreSQL and SQLite data"""
    print("\n" + "=" * 60)
    print("📊 DATA COMPARISON")
    print("=" * 60)

    if not pg_data or not sqlite_data:
        print("❌ Cannot compare - missing data from one or both databases")
        return

    print(f"\n{'Metric':<20} {'PostgreSQL':<15} {'SQLite':<15} {'Match':<10}")
    print("-" * 60)

    # Compare chunks and embeddings (main data)
    for key in ["chunks", "embeddings", "unique_files"]:
        pg_val = pg_data.get(key, 0)
        sqlite_val = sqlite_data.get(key, 0)
        match = "✅ YES" if pg_val == sqlite_val else "❌ NO"
        print(f"{key:<20} {pg_val:<15} {sqlite_val:<15} {match:<10}")

    # Conversations is expected to be 0 in PostgreSQL and None in SQLite
    pg_conv = pg_data.get("conversations", 0)
    sqlite_conv = sqlite_data.get("conversations")
    conv_match = "✅ YES" if (pg_conv == 0 and sqlite_conv is None) else "⚠️ EXPECTED"
    print(f"{'conversations':<20} {pg_conv:<15} {'N/A':<15} {conv_match:<10}")

    # Summary
    print("\n" + "=" * 60)
    chunks_match = pg_data.get("chunks") == sqlite_data.get("chunks")
    embeddings_match = pg_data.get("embeddings") == sqlite_data.get("embeddings")
    files_match = pg_data.get("unique_files") == sqlite_data.get("unique_files")

    if chunks_match and embeddings_match and files_match:
        print("✅ DATA INTEGRITY CHECK PASSED - All data matches!")
        print("\n📊 Migration Summary:")
        print(f"   ✅ {pg_data.get('chunks')} chunks migrated successfully")
        print(f"   ✅ {pg_data.get('embeddings')} embeddings migrated successfully")
        print(f"   ✅ {pg_data.get('unique_files')} unique files processed")
    else:
        print("⚠️ DATA MISMATCH - PostgreSQL and SQLite have different data")
        print("\nPossible causes:")
        print("1. Migration was not completed successfully")
        print("2. Data was modified after migration")
        print("3. Connection issue with PostgreSQL")


if __name__ == "__main__":
    print("\n🔍 DATA INTEGRITY CHECK - SQLite vs PostgreSQL\n")

    pg_data = check_postgresql()
    sqlite_data = check_sqlite()

    compare_data(pg_data, sqlite_data)

    print("\n" + "=" * 60 + "\n")
