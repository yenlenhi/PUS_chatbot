# ✅ Vector Dimension Fix - Summary

## 📌 Problem Solved

**Error:** `different vector dimensions 768 and 384`

**Root Cause:** Mismatch between embedding model output dimension and database schema.

## 🎯 Solution Implemented

### 1. Made Embedding Dimension Configurable

**Updated Files:**
- [config/settings.py](config/settings.py) - Added `EMBEDDING_DIMENSION` setting
- [src/services/postgres_database_service.py](src/services/postgres_database_service.py) - Uses dynamic dimension
- [src/services/memory_service.py](src/services/memory_service.py) - Uses dynamic dimension

**New Environment Variable:**
```env
EMBEDDING_DIMENSION=384  # or 768
```

### 2. Created Helper Scripts

**[scripts/check_vector_dimension.py](scripts/check_vector_dimension.py)**
- Diagnoses dimension mismatches
- Shows current model and database dimensions
- Provides recommendations

**[scripts/fix_vector_dimension.py](scripts/fix_vector_dimension.py)**
- Migrates database between 384 and 768 dimensions
- Interactive menu to choose target dimension
- Creates backups before migration

### 3. Created Documentation

**[VECTOR_DIMENSION_FIX.md](VECTOR_DIMENSION_FIX.md)**
- Comprehensive fix guide with all options
- Step-by-step instructions
- Model dimension reference table

**[RAILWAY_VECTOR_FIX_QUICK.md](RAILWAY_VECTOR_FIX_QUICK.md)**
- Quick 5-minute fix for Railway
- Emergency solution steps
- Troubleshooting guide

**[.env.embedding.template](.env.embedding.template)**
- Template for embedding configuration
- Model comparison table
- Railway deployment notes

## 🚀 How to Fix on Railway (Choose One)

### Option A: Quick Fix (5 minutes) ⚡

Use 384-dimensional model (matches current database):

1. **Set environment variable on Railway:**
   ```
   EMBEDDING_MODEL=keepitreal/vietnamese-sbert
   EMBEDDING_DIMENSION=384
   ```

2. **Redeploy** (Railway auto-deploys on env change)

3. **Rebuild embeddings:**
   ```bash
   railway run python scripts/build_embeddings.py
   ```

**Status:** ✅ Ready to use immediately

---

### Option B: Better Quality (20 minutes) 🎯

Use 768-dimensional model (better Vietnamese accuracy):

1. **Run locally (with Railway DATABASE_URL):**
   ```bash
   export DATABASE_URL="<railway-postgres-url>"
   python scripts/fix_vector_dimension.py
   # Choose option 1 (768 dimensions)
   ```

2. **Commit code changes:**
   ```bash
   git add .
   git commit -m "Update to 768-dim embeddings"
   git push
   ```

3. **Set environment variables on Railway:**
   ```
   EMBEDDING_MODEL=hiieu/halong_embedding
   EMBEDDING_DIMENSION=768
   ```

4. **Rebuild embeddings:**
   ```bash
   railway run python scripts/build_embeddings.py
   ```

**Status:** ✅ Better accuracy, requires Railway Developer plan

---

## 📊 Model Reference

| Model | Dimensions | Language | Railway Plan | Setup Time |
|-------|------------|----------|--------------|------------|
| `keepitreal/vietnamese-sbert` | 384 | Vietnamese | Starter ✅ | 5 min |
| `hiieu/halong_embedding` | 768 | Vietnamese | Developer+ 💰 | 20 min |
| `bkai-foundation-models/vietnamese-embedding-v1` | 768 | Vietnamese | Developer+ 💰 | 20 min |
| `all-MiniLM-L6-v2` | 384 | English | Starter ✅ | 5 min |

## ✅ Verification

After applying the fix:

```bash
# Check dimensions match
python scripts/check_vector_dimension.py

# Should output:
# ✅ Dimensions match! (384D) or (768D)
```

Test the API:

```bash
curl -X POST https://your-app.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test query", "session_id": "test"}'
```

Should return response without dimension errors.

## 🔧 Maintenance Commands

**Diagnose issues:**
```bash
python scripts/check_vector_dimension.py
```

**Migrate dimensions:**
```bash
python scripts/fix_vector_dimension.py
```

**Rebuild embeddings:**
```bash
python scripts/build_embeddings.py
```

**Check database schema:**
```sql
SELECT 
    pg_catalog.format_type(atttypid, atttypmod) as column_type
FROM pg_attribute 
WHERE attrelid = 'embeddings'::regclass 
AND attname = 'embedding';
```

## 🆘 Troubleshooting

### Still seeing dimension errors?

1. **Check environment variables:**
   ```bash
   echo $EMBEDDING_MODEL
   echo $EMBEDDING_DIMENSION
   ```

2. **Verify model dimension:**
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer(os.getenv('EMBEDDING_MODEL'))
   emb = model.encode("test")
   print(f"Model produces: {len(emb)} dimensions")
   ```

3. **Verify database dimension:**
   ```sql
   SELECT vector_dims(embedding) FROM embeddings LIMIT 1;
   ```

4. **If dimensions don't match:**
   - Run `python scripts/fix_vector_dimension.py`
   - Choose the correct target dimension
   - Rebuild embeddings

### Model not found?

Some models need Hugging Face token:

```env
HF_TOKEN=your_huggingface_token
```

### Out of memory?

- Use 384-dimensional model (less memory)
- Or upgrade Railway plan

## 📝 Next Steps

1. ✅ Choose your preferred option (A or B above)
2. ✅ Apply the fix on Railway
3. ✅ Verify with test query
4. ✅ Monitor logs for any errors
5. ✅ Update documentation if needed

## 📚 Related Files

- [VECTOR_DIMENSION_FIX.md](VECTOR_DIMENSION_FIX.md) - Detailed guide
- [RAILWAY_VECTOR_FIX_QUICK.md](RAILWAY_VECTOR_FIX_QUICK.md) - Quick reference
- [.env.embedding.template](.env.embedding.template) - Configuration template
- [scripts/check_vector_dimension.py](scripts/check_vector_dimension.py) - Diagnostic tool
- [scripts/fix_vector_dimension.py](scripts/fix_vector_dimension.py) - Migration tool

---

**Status:** ✅ All fixes implemented and documented  
**Date:** 2025-12-25  
**Tested:** Yes, code changes verified
