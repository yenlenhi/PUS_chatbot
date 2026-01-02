"""
Fix analytics tables schema for Supabase
Adds missing columns to various analytics tables
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config import settings


def fix_query_document_coverage():
    """Fix query_document_coverage table - add missing columns"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n🔧 Fixing query_document_coverage table...")
        
        # Add missing columns
        columns_to_add = [
            ("relevance_scores", "FLOAT[]"),
            ("has_good_answer", "BOOLEAN DEFAULT TRUE"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE query_document_coverage ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                conn.commit()
                print(f"   ✅ Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"   ⏭️ Column {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")


def fix_access_logs():
    """Fix access_logs table - add missing columns"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n🔧 Fixing access_logs table...")
        
        columns_to_add = [
            ("session_id", "VARCHAR(255)"),
            ("is_blocked", "BOOLEAN DEFAULT FALSE"),
            ("block_reason", "TEXT"),
            ("response_time_ms", "FLOAT"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE access_logs ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                conn.commit()
                print(f"   ✅ Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"   ⏭️ Column {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")


def fix_document_history():
    """Fix document_history table - add missing columns"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n🔧 Fixing document_history table...")
        
        columns_to_add = [
            ("file_size", "BIGINT DEFAULT 0"),
            ("chunk_count", "INTEGER DEFAULT 0"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE document_history ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                conn.commit()
                print(f"   ✅ Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"   ⏭️ Column {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")


def fix_user_sessions():
    """Fix user_sessions table - add missing columns"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n🔧 Fixing user_sessions table...")
        
        columns_to_add = [
            ("last_visit", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("is_new_user", "BOOLEAN DEFAULT TRUE"),
            ("total_queries", "INTEGER DEFAULT 0"),
            ("total_time_seconds", "INTEGER DEFAULT 0"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                conn.commit()
                print(f"   ✅ Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"   ⏭️ Column {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")
        
        # Update last_visit from last_active if exists
        try:
            conn.execute(text("UPDATE user_sessions SET last_visit = last_active WHERE last_visit IS NULL AND last_active IS NOT NULL"))
            conn.commit()
            print("   ✅ Migrated last_active to last_visit")
        except Exception as e:
            print(f"   ⚠️ Could not migrate last_active: {e}")


def fix_token_usage():
    """Fix token_usage table - add missing columns"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n🔧 Fixing token_usage table...")
        
        columns_to_add = [
            ("estimated_cost", "FLOAT DEFAULT 0.0"),
            ("session_id", "VARCHAR(255)"),
            ("query_type", "VARCHAR(50)"),
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE token_usage ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                conn.commit()
                print(f"   ✅ Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"   ⏭️ Column {col_name} already exists")
                else:
                    print(f"   ❌ Error adding {col_name}: {e}")


def verify_all_tables():
    """Verify all tables have correct schema"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n📋 Verifying all tables...")
        
        tables = ['query_document_coverage', 'access_logs', 'document_history', 'user_sessions', 'token_usage']
        
        for table in tables:
            result = conn.execute(text(f"""
                SELECT column_name
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """))
            cols = [row[0] for row in result.fetchall()]
            print(f"\n   {table}: {', '.join(cols)}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Fixing Analytics Tables Schema for Supabase")
    print("=" * 60)
    
    try:
        fix_query_document_coverage()
        fix_access_logs()
        fix_document_history()
        fix_user_sessions()
        fix_token_usage()
        verify_all_tables()
        
        print("\n" + "=" * 60)
        print("✅ All analytics tables fixed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
