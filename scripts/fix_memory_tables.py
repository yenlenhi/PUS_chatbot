"""
Script to completely fix memory tables schema in Supabase
"""

import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:tinhyeumaunang123@db.thessjemstjljfbkvzih.supabase.co:5432/postgres"
)
conn.autocommit = True
cur = conn.cursor()

print("=== Fixing Memory Tables Schema ===\n")

# Drop and recreate memory_summaries
print("1. Dropping memory_summaries table...")
cur.execute("DROP TABLE IF EXISTS memory_summaries CASCADE")
print("   ✅ Dropped")

print("2. Creating memory_summaries with correct schema...")
cur.execute(
    """
    CREATE TABLE memory_summaries (
        id SERIAL PRIMARY KEY,
        conversation_id VARCHAR(255) NOT NULL,
        summary TEXT NOT NULL,
        turn_start INTEGER NOT NULL,
        turn_end INTEGER NOT NULL,
        embedding vector(384),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)
cur.execute(
    "CREATE INDEX idx_memory_summaries_conv_id ON memory_summaries(conversation_id)"
)
print("   ✅ Created memory_summaries")

# Verify conversation_memory has all columns
print("\n3. Verifying conversation_memory columns...")
cur.execute(
    "SELECT column_name FROM information_schema.columns WHERE table_name = 'conversation_memory'"
)
cols = [c[0] for c in cur.fetchall()]
print(f"   Current columns: {cols}")

required_cols = [
    "conversation_id",
    "role",
    "content",
    "turn_number",
    "timestamp",
    "metadata",
]
missing = [c for c in required_cols if c not in cols]

if missing:
    print(f"   Missing columns: {missing}")
    print("   Dropping and recreating...")
    cur.execute("DROP TABLE IF EXISTS conversation_memory CASCADE")
    cur.execute(
        """
        CREATE TABLE conversation_memory (
            id SERIAL PRIMARY KEY,
            conversation_id VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            turn_number INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB DEFAULT '{}'::jsonb
        )
    """
    )
    cur.execute(
        "CREATE INDEX idx_conv_memory_conv_id ON conversation_memory(conversation_id)"
    )
    cur.execute(
        "CREATE INDEX idx_conv_memory_turn ON conversation_memory(conversation_id, turn_number)"
    )
    print("   ✅ Recreated conversation_memory")
else:
    print("   ✓ All required columns present")

conn.close()
print("\n✅ Memory tables fix completed!")
