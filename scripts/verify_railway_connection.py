"""
Database connection verification script for Railway + Supabase deployment
Run this to test your DATABASE_URL before deploying
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, inspect
from config.settings import DATABASE_URL, SUPABASE_URL


def verify_database_connection():
    """Verify PostgreSQL database connection and configuration"""

    print("=" * 70)
    print("🔍 Railway + Supabase Database Connection Verification")
    print("=" * 70)

    # Check environment variables
    print("\n[1/5] Checking environment variables...")

    if not DATABASE_URL:
        print("❌ DATABASE_URL is not set!")
        return False

    # Mask password in output
    masked_url = DATABASE_URL
    if "@" in masked_url:
        parts = masked_url.split("@")
        user_pass = parts[0].split("://")[1]
        if ":" in user_pass:
            user, _ = user_pass.split(":", 1)
            masked_url = masked_url.replace(user_pass, f"{user}:****")

    print(f"✅ DATABASE_URL: {masked_url}")

    if SUPABASE_URL:
        print(f"✅ SUPABASE_URL: {SUPABASE_URL}")
    else:
        print("⚠️  SUPABASE_URL not set (image uploads won't work)")

    # Test connection
    print("\n[2/5] Testing database connection...")

    try:
        engine = create_engine(
            DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10
        )

        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("✅ Connected to PostgreSQL")
            print(f"   Version: {version[:80]}...")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    # Check pgvector extension
    print("\n[3/5] Checking pgvector extension...")

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
            )
            extension = result.fetchone()

            if extension:
                print("✅ pgvector extension available")
                print(
                    f"   Version: {extension[1] if extension[1] else 'Not installed yet'}"
                )

                # Check if installed
                result = conn.execute(
                    text("SELECT * FROM pg_extension WHERE extname = 'vector'")
                )
                installed = result.fetchone()

                if installed:
                    print("✅ pgvector extension is INSTALLED")
                else:
                    print("⚠️  pgvector extension NOT installed yet")
                    print("   Run this in Supabase SQL Editor:")
                    print("   CREATE EXTENSION IF NOT EXISTS vector;")
            else:
                print("❌ pgvector extension not available")
                print("   Make sure you're using Supabase PostgreSQL")
                return False

    except Exception as e:
        print(f"⚠️  Could not check pgvector: {e}")

    # Check existing tables
    print("\n[4/5] Checking existing tables...")

    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if tables:
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                row_count = "?"
                try:
                    with engine.connect() as conn:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        row_count = result.fetchone()[0]
                except:
                    pass
                print(f"   - {table} ({row_count} rows)")
        else:
            print("⚠️  No tables found (database is empty)")
            print("   Run: python scripts/init_user_database.py")

    except Exception as e:
        print(f"⚠️  Could not list tables: {e}")

    # Test write permission
    print("\n[5/5] Testing write permissions...")

    try:
        with engine.connect() as conn:
            # Create test table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS _connection_test (
                    id SERIAL PRIMARY KEY,
                    test_data TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """
                )
            )
            conn.commit()

            # Insert test data
            conn.execute(
                text(
                    """
                INSERT INTO _connection_test (test_data) 
                VALUES ('Railway deployment test')
            """
                )
            )
            conn.commit()

            # Read test data
            result = conn.execute(text("SELECT * FROM _connection_test LIMIT 1"))
            test_row = result.fetchone()

            # Clean up
            conn.execute(text("DROP TABLE _connection_test"))
            conn.commit()

            print("✅ Write permissions verified")
            print(f"   Test data: {test_row[1]}")

    except Exception as e:
        print(f"❌ Write test failed: {e}")
        return False

    # Final summary
    print("\n" + "=" * 70)
    print("✅ DATABASE CONNECTION VERIFICATION COMPLETE")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print("   1. If pgvector not installed: CREATE EXTENSION IF NOT EXISTS vector;")
    print("   2. Initialize database: python scripts/init_user_database.py")
    print("   3. Deploy to Railway and check logs")
    print("   4. Test health endpoint: curl https://your-app.railway.app/health")
    print("\n" + "=" * 70)

    return True


if __name__ == "__main__":
    try:
        success = verify_database_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
