"""
Add missing columns to user_sessions table for analytics
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL
from src.utils.logger import log


def add_missing_columns():
    """Add missing columns to user_sessions table"""
    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            # Check if columns exist and add if missing
            columns_to_add = [
                ("user_segment", "VARCHAR(50) DEFAULT 'new'"),
                ("total_likes", "INTEGER DEFAULT 0"),
                ("total_dislikes", "INTEGER DEFAULT 0"),
            ]

            for column_name, column_def in columns_to_add:
                try:
                    # Check if column exists
                    result = conn.execute(
                        text(
                            f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'user_sessions' 
                        AND column_name = '{column_name}'
                        """
                        )
                    )

                    if result.fetchone() is None:
                        # Column doesn't exist, add it
                        log.info(f"Adding column: {column_name}")
                        conn.execute(
                            text(
                                f"ALTER TABLE user_sessions ADD COLUMN {column_name} {column_def}"
                            )
                        )
                        conn.commit()
                        log.info(f"✅ Successfully added column: {column_name}")
                    else:
                        log.info(f"✓ Column already exists: {column_name}")

                except Exception as e:
                    log.error(f"❌ Error adding column {column_name}: {e}")
                    conn.rollback()

        log.info("✅ All missing columns checked and added")

    except Exception as e:
        log.error(f"❌ Error in migration: {e}")
        raise


if __name__ == "__main__":
    log.info("Starting migration to add missing analytics columns...")
    add_missing_columns()
    log.info("Migration completed!")
