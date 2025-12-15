"""
Migration script to add document_attachments table
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL
from src.utils.logger import log


def create_attachments_table():
    """Create document_attachments table"""
    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            # Create document_attachments table
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS document_attachments (
                        id SERIAL PRIMARY KEY,
                        file_name VARCHAR(255) NOT NULL,
                        file_type VARCHAR(50) NOT NULL,
                        file_path VARCHAR(500) NOT NULL,
                        file_size INTEGER,
                        description TEXT,
                        keywords TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """
                )
            )
            log.info("✅ Created document_attachments table")

            # Create chunk_attachments junction table (many-to-many relationship)
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS chunk_attachments (
                        id SERIAL PRIMARY KEY,
                        chunk_id INTEGER NOT NULL,
                        attachment_id INTEGER NOT NULL,
                        relevance_score FLOAT DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE,
                        FOREIGN KEY (attachment_id) REFERENCES document_attachments (id) ON DELETE CASCADE,
                        UNIQUE(chunk_id, attachment_id)
                    )
                """
                )
            )
            log.info("✅ Created chunk_attachments junction table")

            # Create indexes
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_attachments_filename ON document_attachments(file_name)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_attachments_keywords ON document_attachments USING GIN(keywords)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_chunk_attachments_chunk ON chunk_attachments(chunk_id)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_chunk_attachments_attachment ON chunk_attachments(attachment_id)"
                )
            )
            log.info("✅ Created indexes")

            conn.commit()
            log.info("✅ Migration completed successfully")

    except Exception as e:
        log.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    create_attachments_table()
