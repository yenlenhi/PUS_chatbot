"""
Script to fix the UNIQUE constraint on embeddings.chunk_id
"""

import sys

sys.path.insert(0, ".")

from sqlalchemy import text
from src.services.postgres_database_service import PostgresDatabaseService


def main():
    db = PostgresDatabaseService()
    session = db.SessionLocal()

    try:
        # Check current constraints
        result = session.execute(
            text(
                """
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'embeddings'
        """
            )
        )
        constraints = result.fetchall()
        print("Current constraints on embeddings table:")
        for c in constraints:
            print(f"  - {c[0]}: {c[1]}")

        # Check if UNIQUE constraint exists on chunk_id
        has_unique = any(
            "chunk_id" in c[0].lower() for c in constraints if c[1] == "UNIQUE"
        )

        if not has_unique:
            print("\n⚠️ No UNIQUE constraint on chunk_id found!")
            print("Adding UNIQUE constraint...")

            # First, remove any duplicate chunk_ids (keep only the latest)
            session.execute(
                text(
                    """
                DELETE FROM embeddings a USING embeddings b
                WHERE a.id < b.id AND a.chunk_id = b.chunk_id
            """
                )
            )
            session.commit()
            print("✅ Removed duplicate entries")

            # Now add the constraint
            session.execute(
                text(
                    """
                ALTER TABLE embeddings 
                ADD CONSTRAINT embeddings_chunk_id_unique UNIQUE (chunk_id)
            """
                )
            )
            session.commit()
            print("✅ Added UNIQUE constraint on chunk_id")
        else:
            print("\n✅ UNIQUE constraint already exists on chunk_id")

        # Also check vector dimension
        result = session.execute(
            text(
                """
            SELECT column_name, udt_name, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'embeddings' AND column_name = 'embedding'
        """
            )
        )
        col_info = result.fetchone()
        print(f"\nEmbedding column type: {col_info}")

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
