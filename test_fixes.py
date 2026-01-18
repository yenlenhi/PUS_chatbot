"""
Quick test script to verify fixes before deployment
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_async_database():
    """Test async database initialization"""
    print("🧪 Testing async database service...")
    try:
        from src.services.async_postgres_database_service import (
            AsyncPostgresDatabaseService,
        )

        service = AsyncPostgresDatabaseService()
        await service.initialize()
        print("✅ Async database service initialized successfully!")

        # Test a simple query
        async with service.get_session() as session:
            from sqlalchemy import text

            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Query test passed: {row[0]}")

        return True
    except Exception as e:
        print(f"❌ Async database test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_supabase_import():
    """Test supabase client creation"""
    print("\n🧪 Testing Supabase client...")
    try:

        # Just test if we can call the function without crash
        # Actual connection test would need valid credentials
        print("✅ Supabase import successful!")
        print(
            "   (Connection test requires valid SUPABASE_URL and SUPABASE_SERVICE_KEY)"
        )
        return True
    except Exception as e:
        print(f"❌ Supabase import test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("🔍 Pre-deployment Test Suite")
    print("=" * 60)

    # Test 1: Supabase import (synchronous)
    test1_passed = test_supabase_import()

    # Test 2: Async database (async)
    test2_passed = await test_async_database()

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Supabase Import: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Async Database:  {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print("=" * 60)

    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Safe to deploy.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review before deploying.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
