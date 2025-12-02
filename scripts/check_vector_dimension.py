"""
Script to check and fix vector dimension in embeddings table
"""

import sys

sys.path.insert(0, ".")

from sqlalchemy import text
from src.services.postgres_database_service import PostgresDatabaseService


def main():
    db = PostgresDatabaseService()
    session = db.SessionLocal()

    try:
        # Check vector dimension using pg_attribute
        result = session.execute(
            text(
                """
            SELECT atttypmod 
            FROM pg_attribute 
            WHERE attrelid = 'embeddings'::regclass 
            AND attname = 'embedding'
        """
            )
        )
        row = result.fetchone()
        current_dim = row[0] if row else None
        print(f"Current vector dimension in database: {current_dim}")

        # Check what dimension the embedding model creates
        print("\nChecking embedding model dimension...")
        from src.services.embedding_service import EmbeddingService

        emb_service = EmbeddingService()
        test_emb = emb_service.create_embedding("test")
        model_dim = len(test_emb)
        print(f"Embedding model dimension: {model_dim}")

        if current_dim and current_dim != model_dim:
            print(
                f"\n⚠️ Dimension mismatch! Database has {current_dim}, model produces {model_dim}"
            )
            print("Need to alter the column...")

            # First, clear existing embeddings since they're incompatible
            count_result = session.execute(text("SELECT COUNT(*) FROM embeddings"))
            count = count_result.scalar()
            print(f"Will delete {count} existing embeddings...")

            if count > 0:
                session.execute(text("TRUNCATE embeddings"))
                session.commit()
                print("✅ Cleared embeddings table")

            # Alter column to new dimension
            session.execute(
                text(
                    f"ALTER TABLE embeddings ALTER COLUMN embedding TYPE vector({model_dim})"
                )
            )
            session.commit()
            print(f"✅ Changed embedding column to vector({model_dim})")
        else:
            print(f"\n✅ Vector dimension is correct: {current_dim}")

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        import traceback

        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
