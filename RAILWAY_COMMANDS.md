# 🚀 Railway Fix Commands - Copy & Paste

## 🔴 CURRENT ERROR
```
ERROR: different vector dimensions 768 and 384
```

---

## ⚡ QUICK FIX (Recommended - 5 minutes)

### Step 1: Set Railway Environment Variables

Go to **Railway Dashboard → Your Service → Variables** and add/update:

```
EMBEDDING_MODEL=keepitreal/vietnamese-sbert
EMBEDDING_DIMENSION=384
```

### Step 2: Railway will auto-redeploy

Wait for deployment to complete (~2-3 minutes)

### Step 3: Rebuild Embeddings

Option A - Via Railway CLI:
```bash
railway run python scripts/build_embeddings.py
```

Option B - Via Railway Shell:
```bash
# Open Railway shell
railway shell

# Then run:
python scripts/build_embeddings.py
```

### Step 4: Verify Fix

Test the API:
```bash
curl -X POST https://your-railway-url.up.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quy định thi là gì?", "session_id": "test"}'
```

**✅ Done! Error should be fixed.**

---

## 🎯 ALTERNATIVE: Better Quality (768-dim)

If you want higher accuracy and have Railway Developer plan:

### Step 1: Migrate Database Locally

```bash
# Get Railway PostgreSQL URL from dashboard
export DATABASE_URL="postgresql://postgres:password@host:port/railway"

# Run migration script
python scripts/fix_vector_dimension.py

# Choose option 1 (768 dimensions)
```

### Step 2: Commit Changes

```bash
git add .
git commit -m "Fix: Update to 768-dimensional embeddings"
git push
```

### Step 3: Update Railway Variables

```
EMBEDDING_MODEL=hiieu/halong_embedding
EMBEDDING_DIMENSION=768
```

### Step 4: Rebuild Embeddings

```bash
railway run python scripts/build_embeddings.py
```

---

## 🔍 DIAGNOSTIC COMMANDS

### Check Current State (Local)

```bash
# Check what dimensions your model produces
python -c "from sentence_transformers import SentenceTransformer; m=SentenceTransformer('keepitreal/vietnamese-sbert'); print(f'Dimension: {len(m.encode(\"test\"))}')"

# Check database dimension
python scripts/check_vector_dimension.py
```

### Check Database on Railway

```bash
# Connect to Railway PostgreSQL
railway connect postgres

# Then run this SQL:
SELECT 
    pg_catalog.format_type(atttypid, atttypmod) as column_type
FROM pg_attribute 
WHERE attrelid = 'embeddings'::regclass 
AND attname = 'embedding';

# Should show: vector(384) or vector(768)
```

---

## 📋 Railway Environment Variables (Complete List)

Copy these to Railway Dashboard → Variables:

```bash
# ============================================
# LLM Configuration
# ============================================
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# ============================================
# Embedding Configuration (REQUIRED)
# ============================================
# Option 1: 384-dim (Recommended for Starter plan)
EMBEDDING_MODEL=keepitreal/vietnamese-sbert
EMBEDDING_DIMENSION=384

# Option 2: 768-dim (For Developer plan)
# EMBEDDING_MODEL=hiieu/halong_embedding
# EMBEDDING_DIMENSION=768

# ============================================
# Database (Auto-configured by Railway)
# ============================================
# DATABASE_URL is automatically set by Railway PostgreSQL plugin
# No need to set manually

# ============================================
# Redis (Optional but recommended)
# ============================================
# REDIS_URL is automatically set if you add Redis plugin
ENABLE_REDIS_CACHE=true

# ============================================
# Optional Settings
# ============================================
LOG_LEVEL=INFO
TOP_K_RESULTS=15
SIMILARITY_THRESHOLD=0.35
DENSE_WEIGHT=0.7
```

---

## ⚠️ Important Notes

1. **EMBEDDING_DIMENSION must match your model:**
   - `keepitreal/vietnamese-sbert` → 384
   - `hiieu/halong_embedding` → 768

2. **If you change dimension, you MUST:**
   - Migrate database (run `fix_vector_dimension.py`)
   - OR rebuild database from scratch
   - Rebuild all embeddings

3. **Railway Starter Plan (512MB RAM):**
   - Use 384-dimensional models only
   - 768-dimensional models may cause OOM errors

4. **After any change:**
   - Always rebuild embeddings: `railway run python scripts/build_embeddings.py`

---

## 🆘 If Something Goes Wrong

### Error: "Model not found"

```bash
# Add Hugging Face token on Railway
HF_TOKEN=your_huggingface_token
```

### Error: "Out of memory"

- Use 384-dimensional model (Option 1)
- Or upgrade Railway plan to Developer

### Error: "Table already exists with different dimension"

```bash
# Connect to Railway PostgreSQL
railway connect postgres

# Drop and recreate table
DROP TABLE IF EXISTS embeddings CASCADE;
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL UNIQUE,
    embedding vector(384),  -- or 768
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
);

# Exit PostgreSQL
\q

# Rebuild embeddings
railway run python scripts/build_embeddings.py
```

### Still Having Issues?

1. Check Railway logs: `railway logs`
2. Check deployment status: Railway Dashboard
3. Verify environment variables: Railway Dashboard → Variables
4. Test locally first with Railway DATABASE_URL

---

## ✅ Verification Checklist

After applying the fix:

- [ ] Railway deployment successful (no errors in logs)
- [ ] Environment variables set correctly
- [ ] Embeddings rebuilt successfully
- [ ] Test API call returns valid response
- [ ] No dimension mismatch errors in logs

---

## 📚 Related Documentation

- [FIX_SUMMARY.md](FIX_SUMMARY.md) - Complete fix summary
- [RAILWAY_VECTOR_FIX_QUICK.md](RAILWAY_VECTOR_FIX_QUICK.md) - Quick reference
- [VECTOR_DIMENSION_FIX.md](VECTOR_DIMENSION_FIX.md) - Detailed guide
- [.env.embedding.template](.env.embedding.template) - Configuration examples

---

**Last Updated:** 2025-12-25  
**Status:** ✅ Ready to use
