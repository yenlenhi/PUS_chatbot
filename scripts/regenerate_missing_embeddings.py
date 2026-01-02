#!/usr/bin/env python3
"""
Script để tạo embeddings cho các chunks bị thiếu
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from sentence_transformers import SentenceTransformer

# Database connection
DATABASE_URL = "postgresql://postgres.thessjemstjljfbkvzih:tinhyeumaunang123@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"


def main():
    print("🔍 Finding chunks without embeddings...")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Find chunks without embeddings
    cur.execute(
        """
        SELECT c.id, c.content, c.source_file
        FROM chunks c
        LEFT JOIN embeddings e ON c.id = e.chunk_id
        WHERE e.id IS NULL
        ORDER BY c.id
    """
    )

    missing_chunks = cur.fetchall()

    if not missing_chunks:
        print("✅ All chunks have embeddings!")
        cur.close()
        conn.close()
        return

    print(f"📊 Found {len(missing_chunks)} chunks without embeddings")

    # Load embedding model
    print("🔧 Loading embedding model...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # Generate embeddings
    print("⚙️ Generating embeddings...")

    for chunk_id, content, source_file in missing_chunks:
        print(f"  Processing chunk {chunk_id} from {source_file}")

        # Generate embedding
        embedding = model.encode(content)
        embedding_list = embedding.tolist()

        # Insert embedding
        cur.execute(
            """
            INSERT INTO embeddings (chunk_id, embedding)
            VALUES (%s, %s)
            ON CONFLICT (chunk_id) DO UPDATE SET embedding = EXCLUDED.embedding
        """,
            (chunk_id, embedding_list),
        )

    conn.commit()
    print(f"✅ Generated embeddings for {len(missing_chunks)} chunks")

    # Verify
    cur.execute(
        """
        SELECT COUNT(*) FROM chunks c
        LEFT JOIN embeddings e ON c.id = e.chunk_id
        WHERE e.id IS NULL
    """
    )
    remaining = cur.fetchone()[0]

    if remaining == 0:
        print("✅ All chunks now have embeddings!")
    else:
        print(f"⚠️ Still {remaining} chunks without embeddings")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
