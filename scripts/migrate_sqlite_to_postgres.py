#!/usr/bin/env python3
"""
Migration script: SQLite → PostgreSQL
Migrates chunks, embeddings, and conversations data
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from sqlalchemy import create_engine, text


def get_sqlite_connection():
    """Connect to SQLite database"""
    db_path = Path("data/embeddings/chatbot.db")
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {db_path}")
    return sqlite3.connect(str(db_path))


def get_postgres_connection():
    """Connect to PostgreSQL database"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL not set in .env")
    return create_engine(db_url)


def migrate_chunks(sqlite_conn, postgres_engine):
    """Migrate chunks from SQLite to PostgreSQL"""
    print("\n" + "=" * 60)
    print("📦 MIGRATING CHUNKS")
    print("=" * 60)

    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chunks")
    total_chunks = cursor.fetchone()[0]

    print(f"Total chunks to migrate: {total_chunks}")

    cursor.execute(
        """
        SELECT id, content, source_file, page_number, chunk_index,
               heading_text, heading_level, heading_number, parent_heading,
               is_sub_chunk, sub_chunk_index, total_sub_chunks,
               chunk_type, word_count, char_count, created_at
        FROM chunks
    """
    )

    chunks_data = []
    for row in tqdm(cursor.fetchall(), total=total_chunks, desc="Reading chunks"):
        chunks_data.append(
            {
                "id": row[0],
                "content": row[1],
                "source_file": row[2],
                "page_number": row[3],
                "chunk_index": row[4],
                "heading_text": row[5],
                "heading_level": row[6],
                "heading_number": row[7],
                "parent_heading": row[8],
                "is_sub_chunk": bool(row[9]),
                "sub_chunk_index": row[10],
                "total_sub_chunks": row[11],
                "chunk_type": row[12],
                "word_count": row[13],
                "char_count": row[14],
                "created_at": row[15],
            }
        )

    # Insert into PostgreSQL
    with postgres_engine.connect() as conn:
        for chunk in tqdm(chunks_data, desc="Inserting chunks"):
            conn.execute(
                text(
                    """
                INSERT INTO chunks (id, content, source_file, page_number, chunk_index,
                                   heading_text, heading_level, heading_number, parent_heading,
                                   is_sub_chunk, sub_chunk_index, total_sub_chunks,
                                   chunk_type, word_count, char_count, created_at)
                VALUES (:id, :content, :source_file, :page_number, :chunk_index,
                       :heading_text, :heading_level, :heading_number, :parent_heading,
                       :is_sub_chunk, :sub_chunk_index, :total_sub_chunks,
                       :chunk_type, :word_count, :char_count, :created_at)
                ON CONFLICT (id) DO NOTHING
            """
                ),
                chunk,
            )
        conn.commit()

    print(f"✅ Migrated {len(chunks_data)} chunks")
    return len(chunks_data)


def migrate_embeddings(sqlite_conn, postgres_engine):
    """Migrate embeddings from SQLite to PostgreSQL"""
    print("\n" + "=" * 60)
    print("🧠 MIGRATING EMBEDDINGS")
    print("=" * 60)

    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    total_embeddings = cursor.fetchone()[0]

    print(f"Total embeddings to migrate: {total_embeddings}")

    cursor.execute(
        """
        SELECT id, chunk_id, embedding, created_at
        FROM embeddings
    """
    )

    embeddings_data = []
    for row in tqdm(
        cursor.fetchall(), total=total_embeddings, desc="Reading embeddings"
    ):
        embedding_blob = row[2]
        try:
            # Handle binary format (numpy array saved as bytes)
            if isinstance(embedding_blob, bytes):
                # Try to load as numpy array
                embedding_array = np.frombuffer(embedding_blob, dtype=np.float32)
                embedding_list = embedding_array.tolist()
            elif isinstance(embedding_blob, str):
                # Try JSON format
                embedding_list = json.loads(embedding_blob)
            else:
                print(
                    f"⚠️ Unknown embedding format for {row[0]}: {type(embedding_blob)}"
                )
                continue

            embeddings_data.append(
                {
                    "id": row[0],
                    "chunk_id": row[1],
                    "embedding": embedding_list,
                    "created_at": row[3],
                }
            )
        except Exception as e:
            print(f"⚠️ Error parsing embedding {row[0]}: {e}")
            continue

    # Insert into PostgreSQL
    with postgres_engine.connect() as conn:
        for emb in tqdm(embeddings_data, desc="Inserting embeddings"):
            conn.execute(
                text(
                    """
                INSERT INTO embeddings (id, chunk_id, embedding, created_at)
                VALUES (:id, :chunk_id, :embedding, :created_at)
                ON CONFLICT (id) DO NOTHING
            """
                ),
                {
                    "id": emb["id"],
                    "chunk_id": emb["chunk_id"],
                    "embedding": emb["embedding"],
                    "created_at": emb["created_at"],
                },
            )
        conn.commit()

    print(f"✅ Migrated {len(embeddings_data)} embeddings")
    return len(embeddings_data)


def verify_migration(sqlite_conn, postgres_engine):
    """Verify migration was successful"""
    print("\n" + "=" * 60)
    print("✅ VERIFICATION")
    print("=" * 60)

    # Check SQLite counts
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chunks")
    sqlite_chunks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    sqlite_embeddings = cursor.fetchone()[0]

    # Check PostgreSQL counts
    with postgres_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM chunks"))
        pg_chunks = result.scalar()
        result = conn.execute(text("SELECT COUNT(*) FROM embeddings"))
        pg_embeddings = result.scalar()

    print("\nChunks:")
    print(f"  SQLite: {sqlite_chunks}")
    print(f"  PostgreSQL: {pg_chunks}")
    print(f"  Match: {'✅' if sqlite_chunks == pg_chunks else '❌'}")

    print("\nEmbeddings:")
    print(f"  SQLite: {sqlite_embeddings}")
    print(f"  PostgreSQL: {pg_embeddings}")
    print(f"  Match: {'✅' if sqlite_embeddings == pg_embeddings else '❌'}")

    if sqlite_chunks == pg_chunks and sqlite_embeddings == pg_embeddings:
        print("\n🎉 Migration verification PASSED!")
        return True
    else:
        print("\n❌ Migration verification FAILED!")
        return False


def main():
    """Main migration function"""
    print("\n" + "=" * 60)
    print("🚀 STARTING SQLITE → POSTGRESQL MIGRATION")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Connect to databases
        print("\n📡 Connecting to databases...")
        sqlite_conn = get_sqlite_connection()
        postgres_engine = get_postgres_connection()
        print("✅ Connected to both databases")

        # Migrate data
        chunks_migrated = migrate_chunks(sqlite_conn, postgres_engine)
        embeddings_migrated = migrate_embeddings(sqlite_conn, postgres_engine)

        # Verify
        success = verify_migration(sqlite_conn, postgres_engine)

        # Summary
        print("\n" + "=" * 60)
        print("📊 MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Chunks migrated: {chunks_migrated}")
        print(f"Embeddings migrated: {embeddings_migrated}")
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        sqlite_conn.close()

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
