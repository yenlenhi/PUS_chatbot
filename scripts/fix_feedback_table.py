"""
Fix feedback table schema - Change rating column from INTEGER to VARCHAR
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config import settings


def fix_feedback_table():
    """Fix the feedback table rating column type"""

    database_url = settings.DATABASE_URL
    print("🔗 Connecting to database...")
    print(f"   URL: {database_url[:50]}...")

    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Check current column type
        print("\n📋 Checking current feedback table schema...")
        result = conn.execute(
            text(
                """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'feedback'
            ORDER BY ordinal_position
        """
            )
        )

        columns = result.fetchall()
        if not columns:
            print("❌ Feedback table does not exist!")
            return False

        print("\nCurrent schema:")
        rating_type = None
        for col in columns:
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
            if col[0] == "rating":
                rating_type = col[1]

        if rating_type == "character varying":
            print("\n✅ Rating column is already VARCHAR. No fix needed!")
            return True

        print(f"\n⚠️ Rating column is currently: {rating_type}")
        print("   Need to change to VARCHAR(20)")

        # Check if there's any data
        result = conn.execute(text("SELECT COUNT(*) FROM feedback"))
        count = result.scalar()
        print(f"\n📊 Current feedback records: {count}")

        # Drop and recreate the feedback table with correct schema
        print("\n🔧 Recreating feedback table with correct schema...")

        # Create backup if data exists
        if count > 0:
            print("   Creating backup...")
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS feedback_backup AS 
                SELECT * FROM feedback
            """
                )
            )
            conn.commit()
            print("   ✅ Backup created as 'feedback_backup'")

        # Drop existing table
        print("   Dropping old table...")
        conn.execute(text("DROP TABLE IF EXISTS feedback CASCADE"))
        conn.commit()

        # Create new table with correct schema
        print("   Creating new table with VARCHAR rating...")
        conn.execute(
            text(
                """
            CREATE TABLE feedback (
                id SERIAL PRIMARY KEY,
                conversation_id VARCHAR(255) NOT NULL,
                message_id VARCHAR(255),
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                rating VARCHAR(20) NOT NULL,
                comment TEXT,
                chunk_ids INTEGER[] DEFAULT '{}',
                user_id VARCHAR(255),
                session_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )
        conn.commit()

        # Create indexes
        print("   Creating indexes...")
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_feedback_conversation 
            ON feedback(conversation_id)
        """
            )
        )
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_feedback_created_at 
            ON feedback(created_at)
        """
            )
        )
        conn.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_feedback_rating 
            ON feedback(rating)
        """
            )
        )
        conn.commit()

        print("\n✅ Feedback table recreated successfully!")

        # Verify new schema
        print("\n📋 Verifying new schema...")
        result = conn.execute(
            text(
                """
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'feedback'
            ORDER BY ordinal_position
        """
            )
        )

        for col in result.fetchall():
            print(f"   - {col[0]}: {col[1]}")

        return True


def fix_related_tables():
    """Fix chunk_performance and query_metrics tables"""

    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Fix chunk_performance table - drop and recreate with correct schema
        print("\n🔧 Fixing chunk_performance table...")
        conn.execute(text("DROP TABLE IF EXISTS chunk_performance CASCADE"))
        conn.commit()

        conn.execute(
            text(
                """
            CREATE TABLE chunk_performance (
                id SERIAL PRIMARY KEY,
                chunk_id INTEGER NOT NULL,
                times_used INTEGER DEFAULT 0,
                positive_feedback INTEGER DEFAULT 0,
                negative_feedback INTEGER DEFAULT 0,
                neutral_feedback INTEGER DEFAULT 0,
                effectiveness_score FLOAT DEFAULT 0.5,
                retrieval_weight FLOAT DEFAULT 1.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chunk_id)
            )
        """
            )
        )
        conn.commit()
        print("   ✅ chunk_performance table recreated with correct schema")

        # Fix query_metrics table - drop and recreate with correct schema
        print("\n🔧 Fixing query_metrics table...")
        conn.execute(text("DROP TABLE IF EXISTS query_metrics CASCADE"))
        conn.commit()

        conn.execute(
            text(
                """
            CREATE TABLE query_metrics (
                id SERIAL PRIMARY KEY,
                query TEXT NOT NULL,
                response_time_ms FLOAT,
                chunks_retrieved INTEGER,
                confidence_score FLOAT,
                has_feedback BOOLEAN DEFAULT FALSE,
                feedback_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )
        conn.commit()
        print("   ✅ query_metrics table recreated with correct schema")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Fixing Feedback Table Schema for Supabase")
    print("=" * 60)

    try:
        fix_feedback_table()
        fix_related_tables()
        print("\n" + "=" * 60)
        print("✅ All fixes completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
