"""
Migration script to add is_active column to chunks table.
This allows admin to activate/deactivate PDF documents.
When is_active = false, the chunks won't be retrieved by LLM.
"""

import sys

sys.path.insert(0, ".")

from sqlalchemy import text
from src.services.postgres_database_service import PostgresDatabaseService


def main():
    print("🚀 Starting migration: Add is_active column to chunks table")

    db = PostgresDatabaseService()
    session = db.SessionLocal()

    try:
        # Check if column already exists
        result = session.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'chunks' AND column_name = 'is_active'
        """
            )
        )

        if result.fetchone():
            print("✅ Column 'is_active' already exists in chunks table")
            return

        # Add is_active column with default value TRUE (all existing chunks are active)
        print("📝 Adding 'is_active' column to chunks table...")
        session.execute(
            text(
                """
            ALTER TABLE chunks 
            ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL
        """
            )
        )
        session.commit()
        print("✅ Column 'is_active' added successfully")

        # Create index for faster queries
        print("📝 Creating index on is_active column...")
        session.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_chunks_is_active 
            ON chunks(is_active)
        """
            )
        )
        session.commit()
        print("✅ Index created successfully")

        # Verify
        result = session.execute(
            text(
                """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active
            FROM chunks
        """
            )
        )
        row = result.fetchone()
        print(f"📊 Total chunks: {row[0]}, Active chunks: {row[1]}")

        print("\n🎉 Migration completed successfully!")

    except Exception as e:
        session.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
