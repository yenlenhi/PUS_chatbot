"""
Migration script to add new columns to analytics tables
Run this once to update existing database schema
"""

from src.services.postgres_database_service import PostgresDatabaseService
from sqlalchemy import text


def migrate_user_sessions():
    """Add missing columns to user_sessions table"""
    db = PostgresDatabaseService()
    
    columns_to_add = [
        ("ip_address", "VARCHAR(50)"),
        ("user_agent", "TEXT"),
        ("total_likes", "INTEGER DEFAULT 0"),
        ("total_dislikes", "INTEGER DEFAULT 0"),
        ("user_segment", "VARCHAR(50) DEFAULT 'new'"),
    ]
    
    with db.engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"✅ Added column: {col_name}")
            except Exception as e:
                print(f"⚠️ Column {col_name}: {e}")
        
        conn.commit()
        print("✅ user_sessions migration completed!")


def create_new_tables():
    """Create new analytics tables if they don't exist"""
    db = PostgresDatabaseService()
    
    with db.engine.connect() as conn:
        # Create topic_classifications table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS topic_classifications (
                id SERIAL PRIMARY KEY,
                conversation_id VARCHAR(255),
                session_id VARCHAR(255),
                query TEXT NOT NULL,
                topic VARCHAR(100) NOT NULL,
                confidence FLOAT DEFAULT 0.0,
                keywords TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Created topic_classifications table")
        
        # Create unanswered_queries table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS unanswered_queries (
                id SERIAL PRIMARY KEY,
                conversation_id VARCHAR(255),
                session_id VARCHAR(255),
                query TEXT NOT NULL,
                response TEXT,
                reason VARCHAR(100),
                confidence FLOAT DEFAULT 0.0,
                retrieval_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Created unanswered_queries table")
        
        # Create document_history table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS document_history (
                id SERIAL PRIMARY KEY,
                document_name VARCHAR(500) NOT NULL,
                action VARCHAR(50) NOT NULL,
                file_size INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                category VARCHAR(100),
                previous_version VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Created document_history table")
        
        # Create query_document_coverage table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS query_document_coverage (
                id SERIAL PRIMARY KEY,
                query TEXT NOT NULL,
                topic VARCHAR(100),
                matched_documents TEXT[],
                coverage_score FLOAT DEFAULT 0.0,
                relevance_scores FLOAT[],
                has_good_answer BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Created query_document_coverage table")
        
        # Create indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_topic_class_topic ON topic_classifications(topic)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_topic_class_created ON topic_classifications(created_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_unanswered_created ON unanswered_queries(created_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_doc_history_created ON document_history(created_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_query_coverage_topic ON query_document_coverage(topic)"))
        print("✅ Created indexes")
        
        conn.commit()
        print("✅ All new tables created!")


def main():
    print("=" * 50)
    print("Analytics Tables Migration Script")
    print("=" * 50)
    
    print("\n1. Migrating user_sessions table...")
    migrate_user_sessions()
    
    print("\n2. Creating new analytics tables...")
    create_new_tables()
    
    print("\n" + "=" * 50)
    print("✅ Migration completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
