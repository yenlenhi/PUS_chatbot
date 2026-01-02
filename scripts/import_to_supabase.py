"""
Import data from JSON files to Supabase PostgreSQL
Run this script after creating the schema in Supabase
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
import numpy as np
from src.utils.logger import log


def import_data(supabase_url: str):
    """Import data from JSON files to Supabase PostgreSQL"""

    try:
        # Connect to Supabase
        engine = create_engine(supabase_url)

        export_dir = Path("data/migration_export")

        if not export_dir.exists():
            log.error(f"❌ Export directory not found: {export_dir}")
            log.error("Please run export_docker_data.py first!")
            return False

        log.info("🔄 Connecting to Supabase PostgreSQL...")

        with engine.connect() as conn:
            # Import chunks
            log.info("📦 Importing chunks table...")
            with open(export_dir / "chunks.json", "r", encoding="utf-8") as f:
                chunks = json.load(f)

            for chunk in chunks:
                conn.execute(
                    text(
                        """
                        INSERT INTO chunks (
                            id, content, source_file, page_number, chunk_index,
                            heading_text, heading_level, heading_number, parent_heading,
                            is_sub_chunk, sub_chunk_index, total_sub_chunks, chunk_type,
                            word_count, char_count, created_at, updated_at
                        ) VALUES (
                            :id, :content, :source_file, :page_number, :chunk_index,
                            :heading_text, :heading_level, :heading_number, :parent_heading,
                            :is_sub_chunk, :sub_chunk_index, :total_sub_chunks, :chunk_type,
                            :word_count, :char_count, :created_at, :updated_at
                        )
                        ON CONFLICT (id) DO NOTHING
                    """
                    ),
                    chunk,
                )
            conn.commit()
            log.info(f"✅ Imported {len(chunks)} chunks")

            # Update sequence for chunks
            result = conn.execute(text("SELECT MAX(id) FROM chunks"))
            max_id = result.scalar() or 0
            conn.execute(text(f"SELECT setval('chunks_id_seq', {max_id}, true)"))
            conn.commit()

            # Import embeddings
            log.info("🧮 Importing embeddings table...")
            with open(export_dir / "embeddings.json", "r", encoding="utf-8") as f:
                embeddings = json.load(f)

            for emb in embeddings:
                # Convert list back to numpy array then to binary
                embedding_list = emb["embedding"]
                embedding_array = np.array(embedding_list, dtype=np.float32)

                conn.execute(
                    text(
                        """
                        INSERT INTO embeddings (id, chunk_id, embedding, created_at)
                        VALUES (:id, :chunk_id, :embedding::vector, :created_at)
                        ON CONFLICT (chunk_id) DO NOTHING
                    """
                    ),
                    {
                        "id": emb["id"],
                        "chunk_id": emb["chunk_id"],
                        "embedding": str(
                            embedding_list
                        ),  # pgvector accepts string format
                        "created_at": emb["created_at"],
                    },
                )
            conn.commit()
            log.info(f"✅ Imported {len(embeddings)} embeddings")

            # Update sequence for embeddings
            result = conn.execute(text("SELECT MAX(id) FROM embeddings"))
            max_id = result.scalar() or 0
            conn.execute(text(f"SELECT setval('embeddings_id_seq', {max_id}, true)"))
            conn.commit()

            # Import conversations
            log.info("💬 Importing conversations table...")
            with open(export_dir / "conversations.json", "r", encoding="utf-8") as f:
                conversations = json.load(f)

            for conv in conversations:
                conn.execute(
                    text(
                        """
                        INSERT INTO conversations (
                            id, conversation_id, user_message, assistant_response,
                            sources, confidence, processing_time, created_at
                        ) VALUES (
                            :id, :conversation_id, :user_message, :assistant_response,
                            :sources, :confidence, :processing_time, :created_at
                        )
                        ON CONFLICT (conversation_id) DO NOTHING
                    """
                    ),
                    conv,
                )
            conn.commit()
            log.info(f"✅ Imported {len(conversations)} conversations")

            # Update sequence for conversations
            result = conn.execute(text("SELECT MAX(id) FROM conversations"))
            max_id = result.scalar() or 0
            conn.execute(text(f"SELECT setval('conversations_id_seq', {max_id}, true)"))
            conn.commit()

            # Import bm25_index (without bm25_vector, will be regenerated)
            log.info("🔍 Importing bm25_index table...")
            with open(export_dir / "bm25_index.json", "r", encoding="utf-8") as f:
                bm25_data = json.load(f)

            for bm25 in bm25_data:
                # Get chunk content to regenerate bm25_vector
                result = conn.execute(
                    text("SELECT content FROM chunks WHERE id = :chunk_id"),
                    {"chunk_id": bm25["chunk_id"]},
                )
                row = result.fetchone()
                if row:
                    content = row[0]
                    conn.execute(
                        text(
                            """
                            INSERT INTO bm25_index (id, chunk_id, bm25_vector, created_at)
                            VALUES (:id, :chunk_id, to_tsvector('english', :content), :created_at)
                            ON CONFLICT (chunk_id) DO NOTHING
                        """
                        ),
                        {
                            "id": bm25["id"],
                            "chunk_id": bm25["chunk_id"],
                            "content": content,
                            "created_at": bm25["created_at"],
                        },
                    )
            conn.commit()
            log.info(f"✅ Imported {len(bm25_data)} bm25 records")

            # Update sequence for bm25_index
            result = conn.execute(text("SELECT MAX(id) FROM bm25_index"))
            max_id = result.scalar() or 0
            conn.execute(text(f"SELECT setval('bm25_index_id_seq', {max_id}, true)"))
            conn.commit()

            # Verify import
            log.info("\n" + "=" * 50)
            log.info("📊 Verifying import...")

            tables = ["chunks", "embeddings", "conversations", "bm25_index"]
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                log.info(f"  - {table}: {count} records")

            log.info("=" * 50)
            log.info("✅ Import completed successfully!")
            log.info("=" * 50)

            return True

    except Exception as e:
        log.error(f"❌ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import data to Supabase")
    parser.add_argument(
        "--url",
        required=True,
        help="Supabase connection URL (postgresql://postgres:password@host:5432/postgres)",
    )

    args = parser.parse_args()

    log.info("🚀 Starting data import to Supabase...")
    success = import_data(args.url)
    sys.exit(0 if success else 1)
