"""
Fix embeddings table sequence issue
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config import settings


def fix_embeddings_sequence():
    """Fix the embeddings table sequence"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        print("🔧 Fixing embeddings table sequence...")

        # Get max id from embeddings
        result = conn.execute(text("SELECT MAX(id) FROM embeddings"))
        max_id = result.scalar() or 0
        print(f"   Max id in embeddings: {max_id}")

        # Reset sequence to max_id + 1
        new_val = max_id + 1
        conn.execute(text(f"SELECT setval('embeddings_id_seq', {new_val}, false)"))
        conn.commit()
        print(f"   ✅ Sequence reset to {new_val}")

        # Also fix chunks sequence
        result = conn.execute(text("SELECT MAX(id) FROM chunks"))
        max_chunk_id = result.scalar() or 0
        print(f"   Max id in chunks: {max_chunk_id}")

        new_chunk_val = max_chunk_id + 1
        conn.execute(text(f"SELECT setval('chunks_id_seq', {new_chunk_val}, false)"))
        conn.commit()
        print(f"   ✅ Chunks sequence reset to {new_chunk_val}")

        print("\n✅ All sequences fixed!")


if __name__ == "__main__":
    fix_embeddings_sequence()
