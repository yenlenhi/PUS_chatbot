# 🔧 Vector Dimension Mismatch Fix Guide

## 🚨 Problem

```
ERROR: different vector dimensions 768 and 384
```

**Root Cause:** The database schema was created for 384-dimensional embeddings, but the current embedding model (`hiieu/halong_embedding`) produces 768-dimensional vectors.

## 📊 Current State

| Component | Dimension | Model |
|-----------|-----------|-------|
| **Local .env** | 768 | `hiieu/halong_embedding` |
| **Database Schema** | 384 | Created for `all-MiniLM-L6-v2` or Vietnamese 384-dim model |
| **Railway (likely)** | Mixed | Fallback to `all-MiniLM-L6-v2` (384-dim) |

## ✅ Solution Options

### **Option 1: Update Database to 768 Dimensions (Recommended)**

This option keeps your current embedding model and updates the database schema.

#### Step 1: Check Current Vector Dimension

```sql
-- Connect to Railway PostgreSQL
SELECT 
    table_name,
    column_name,
    udt_name,
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'embeddings' AND column_name = 'embedding';
```

#### Step 2: Drop and Recreate Embeddings Table

**⚠️ WARNING:** This will delete all existing embeddings!

```sql
-- Backup existing data first (optional)
CREATE TABLE embeddings_backup AS SELECT * FROM embeddings;

-- Drop the table
DROP TABLE IF EXISTS embeddings CASCADE;

-- Recreate with 768 dimensions
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL,
    embedding vector(768),  -- Changed from 384 to 768
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
    UNIQUE(chunk_id)
);

-- Create index for faster similarity search
CREATE INDEX idx_embeddings_vector ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

#### Step 3: Update Database Service Code

Update [src/services/postgres_database_service.py](src/services/postgres_database_service.py#L110):

```python
# Change line 110 from:
embedding vector(384),

# To:
embedding vector(768),
```

Also update [src/services/memory_service.py](src/services/memory_service.py#L90):

```python
# Change line 90 from:
embedding vector(384),

# To:
embedding vector(768),
```

#### Step 4: Rebuild All Embeddings

```bash
# Rebuild embeddings with the new 768-dimensional model
python scripts/build_embeddings.py
```

---

### **Option 2: Use 384-Dimensional Model (Faster)**

This option changes the embedding model to match the existing database schema.

#### Step 1: Update Environment Variable

**Local `.env`:**
```env
# Change from:
# EMBEDDING_MODEL=hiieu/halong_embedding

# To one of these 384-dimensional models:
EMBEDDING_MODEL=keepitreal/vietnamese-sbert  # Vietnamese, 384-dim
# OR
EMBEDDING_MODEL=all-MiniLM-L6-v2  # English, 384-dim, faster
```

**Railway Environment Variables:**
1. Go to Railway Dashboard → Your Service → Variables
2. Set or update:
   ```
   EMBEDDING_MODEL=keepitreal/vietnamese-sbert
   ```

#### Step 2: Verify Model Dimensions

```python
# Test script to check model dimensions
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("keepitreal/vietnamese-sbert")
test_embedding = model.encode("test text")
print(f"Embedding dimension: {len(test_embedding)}")
# Should output: Embedding dimension: 384
```

#### Step 3: Rebuild Embeddings (if needed)

If your existing embeddings were created with a different model:

```bash
python scripts/build_embeddings.py
```

---

## 🔍 Model Dimension Reference

| Model | Dimensions | Language | Speed | Accuracy |
|-------|------------|----------|-------|----------|
| `hiieu/halong_embedding` | **768** | Vietnamese | Slower | Higher |
| `bkai-foundation-models/vietnamese-embedding-v1` | **768** | Vietnamese | Slower | Higher |
| `keepitreal/vietnamese-sbert` | **384** | Vietnamese | Faster | Good |
| `all-MiniLM-L6-v2` | **384** | English | Fastest | Good |

---

## 🚀 Recommended Approach

### For **Production (Railway)**:

**Use Option 1 (768 dimensions)** for better Vietnamese accuracy:

1. **Update database schema** to `vector(768)`
2. **Set environment variable**: `EMBEDDING_MODEL=hiieu/halong_embedding`
3. **Rebuild embeddings** from scratch
4. **Verify** with a test query

### For **Development/Testing**:

**Use Option 2 (384 dimensions)** for faster iteration:

1. **Keep database schema** at `vector(384)`
2. **Set environment variable**: `EMBEDDING_MODEL=keepitreal/vietnamese-sbert`
3. **Rebuild embeddings** if needed

---

## 📝 Step-by-Step Fix for Railway

### 1. Connect to Railway PostgreSQL

```bash
# Get connection string from Railway Dashboard
railway connect postgres
```

Or use `psql`:

```bash
psql "postgresql://postgres:...@...railway.app:5432/railway"
```

### 2. Check Current Schema

```sql
\d embeddings
```

Look for the `embedding` column type (e.g., `vector(384)` or `vector(768)`).

### 3. Apply Fix (Choose Option 1 or 2 above)

If using **Option 1** (recommended):
- Run SQL commands to recreate table with `vector(768)`
- Update code files
- Rebuild embeddings

If using **Option 2** (faster):
- Update `EMBEDDING_MODEL` environment variable
- Rebuild embeddings if necessary

### 4. Update Code Files

Update these files if using Option 1 (768-dim):

```bash
# Update database service
# File: src/services/postgres_database_service.py
# Line 110: embedding vector(768),

# Update memory service  
# File: src/services/memory_service.py
# Line 90: embedding vector(768),
```

### 5. Rebuild Embeddings

```bash
# On Railway or locally with Railway DATABASE_URL
python scripts/build_embeddings.py
```

### 6. Verify Fix

```python
# Test the fix
import os
os.environ['DATABASE_URL'] = 'postgresql://...'  # Your Railway URL

from src.services.embedding_service import EmbeddingService
from src.services.postgres_database_service import PostgresDatabaseService

# Check embedding dimension
embedding_service = EmbeddingService()
test_embedding = embedding_service.create_embedding("Test query")
print(f"Query embedding dimension: {len(test_embedding)}")

# Check database
db_service = PostgresDatabaseService()
result = db_service.session.execute("SELECT vector_dims(embedding) FROM embeddings LIMIT 1;")
db_dim = result.scalar()
print(f"Database vector dimension: {db_dim}")

# Should match!
assert len(test_embedding) == db_dim, "Dimension mismatch!"
print("✅ Dimensions match!")
```

---

## 🔄 Migration Script

Create [scripts/fix_vector_dimension.py](scripts/fix_vector_dimension.py):

```python
"""
Script to migrate embeddings table from 384 to 768 dimensions
"""
import os
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

def migrate_to_768_dimensions():
    """Migrate embeddings table to 768 dimensions"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("🔄 Starting migration...")
        
        # Backup existing table
        print("📦 Creating backup...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS embeddings_backup_384 AS 
            SELECT * FROM embeddings;
        """))
        conn.commit()
        
        # Drop existing table
        print("🗑️ Dropping old table...")
        conn.execute(text("DROP TABLE IF EXISTS embeddings CASCADE;"))
        conn.commit()
        
        # Create new table with 768 dimensions
        print("✨ Creating new table with 768 dimensions...")
        conn.execute(text("""
            CREATE TABLE embeddings (
                id SERIAL PRIMARY KEY,
                chunk_id INTEGER NOT NULL,
                embedding vector(768),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
                UNIQUE(chunk_id)
            );
        """))
        conn.commit()
        
        # Create index
        print("🔍 Creating vector index...")
        conn.execute(text("""
            CREATE INDEX idx_embeddings_vector ON embeddings 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """))
        conn.commit()
        
        print("✅ Migration complete!")
        print("⚠️ Remember to rebuild embeddings: python scripts/build_embeddings.py")

if __name__ == "__main__":
    migrate_to_768_dimensions()
```

Run it:

```bash
# Set Railway DATABASE_URL
export DATABASE_URL="postgresql://..."
# or PowerShell:
# $env:DATABASE_URL = "postgresql://..."

python scripts/fix_vector_dimension.py
```

---

## ✅ Verification Checklist

After applying the fix:

- [ ] Database schema shows `vector(768)` (or `vector(384)` if using Option 2)
- [ ] Environment variable `EMBEDDING_MODEL` set correctly
- [ ] Test embedding creation works without errors
- [ ] Embeddings table has data
- [ ] Query search works without dimension errors
- [ ] Railway deployment logs show no errors

---

## 🆘 Troubleshooting

### Error: "pgvector extension not found"

```sql
-- Run in PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;
```

### Error: "Cannot create index on empty table"

This is fine - the index will be populated when you add embeddings.

### Error: "Out of memory" when rebuilding

- Build embeddings in smaller batches
- Or use Railway's larger plan
- Or use the 384-dimensional model (smaller memory footprint)

### Embeddings not found after migration

Make sure to run:

```bash
python scripts/build_embeddings.py
```

---

## 📚 Related Files

- [config/settings.py](config/settings.py#L120) - `EMBEDDING_MODEL` configuration
- [src/services/postgres_database_service.py](src/services/postgres_database_service.py#L110) - Database schema
- [src/services/embedding_service.py](src/services/embedding_service.py) - Embedding generation
- [src/services/hybrid_retrieval_service.py](src/services/hybrid_retrieval_service.py#L117) - Where the error occurs
- [scripts/build_embeddings.py](scripts/build_embeddings.py) - Rebuild embeddings script

---

## 🎯 Quick Fix Summary

**For immediate fix on Railway:**

```bash
# 1. Set correct model (384-dim)
EMBEDDING_MODEL=keepitreal/vietnamese-sbert

# 2. Redeploy
git push

# 3. Rebuild embeddings (if needed)
railway run python scripts/build_embeddings.py
```

**For long-term solution:**

1. Update database schema to `vector(768)`
2. Use `hiieu/halong_embedding` model
3. Rebuild all embeddings
4. Better Vietnamese accuracy

---

**Last Updated:** 2025-12-25
