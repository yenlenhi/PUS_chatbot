"""
Script to add images column to conversations table for storing image URLs from Supabase Storage
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.services.postgres_database_service import PostgresDatabaseService
from src.utils.logger import log


def add_images_column():
    """Add images column to conversations table"""
    db_service = PostgresDatabaseService()

    try:
        with db_service.engine.connect() as conn:
            # Add images column (JSON array of image URLs)
            conn.execute(
                text(
                    """
                ALTER TABLE conversations 
                ADD COLUMN IF NOT EXISTS images TEXT;
            """
                )
            )

            conn.commit()
            log.info("✅ Successfully added images column to conversations table")

            # Verify column was added
            result = conn.execute(
                text(
                    """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'conversations' AND column_name = 'images';
            """
                )
            )

            column_info = result.fetchone()
            if column_info:
                log.info(f"✅ Column verified: {column_info[0]} ({column_info[1]})")
            else:
                log.warning("⚠️ Column not found after creation")

    except Exception as e:
        log.error(f"❌ Error adding images column: {e}")
        raise


if __name__ == "__main__":
    add_images_column()
    print("Migration completed successfully!")
