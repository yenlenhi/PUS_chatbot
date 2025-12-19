#!/usr/bin/env python3
"""
Re-embed DB rows where stored vector dimension doesn't match the current embedding model.

Usage:
  Set `DATABASE_URL` in the environment (or the script will use the project's default in `config.settings`).
  Then run:
    python scripts/reembed_mismatched_embeddings.py --limit 0

Notes:
  - This script uses `EmbeddingService` from the project to create embeddings.
  - It updates `embeddings.embedding` by casting a vector literal via SQL: `CAST(:vec_text AS vector)`.
  - Test on a small `--limit` before running for all rows.
"""
import os
import argparse
import time
from typing import List

from sqlalchemy import create_engine, text

from config.settings import DATABASE_URL as DEFAULT_DB_URL
from src.services.embedding_service import EmbeddingService


def find_mismatched_rows(engine, desired_dim: int, limit: int = 0) -> List[dict]:
    """Return rows where stored embedding dimension != desired_dim.

    We compute dimension by splitting the text representation of the vector.
    """
    sql = (
        "SELECT e.id, e.chunk_id, e.embedding::text as embedding_text, c.text as chunk_text "
        "FROM embeddings e JOIN chunks c ON e.chunk_id = c.id "
        "WHERE array_length(string_to_array(trim(both '[]' from e.embedding::text), ','), 1) != :desired_dim "
    )
    if limit > 0:
        sql += " LIMIT :limit"

    with engine.connect() as conn:
        result = conn.execute(text(sql), {"desired_dim": desired_dim, "limit": limit})
        rows = [dict(row) for row in result.fetchall()]

    return rows


def reembed_rows(engine, embedding_service: EmbeddingService, rows: List[dict]):
    """Generate new embeddings and update the DB in a transaction."""
    if not rows:
        print("No mismatched rows found.")
        return

    print(f"Re-embedding {len(rows)} rows...")
    start = time.time()

    with engine.begin() as conn:
        for i, row in enumerate(rows, start=1):
            chunk_text = row.get("chunk_text") or ""
            emb = embedding_service.create_embedding(chunk_text)
            vec_text = "[" + ",".join(map(str, emb.tolist())) + "]"

            update_sql = text(
                "UPDATE embeddings SET embedding = CAST(:vec_text AS vector) WHERE id = :id"
            )
            conn.execute(update_sql, {"vec_text": vec_text, "id": row["id"]})

            if i % 10 == 0:
                print(f"  Updated {i}/{len(rows)}")

    elapsed = time.time() - start
    print(f"Done. Re-embedded {len(rows)} rows in {elapsed:.1f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of mismatched rows to process (0 = no limit)",
    )
    args = parser.parse_args()

    db_url = os.getenv("DATABASE_URL") or DEFAULT_DB_URL
    print(f"Using DATABASE_URL: {db_url}")

    engine = create_engine(db_url)

    emb_service = EmbeddingService()
    desired_dim = emb_service.get_embedding_dimension()
    print(f"Current embedding model dimension: {desired_dim}")

    rows = find_mismatched_rows(engine, desired_dim, limit=args.limit)
    print(f"Found {len(rows)} mismatched rows.")

    if not rows:
        return

    # Confirm before proceeding
    confirm = input(f"Proceed to re-embed {len(rows)} rows? (yes/no): ")
    if confirm.strip().lower() not in ("y", "yes"):
        print("Aborted by user.")
        return

    reembed_rows(engine, emb_service, rows)


if __name__ == "__main__":
    main()
