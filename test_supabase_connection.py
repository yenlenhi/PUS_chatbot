"""
Test Supabase PostgreSQL connection
Run this after updating DATABASE_URL to Supabase connection string
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL
from src.utils.logger import log


def test_supabase_connection():
    """Test connection to Supabase PostgreSQL"""

    try:
        log.info("🔄 Testing Supabase connection...")
        log.info(
            f"📍 Connection: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Unknown'}"
        )

        # Create engine
        engine = create_engine(DATABASE_URL, echo=False)

        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            log.info(f"✅ Connected to PostgreSQL: {version[:50]}...")

            # Check if Supabase
            if "supabase" in DATABASE_URL.lower():
                log.info("✅ Connected to Supabase PostgreSQL")

            # Check pgvector extension
            result = conn.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'vector'")
            )
            if result.fetchone():
                log.info("✅ pgvector extension is installed")
            else:
                log.error("❌ pgvector extension NOT found!")
                log.info(
                    "💡 Run in Supabase SQL Editor: CREATE EXTENSION IF NOT EXISTS vector;"
                )
                return False

            # Check tables
            log.info("\n📊 Checking tables...")
            tables = ["chunks", "embeddings", "conversations", "bm25_index"]
            all_tables_exist = True

            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    log.info(f"  ✅ {table}: {count} records")
                except Exception as e:
                    log.error(f"  ❌ {table}: Table not found or error - {e}")
                    all_tables_exist = False

            if not all_tables_exist:
                log.error("\n❌ Some tables are missing!")
                log.info("💡 Run migration script: scripts/migrate_to_supabase.sql")
                return False

            # Check indexes
            log.info("\n🔍 Checking indexes...")
            result = conn.execute(
                text(
                    """
                    SELECT tablename, indexname 
                    FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND tablename IN ('chunks', 'embeddings', 'conversations', 'bm25_index')
                    ORDER BY tablename, indexname
                """
                )
            )
            indexes = result.fetchall()

            if indexes:
                log.info(f"  ✅ Found {len(indexes)} indexes:")
                for table, index in indexes:
                    log.info(f"    - {table}.{index}")
            else:
                log.warning("  ⚠️ No indexes found (may impact performance)")

            # Check vector index specifically
            result = conn.execute(
                text(
                    """
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = 'embeddings' 
                    AND indexname LIKE '%vector%'
                """
                )
            )
            vector_index = result.fetchone()

            if vector_index:
                log.info(f"  ✅ Vector index found: {vector_index[0]}")
            else:
                log.warning(
                    "  ⚠️ Vector index not found (may impact search performance)"
                )

            # Check views
            log.info("\n�️ Checking views...")
            views = ["chunk_statistics", "embedding_statistics"]

            for view in views:
                try:
                    result = conn.execute(text(f"SELECT * FROM {view}"))
                    log.info(f"  ✅ {view}: Available")
                except Exception:
                    log.warning(f"  ⚠️ {view}: Not found")

            # Database statistics
            log.info("\n" + "=" * 50)
            log.info("📈 Database Statistics:")

            result = conn.execute(
                text("SELECT pg_size_pretty(pg_database_size(current_database()))")
            )
            db_size = result.scalar()
            log.info(f"  Database Size: {db_size}")

            result = conn.execute(text("SELECT COUNT(*) FROM chunks"))
            chunks_count = result.scalar()
            log.info(f"  Total Chunks: {chunks_count}")

            result = conn.execute(text("SELECT COUNT(*) FROM embeddings"))
            embeddings_count = result.scalar()
            log.info(f"  Total Embeddings: {embeddings_count}")

            if chunks_count > 0:
                coverage = (embeddings_count / chunks_count) * 100
                log.info(f"  Embedding Coverage: {coverage:.1f}%")

            result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
            conversations_count = result.scalar()
            log.info(f"  Total Conversations: {conversations_count}")

            result = conn.execute(
                text("SELECT COUNT(DISTINCT source_file) FROM chunks")
            )
            files_count = result.scalar()
            log.info(f"  Unique Documents: {files_count}")

            log.info("=" * 50)
            log.info("✅ All tests passed! Supabase connection is working correctly!")
            log.info("=" * 50)

            return True

    except Exception as e:
        log.error(f"\n❌ Connection test failed: {e}")
        import traceback

        traceback.print_exc()

        log.info("\n💡 Troubleshooting:")
        log.info("1. Check DATABASE_URL in .env file")
        log.info("2. Verify Supabase project is running")
        log.info("3. Check internet connection")
        log.info("4. Verify database password is correct")

        return False


if __name__ == "__main__":
    log.info("🚀 Starting Supabase connection test...\n")
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
