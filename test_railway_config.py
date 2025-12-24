"""
Test Railway deployment configuration
Tests database connection, Redis connection, and embedding service
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import (
    DATABASE_URL,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
    EMBEDDING_MODEL,
    LLM_PROVIDER,
    GEMINI_API_KEY,
)


def test_database_url():
    """Test DATABASE_URL format"""
    print("\n" + "=" * 50)
    print("🔍 Testing DATABASE_URL Configuration")
    print("=" * 50)

    print(f"\nDATABASE_URL: {DATABASE_URL[:50]}..." if DATABASE_URL else "Not set")

    # Check if URL has correct scheme
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgresql://"):
            print("✅ DATABASE_URL has correct scheme (postgresql://)")
            return True
        elif DATABASE_URL.startswith("postgres://"):
            print(
                "❌ DATABASE_URL has wrong scheme (postgres://), should be postgresql://"
            )
            return False
        else:
            print("⚠️  DATABASE_URL has unknown scheme")
            return False
    else:
        print("❌ DATABASE_URL is not set")
        return False


def test_postgres_connection():
    """Test PostgreSQL connection"""
    print("\n" + "=" * 50)
    print("🔍 Testing PostgreSQL Connection")
    print("=" * 50)

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(DATABASE_URL, pool_pre_ping=True)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("✅ PostgreSQL connected successfully")
            print(f"📊 Version: {version[:50]}...")

            # Test pgvector extension
            result = conn.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'vector'")
            )
            if result.fetchone():
                print("✅ pgvector extension is installed")
            else:
                print("⚠️  pgvector extension not found")

            return True

    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


def test_redis_config():
    """Test Redis configuration"""
    print("\n" + "=" * 50)
    print("🔍 Testing Redis Configuration")
    print("=" * 50)

    print(f"\nREDIS_HOST: {REDIS_HOST}")
    print(f"REDIS_PORT: {REDIS_PORT}")
    print(f"REDIS_DB: {REDIS_DB}")
    print(f"REDIS_PASSWORD: {'***' if REDIS_PASSWORD else 'None'}")

    return True


def test_redis_connection():
    """Test Redis connection"""
    print("\n" + "=" * 50)
    print("🔍 Testing Redis Connection")
    print("=" * 50)

    try:
        import redis

        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

        # Test connection
        client.ping()
        print("✅ Redis connected successfully")

        # Test set/get
        test_key = "test:railway"
        test_value = "hello"
        client.set(test_key, test_value, ex=60)
        retrieved = client.get(test_key)

        if retrieved and retrieved.decode() == test_value:
            print("✅ Redis read/write test passed")
        else:
            print("⚠️  Redis read/write test failed")

        # Clean up
        client.delete(test_key)

        return True

    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("ℹ️  System will run in no-cache mode")
        return False


def test_embedding_service():
    """Test embedding service"""
    print("\n" + "=" * 50)
    print("🔍 Testing Embedding Service")
    print("=" * 50)

    print(f"\nEMBEDDING_MODEL: {EMBEDDING_MODEL}")

    try:
        from src.services.embedding_service import EmbeddingService

        service = EmbeddingService()
        print("✅ Embedding service initialized")
        print(f"📊 Model: {service.model_name}")
        print(f"📊 Device: {service.device}")

        # Test embedding
        test_text = "Đại học Kinh tế Quốc dân tuyển sinh năm 2024"
        embedding = service.create_embedding(test_text)

        if embedding is not None and len(embedding) > 0:
            print(f"✅ Embedding test passed (dimension: {len(embedding)})")
            return True
        else:
            print("❌ Embedding test failed")
            return False

    except Exception as e:
        print(f"❌ Embedding service failed: {e}")
        return False


def test_llm_config():
    """Test LLM configuration"""
    print("\n" + "=" * 50)
    print("🔍 Testing LLM Configuration")
    print("=" * 50)

    print(f"\nLLM_PROVIDER: {LLM_PROVIDER}")

    if LLM_PROVIDER == "gemini":
        if GEMINI_API_KEY:
            print(f"✅ GEMINI_API_KEY is set ({GEMINI_API_KEY[:10]}...)")
            return True
        else:
            print("❌ GEMINI_API_KEY is not set")
            return False
    elif LLM_PROVIDER == "ollama":
        print("ℹ️  Using Ollama (local)")
        return True
    else:
        print(f"⚠️  Unknown LLM_PROVIDER: {LLM_PROVIDER}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚂 RAILWAY DEPLOYMENT CONFIGURATION TEST")
    print("=" * 60)

    results = {
        "Database URL Format": test_database_url(),
        "PostgreSQL Connection": test_postgres_connection(),
        "Redis Configuration": test_redis_config(),
        "Redis Connection": test_redis_connection(),
        "LLM Configuration": test_llm_config(),
        "Embedding Service": test_embedding_service(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! Ready to deploy.")
        return 0
    elif passed >= total - 1:
        print("⚠️  Most tests passed. Check warnings above.")
        return 0
    else:
        print("❌ Some critical tests failed. Fix issues before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
