"""
Script to migrate embeddings table from 384 to 768 dimensions
Run this script to fix the vector dimension mismatch error on Railway
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL
from src.utils.logger import log


def check_current_dimension():
    """Check current vector dimension in database"""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Check if embeddings table exists
            result = conn.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'embeddings'
                );
            """
                )
            )
            table_exists = result.scalar()

            if not table_exists:
                log.info("📋 Embeddings table does not exist yet")
                return None

            # Get vector dimension
            result = conn.execute(
                text(
                    """
                SELECT 
                    atttypmod 
                FROM pg_attribute 
                WHERE attrelid = 'embeddings'::regclass 
                AND attname = 'embedding';
            """
                )
            )

            typmod = result.scalar()
            if typmod and typmod > 0:
                dimension = typmod - 4  # pgvector stores dimension as typmod-4
                log.info(f"📊 Current vector dimension: {dimension}")
                return dimension
            else:
                # Try alternative method
                result = conn.execute(
                    text(
                        """
                    SELECT vector_dims(embedding) 
                    FROM embeddings 
                    LIMIT 1;
                """
                    )
                )
                dimension = result.scalar()
                log.info(f"📊 Current vector dimension: {dimension}")
                return dimension

    except Exception as e:
        log.warning(f"⚠️ Could not determine current dimension: {e}")
        return None
    finally:
        engine.dispose()


def migrate_to_768_dimensions():
    """Migrate embeddings table to 768 dimensions"""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            log.info("=" * 60)
            log.info("🔄 Starting migration to 768 dimensions")
            log.info("=" * 60)

            # Check current dimension
            current_dim = check_current_dimension()
            if current_dim == 768:
                log.info("✅ Already using 768 dimensions, no migration needed")
                return True

            log.info(f"📊 Migrating from {current_dim} to 768 dimensions")

            # Backup existing table if it has data
            log.info("📦 Creating backup...")
            conn.execute(
                text(
                    """
                DROP TABLE IF EXISTS embeddings_backup_old;
            """
                )
            )
            conn.commit()

            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) FROM embeddings;
            """
                )
            )
            count = result.scalar()

            if count > 0:
                log.info(f"💾 Backing up {count} embeddings...")
                conn.execute(
                    text(
                        """
                    CREATE TABLE embeddings_backup_old AS 
                    SELECT * FROM embeddings;
                """
                    )
                )
                conn.commit()
                log.info("✅ Backup created")
            else:
                log.info("ℹ️ Table is empty, skipping backup")

            # Drop existing table
            log.info("🗑️ Dropping old embeddings table...")
            conn.execute(text("DROP TABLE IF EXISTS embeddings CASCADE;"))
            conn.commit()

            # Create new table with 768 dimensions
            log.info("✨ Creating new table with 768 dimensions...")
            conn.execute(
                text(
                    """
                CREATE TABLE embeddings (
                    id SERIAL PRIMARY KEY,
                    chunk_id INTEGER NOT NULL,
                    embedding vector(768),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
                    UNIQUE(chunk_id)
                );
            """
                )
            )
            conn.commit()
            log.info("✅ Table created")

            # Create index
            log.info("🔍 Creating vector index...")
            conn.execute(
                text(
                    """
                CREATE INDEX idx_embeddings_vector ON embeddings 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """
                )
            )
            conn.commit()
            log.info("✅ Index created")

            log.info("=" * 60)
            log.info("✅ Migration complete!")
            log.info("=" * 60)
            log.info("")
            log.info("⚠️ IMPORTANT: You must now rebuild embeddings!")
            log.info("Run: python scripts/build_embeddings.py")
            log.info("")

            return True

    except Exception as e:
        log.error(f"❌ Migration failed: {e}")
        return False
    finally:
        engine.dispose()


def migrate_to_384_dimensions():
    """Migrate embeddings table to 384 dimensions"""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            log.info("=" * 60)
            log.info("🔄 Starting migration to 384 dimensions")
            log.info("=" * 60)

            # Check current dimension
            current_dim = check_current_dimension()
            if current_dim == 384:
                log.info("✅ Already using 384 dimensions, no migration needed")
                return True

            log.info(f"📊 Migrating from {current_dim} to 384 dimensions")

            # Backup existing table if it has data
            log.info("📦 Creating backup...")
            conn.execute(
                text(
                    """
                DROP TABLE IF EXISTS embeddings_backup_old;
            """
                )
            )
            conn.commit()

            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) FROM embeddings;
            """
                )
            )
            count = result.scalar()

            if count > 0:
                log.info(f"💾 Backing up {count} embeddings...")
                conn.execute(
                    text(
                        """
                    CREATE TABLE embeddings_backup_old AS 
                    SELECT * FROM embeddings;
                """
                    )
                )
                conn.commit()
                log.info("✅ Backup created")
            else:
                log.info("ℹ️ Table is empty, skipping backup")

            # Drop existing table
            log.info("🗑️ Dropping old embeddings table...")
            conn.execute(text("DROP TABLE IF EXISTS embeddings CASCADE;"))
            conn.commit()

            # Create new table with 384 dimensions
            log.info("✨ Creating new table with 384 dimensions...")
            conn.execute(
                text(
                    """
                CREATE TABLE embeddings (
                    id SERIAL PRIMARY KEY,
                    chunk_id INTEGER NOT NULL,
                    embedding vector(384),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
                    UNIQUE(chunk_id)
                );
            """
                )
            )
            conn.commit()
            log.info("✅ Table created")

            # Create index
            log.info("🔍 Creating vector index...")
            conn.execute(
                text(
                    """
                CREATE INDEX idx_embeddings_vector ON embeddings 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """
                )
            )
            conn.commit()
            log.info("✅ Index created")

            log.info("=" * 60)
            log.info("✅ Migration complete!")
            log.info("=" * 60)
            log.info("")
            log.info("⚠️ IMPORTANT: You must now rebuild embeddings!")
            log.info("Run: python scripts/build_embeddings.py")
            log.info("")

            return True

    except Exception as e:
        log.error(f"❌ Migration failed: {e}")
        return False
    finally:
        engine.dispose()


def main():
    """Main entry point"""
    log.info("=" * 60)
    log.info("🔧 Vector Dimension Migration Tool")
    log.info("=" * 60)
    log.info(f"Database: {DATABASE_URL[:50]}...")
    log.info("")

    # Check current dimension
    current_dim = check_current_dimension()

    if current_dim is None:
        log.warning("⚠️ Could not determine current dimension")
        log.info("Proceeding with migration anyway...")

    # Ask user which dimension to use
    log.info("")
    log.info("Choose target dimension:")
    log.info("  1. 768 dimensions (hiieu/halong_embedding, better Vietnamese)")
    log.info("  2. 384 dimensions (keepitreal/vietnamese-sbert, faster)")
    log.info("")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        log.info("Selected: 768 dimensions")
        success = migrate_to_768_dimensions()
    elif choice == "2":
        log.info("Selected: 384 dimensions")
        success = migrate_to_384_dimensions()
    else:
        log.error("❌ Invalid choice")
        return 1

    if success:
        log.info("")
        log.info("✅ Migration successful!")
        log.info("")
        log.info("Next steps:")
        log.info("1. Update EMBEDDING_MODEL environment variable:")
        if choice == "1":
            log.info("   EMBEDDING_MODEL=hiieu/halong_embedding")
        else:
            log.info("   EMBEDDING_MODEL=keepitreal/vietnamese-sbert")
        log.info("")
        log.info("2. Rebuild embeddings:")
        log.info("   python scripts/build_embeddings.py")
        log.info("")
        return 0
    else:
        log.error("❌ Migration failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
