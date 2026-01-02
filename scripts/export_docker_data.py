"""
Export data from Docker PostgreSQL to JSON files
Run this script to backup your current data before migrating to Supabase
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
import numpy as np
from config.settings import DATABASE_URL
from src.utils.logger import log


def export_data():
    """Export all data from Docker PostgreSQL to JSON files"""

    try:
        # Connect to Docker PostgreSQL
        engine = create_engine(DATABASE_URL)

        export_dir = Path("data/migration_export")
        export_dir.mkdir(parents=True, exist_ok=True)

        log.info("🔄 Connecting to Docker PostgreSQL...")

        with engine.connect() as conn:
            # Export chunks
            log.info("📦 Exporting chunks table...")
            result = conn.execute(text("SELECT * FROM chunks ORDER BY id"))
            chunks = []
            for row in result:
                chunk_dict = dict(row._mapping)
                # Convert datetime to string
                if chunk_dict.get("created_at"):
                    chunk_dict["created_at"] = str(chunk_dict["created_at"])
                if chunk_dict.get("updated_at"):
                    chunk_dict["updated_at"] = str(chunk_dict["updated_at"])
                chunks.append(chunk_dict)

            with open(export_dir / "chunks.json", "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)
            log.info(f"✅ Exported {len(chunks)} chunks")

            # Export embeddings
            log.info("🧮 Exporting embeddings table...")
            result = conn.execute(
                text(
                    "SELECT id, chunk_id, embedding, created_at FROM embeddings ORDER BY id"
                )
            )
            embeddings = []
            for row in result:
                row_dict = dict(row._mapping)
                # Convert embedding bytes to list
                if row_dict.get("embedding"):
                    embedding_data = row_dict["embedding"]
                    # pgvector can store as string or bytes depending on driver
                    if isinstance(embedding_data, str):
                        # Parse string format: "[0.1, 0.2, ...]"
                        import ast

                        row_dict["embedding"] = ast.literal_eval(embedding_data)
                    elif isinstance(embedding_data, bytes):
                        # Convert bytes to numpy array then to list
                        embedding_array = np.frombuffer(
                            embedding_data, dtype=np.float32
                        )
                        row_dict["embedding"] = embedding_array.tolist()
                    else:
                        # Already a list
                        row_dict["embedding"] = list(embedding_data)
                if row_dict.get("created_at"):
                    row_dict["created_at"] = str(row_dict["created_at"])
                embeddings.append(row_dict)

            with open(export_dir / "embeddings.json", "w", encoding="utf-8") as f:
                json.dump(embeddings, f, ensure_ascii=False, indent=2)
            log.info(f"✅ Exported {len(embeddings)} embeddings")

            # Export conversations
            log.info("💬 Exporting conversations table...")
            result = conn.execute(text("SELECT * FROM conversations ORDER BY id"))
            conversations = []
            for row in result:
                conv_dict = dict(row._mapping)
                if conv_dict.get("created_at"):
                    conv_dict["created_at"] = str(conv_dict["created_at"])
                conversations.append(conv_dict)

            with open(export_dir / "conversations.json", "w", encoding="utf-8") as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2)
            log.info(f"✅ Exported {len(conversations)} conversations")

            # Export bm25_index
            log.info("🔍 Exporting bm25_index table...")
            result = conn.execute(
                text("SELECT id, chunk_id, created_at FROM bm25_index ORDER BY id")
            )
            bm25_data = []
            for row in result:
                bm25_dict = dict(row._mapping)
                if bm25_dict.get("created_at"):
                    bm25_dict["created_at"] = str(bm25_dict["created_at"])
                # Note: bm25_vector (TSVECTOR) is not exported as it can be regenerated
                bm25_data.append(bm25_dict)

            with open(export_dir / "bm25_index.json", "w", encoding="utf-8") as f:
                json.dump(bm25_data, f, ensure_ascii=False, indent=2)
            log.info(f"✅ Exported {len(bm25_data)} bm25 records")

            # Create summary
            summary = {
                "export_date": str(np.datetime64("now")),
                "source_database": (
                    DATABASE_URL.split("@")[1]
                    if "@" in DATABASE_URL
                    else "Docker PostgreSQL"
                ),
                "tables_exported": {
                    "chunks": len(chunks),
                    "embeddings": len(embeddings),
                    "conversations": len(conversations),
                    "bm25_index": len(bm25_data),
                },
                "total_records": len(chunks)
                + len(embeddings)
                + len(conversations)
                + len(bm25_data),
            }

            with open(export_dir / "export_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            log.info("\n" + "=" * 50)
            log.info("✅ Export completed successfully!")
            log.info(f"📂 Files saved to: {export_dir.absolute()}")
            log.info("=" * 50)
            log.info(f"Total records exported: {summary['total_records']}")
            log.info(f"  - Chunks: {len(chunks)}")
            log.info(f"  - Embeddings: {len(embeddings)}")
            log.info(f"  - Conversations: {len(conversations)}")
            log.info(f"  - BM25 Index: {len(bm25_data)}")
            log.info("=" * 50)

            return True

    except Exception as e:
        log.error(f"❌ Export failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    log.info("🚀 Starting data export from Docker PostgreSQL...")
    success = export_data()
    sys.exit(0 if success else 1)
