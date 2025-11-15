"""
Test script to verify PostgreSQL + pgvector connection and setup
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_connection():
    """Test PostgreSQL connection"""
    print("\n" + "=" * 60)
    print("🧪 PostgreSQL Connection Test")
    print("=" * 60)

    # Get connection string
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://uni_bot_user:uni_bot_password@localhost:5432/uni_bot_db",
    )

    print(f"\n📍 Connection String: {db_url.replace(db_url.split('@')[0].split('://')[1], '***')}")

    try:
        # Create engine
        engine = create_engine(db_url, echo=False)

        # Test connection
        with engine.connect() as conn:
            print("\n✅ PostgreSQL Connection Successful!")

            # Get version
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"📦 PostgreSQL Version: {version.split(',')[0]}")

            # Check pgvector extension
            result = conn.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'vector'")
            )
            if result.fetchone():
                print("✅ pgvector Extension Installed!")
            else:
                print("⚠️ pgvector Extension NOT Found!")
                print("   Attempting to create...")
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    print("✅ pgvector Extension Created!")
                except Exception as e:
                    print(f"❌ Failed to create pgvector: {e}")

            # Check tables
            result = conn.execute(
                text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            )
            tables = [row[0] for row in result.fetchall()]

            print(f"\n📊 Database Tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"   - {table}")

            # Check chunks table
            if "chunks" in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM chunks"))
                chunk_count = result.scalar()
                print(f"\n📄 Chunks in Database: {chunk_count}")

            # Check embeddings table
            if "embeddings" in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM embeddings"))
                embedding_count = result.scalar()
                print(f"🧠 Embeddings in Database: {embedding_count}")

            # Check conversations table
            if "conversations" in tables:
                result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
                conversation_count = result.scalar()
                print(f"💬 Conversations in Database: {conversation_count}")

            print("\n" + "=" * 60)
            print("✅ All Tests Passed!")
            print("=" * 60 + "\n")

            return True

    except Exception as e:
        print(f"\n❌ Connection Failed!")
        print(f"Error: {e}")
        print("\n" + "=" * 60)
        print("🆘 Troubleshooting:")
        print("=" * 60)
        print("1. Check if Docker containers are running:")
        print("   docker-compose ps")
        print("\n2. Check PostgreSQL logs:")
        print("   docker-compose logs postgres")
        print("\n3. Verify .env file has correct credentials")
        print("\n4. Try restarting containers:")
        print("   docker-compose down -v")
        print("   docker-compose up -d")
        print("=" * 60 + "\n")

        return False


def test_services():
    """Test if services can be imported"""
    print("\n" + "=" * 60)
    print("🧪 Services Import Test")
    print("=" * 60)

    try:
        print("\n📦 Importing services...")

        from src.services.postgres_database_service import PostgresDatabaseService

        print("✅ PostgresDatabaseService imported")

        from src.services.hybrid_retrieval_service import HybridRetrievalService

        print("✅ HybridRetrievalService imported")

        from src.services.ingestion_service import IngestionService

        print("✅ IngestionService imported")

        print("\n" + "=" * 60)
        print("✅ All Services Imported Successfully!")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Import Failed!")
        print(f"Error: {e}")
        print("\n" + "=" * 60)
        print("🆘 Troubleshooting:")
        print("=" * 60)
        print("1. Check if all dependencies are installed:")
        print("   pip install -r requirements.txt")
        print("\n2. Check Python version (3.11+ required):")
        print("   python --version")
        print("=" * 60 + "\n")

        return False


def main():
    """Run all tests"""
    print("\n🚀 Starting Uni Bot Data Layer Tests...\n")

    # Test connection
    connection_ok = test_connection()

    # Test services
    services_ok = test_services()

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    print(f"PostgreSQL Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Services Import: {'✅ PASS' if services_ok else '❌ FAIL'}")
    print("=" * 60 + "\n")

    if connection_ok and services_ok:
        print("🎉 All tests passed! Ready to proceed with migration.\n")
        return 0
    else:
        print("⚠️ Some tests failed. Please fix the issues above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

