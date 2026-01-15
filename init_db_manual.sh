#!/bin/sh

# Manual Database Initialization Script
# Run this AFTER the server is successfully deployed
# Usage: railway run sh init_db_manual.sh

set -e

echo "=========================================="
echo "📦 Manual Database Initialization"
echo "=========================================="

# Check environment
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    exit 1
fi

echo ""
echo "[Step 1/2] Testing database connection..."

python3 -c "
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    version = result.fetchone()[0]
    print(f'✅ Connected: {version[:60]}')
"

echo ""
echo "[Step 2/2] Creating users table..."

python3 scripts/init_user_database.py

echo ""
echo "✅ Database initialization complete!"
echo ""
echo "Default accounts:"
echo "  Admin: admin / Admin123"
echo "  User:  user / User1234"
echo ""
echo "⚠️  CHANGE THESE PASSWORDS IMMEDIATELY!"
