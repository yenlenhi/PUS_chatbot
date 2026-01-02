"""
Script to fix Supabase database schema
"""

import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
)
conn.autocommit = True
cur = conn.cursor()

print("=== Fixing Supabase Schema ===\n")

# Check existing tables
cur.execute(
    """
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' ORDER BY table_name
"""
)
tables = [t[0] for t in cur.fetchall()]
print(f"Existing tables: {tables}\n")

# 1. Fix chunks table - add is_active
print("1. Checking chunks table...")
cur.execute(
    "SELECT column_name FROM information_schema.columns WHERE table_name = 'chunks'"
)
chunks_cols = [c[0] for c in cur.fetchall()]
print(f"   Columns: {chunks_cols}")
if "is_active" not in chunks_cols:
    cur.execute("ALTER TABLE chunks ADD COLUMN is_active BOOLEAN DEFAULT true")
    print("   ✅ Added is_active column")
else:
    print("   ✓ is_active already exists")

# 2. Fix/recreate conversation_memory table
print("\n2. Fixing conversation_memory table...")
if "conversation_memory" in tables:
    cur.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'conversation_memory'"
    )
    mem_cols = [c[0] for c in cur.fetchall()]
    print(f"   Current columns: {mem_cols}")

    if "conversation_id" not in mem_cols:
        print("   Dropping and recreating table...")
        cur.execute("DROP TABLE IF EXISTS conversation_memory CASCADE")
        cur.execute(
            """
            CREATE TABLE conversation_memory (
                id SERIAL PRIMARY KEY,
                conversation_id VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """
        )
        cur.execute(
            "CREATE INDEX idx_conv_memory_conv_id ON conversation_memory(conversation_id)"
        )
        cur.execute(
            "CREATE INDEX idx_conv_memory_timestamp ON conversation_memory(timestamp)"
        )
        print("   ✅ Recreated conversation_memory table")
else:
    print("   Creating new table...")
    cur.execute(
        """
        CREATE TABLE conversation_memory (
            id SERIAL PRIMARY KEY,
            conversation_id VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB DEFAULT '{}'::jsonb
        )
    """
    )
    cur.execute(
        "CREATE INDEX idx_conv_memory_conv_id ON conversation_memory(conversation_id)"
    )
    cur.execute(
        "CREATE INDEX idx_conv_memory_timestamp ON conversation_memory(timestamp)"
    )
    print("   ✅ Created conversation_memory table")

# 3. Fix/create query_document_coverage table
print("\n3. Fixing query_document_coverage table...")
if "query_document_coverage" in tables:
    cur.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'query_document_coverage'"
    )
    qdc_cols = [c[0] for c in cur.fetchall()]
    print(f"   Current columns: {qdc_cols}")

    if "topic" not in qdc_cols:
        print("   Dropping and recreating table...")
        cur.execute("DROP TABLE IF EXISTS query_document_coverage CASCADE")
        cur.execute(
            """
            CREATE TABLE query_document_coverage (
                id SERIAL PRIMARY KEY,
                query TEXT NOT NULL,
                topic VARCHAR(255),
                document_sources TEXT[],
                coverage_score FLOAT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        cur.execute(
            "CREATE INDEX idx_query_coverage_topic ON query_document_coverage(topic)"
        )
        print("   ✅ Recreated query_document_coverage table")
else:
    print("   Creating new table...")
    cur.execute(
        """
        CREATE TABLE query_document_coverage (
            id SERIAL PRIMARY KEY,
            query TEXT NOT NULL,
            topic VARCHAR(255),
            document_sources TEXT[],
            coverage_score FLOAT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cur.execute(
        "CREATE INDEX idx_query_coverage_topic ON query_document_coverage(topic)"
    )
    print("   ✅ Created query_document_coverage table")

# 4. Create chat_analytics if not exists
print("\n4. Checking chat_analytics table...")
if "chat_analytics" not in tables:
    cur.execute(
        """
        CREATE TABLE chat_analytics (
            id SERIAL PRIMARY KEY,
            conversation_id VARCHAR(255),
            query TEXT,
            response_time_ms INTEGER,
            confidence_score FLOAT,
            sources_count INTEGER DEFAULT 0,
            feedback_rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cur.execute("CREATE INDEX idx_chat_analytics_created ON chat_analytics(created_at)")
    print("   ✅ Created chat_analytics table")
else:
    print("   ✓ Already exists")

# 5. Create user_sessions if not exists
print("\n5. Checking user_sessions table...")
if "user_sessions" not in tables:
    cur.execute(
        """
        CREATE TABLE user_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_agent TEXT,
            ip_address VARCHAR(50),
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            messages_count INTEGER DEFAULT 0
        )
    """
    )
    cur.execute("CREATE INDEX idx_user_sessions_session ON user_sessions(session_id)")
    print("   ✅ Created user_sessions table")
else:
    print("   ✓ Already exists")

# Final verification
print("\n=== Final Verification ===")
cur.execute(
    """
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' ORDER BY table_name
"""
)
final_tables = [t[0] for t in cur.fetchall()]
print(f"All tables: {final_tables}")

conn.close()
print("\n✅ Schema fix completed!")
