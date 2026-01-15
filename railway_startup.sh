#!/bin/bash

# ============================================
# Railway Startup Script
# ============================================
# Automatically initializes database and starts the application
# This script is called by Railway's startCommand in railway.json

set -e  # Exit on error

echo "=========================================="
echo "🚂 Railway Startup Script"
echo "=========================================="

# ============================================
# 1. Environment Check
# ============================================
echo ""
echo "[Step 1/5] Checking environment variables..."

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    echo "⚠️  WARNING: SUPABASE_URL is not set (image upload will fail)"
fi

if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "your-secret-key-change-this-in-production-use-openssl-rand-hex-32" ]; then
    echo "⚠️  WARNING: Using default JWT_SECRET_KEY! Generate a secure key!"
fi

echo "✅ Environment variables loaded"

# ============================================
# 2. Database Connection Test
# ============================================
echo ""
echo "[Step 2/5] Testing database connection..."

python3 -c "
import sys
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        version = result.fetchone()[0]
        print(f'✅ PostgreSQL connected: {version[:50]}...')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Exiting..."
    exit 1
fi

# ============================================
# 3. Database Initialization
# ============================================
echo ""
echo "[Step 3/5] Initializing database (users & roles)..."

# Check if users table exists
TABLE_EXISTS=$(python3 -c "
from sqlalchemy import create_engine, text, inspect
from config.settings import DATABASE_URL
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)
print('users' in inspector.get_table_names())
" 2>/dev/null)

if [ "$TABLE_EXISTS" = "True" ]; then
    echo "✅ Users table already exists, skipping initialization"
else
    echo "📦 Creating users table and default accounts..."
    python3 scripts/init_user_database.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Database initialized successfully"
    else
        echo "⚠️  Database initialization had warnings (check logs)"
    fi
fi

# ============================================
# 4. Embeddings Check
# ============================================
echo ""
echo "[Step 4/5] Checking embeddings..."

EMBEDDINGS_DIR="${RAILWAY_VOLUME_MOUNT:-/data}/embeddings"
FAISS_INDEX="$EMBEDDINGS_DIR/faiss_index.index"

if [ -f "$FAISS_INDEX" ]; then
    echo "✅ FAISS index found: $FAISS_INDEX"
    
    # Get vector count
    VECTOR_COUNT=$(python3 -c "
import faiss
index = faiss.read_index('$FAISS_INDEX')
print(index.ntotal)
" 2>/dev/null || echo "0")
    
    echo "📊 Vector count: $VECTOR_COUNT"
    
    if [ "$VECTOR_COUNT" -eq 0 ]; then
        echo "⚠️  FAISS index is empty. Upload PDFs and rebuild embeddings."
    fi
else
    echo "⚠️  FAISS index not found. Building from PDFs..."
    
    # Check if PDFs exist
    PDF_DIR="${RAILWAY_VOLUME_MOUNT:-/data}/pdfs"
    PDF_COUNT=$(find "$PDF_DIR" -name "*.pdf" 2>/dev/null | wc -l)
    
    if [ "$PDF_COUNT" -gt 0 ]; then
        echo "📄 Found $PDF_COUNT PDFs. Building embeddings..."
        python3 scripts/build_embeddings.py
        
        if [ $? -eq 0 ]; then
            echo "✅ Embeddings built successfully"
        else
            echo "❌ Failed to build embeddings"
            echo "⚠️  Continuing with empty index (upload PDFs later)"
        fi
    else
        echo "⚠️  No PDFs found in $PDF_DIR"
        echo "📝 Upload PDFs via API: POST /api/admin/upload"
        echo "🔧 Then rebuild: POST /api/admin/rebuild-embeddings"
    fi
fi

# ============================================
# 5. Start Application
# ============================================
echo ""
echo "[Step 5/5] Starting FastAPI server..."
echo "=========================================="
echo ""

# Railway automatically sets PORT environment variable
# Default to 8000 if not set (for local testing)
PORT="${PORT:-8000}"

exec python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --log-level info \
    --no-access-log

# Note: exec replaces the shell process with uvicorn
# This ensures proper signal handling for Railway restarts
