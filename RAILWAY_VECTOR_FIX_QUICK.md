# 🚨 QUICK FIX: Vector Dimension Mismatch on Railway

## The Problem

```
ERROR: different vector dimensions 768 and 384
```

**Your database schema was created for 384-dimensional vectors, but your embedding model produces 768-dimensional vectors.**

---

## ⚡ FASTEST FIX (2 Steps - 5 minutes)

### Step 1: Change Environment Variable on Railway

Go to Railway Dashboard → Your Service → **Variables** tab:

**Add or update:**
```
EMBEDDING_MODEL=keepitreal/vietnamese-sbert
```

This model produces **384 dimensions** which matches your current database schema.

### Step 2: Rebuild Embeddings

After Railway redeploys, run:

```bash
railway run python scripts/build_embeddings.py
```

Or connect to Railway shell and run it there.

**Done!** ✅ The error should be fixed.

---

## 🎯 Alternative Models (384 dimensions)

If `keepitreal/vietnamese-sbert` doesn't work, try these:

| Model | Dimensions | Language | Notes |
|-------|------------|----------|-------|
| `keepitreal/vietnamese-sbert` | 384 | Vietnamese | Recommended |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 384 | Multilingual | Fallback |
| `all-MiniLM-L6-v2` | 384 | English | Fast fallback |

Set on Railway:
```
EMBEDDING_MODEL=<model_name>
```

---

## 🔧 Better Fix (if you want 768-dim for higher quality)

If you want to use the better `hiieu/halong_embedding` model (768-dim):

### Step 1: Run Migration Script

```bash
# Get Railway database URL
export DATABASE_URL="<your-railway-postgres-url>"

# Run migration
python scripts/fix_vector_dimension.py
```

Choose option **1** (768 dimensions)

### Step 2: Update Code Files

Update these 2 files to use `vector(768)`:

**File 1:** [src/services/postgres_database_service.py](src/services/postgres_database_service.py#L110)
```python
# Line 110 - Change from:
embedding vector(384),
# To:
embedding vector(768),
```

**File 2:** [src/services/memory_service.py](src/services/memory_service.py#L90)
```python
# Line 90 - Change from:
embedding vector(384),
# To:
embedding vector(768),
```

### Step 3: Set Environment Variable on Railway

```
EMBEDDING_MODEL=hiieu/halong_embedding
```

### Step 4: Rebuild Embeddings

```bash
railway run python scripts/build_embeddings.py
```

### Step 5: Deploy

```bash
git add .
git commit -m "Fix: Update to 768-dim embeddings"
git push
```

---

## 🔍 Diagnosis Commands

To check your current state:

```bash
# Check model dimension locally
python scripts/check_vector_dimension.py
```

Or manually:

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("hiieu/halong_embedding")
emb = model.encode("test")
print(f"Model dimension: {len(emb)}")
```

To check database dimension:

```sql
-- Connect to Railway PostgreSQL
SELECT 
    pg_catalog.format_type(atttypid, atttypmod) as column_type
FROM pg_attribute 
WHERE attrelid = 'embeddings'::regclass 
AND attname = 'embedding';
```

---

## 🆘 Still Having Issues?

### Error: "Model not found"

Some models need Hugging Face authentication:

```bash
# On Railway, set:
HF_TOKEN=your_huggingface_token
```

### Error: "Out of memory"

Railway Starter plan (512MB RAM) might struggle with 768-dim models. Either:
- Use 384-dim model (Option 1 above) ✅
- Upgrade Railway plan 💰

### Error: "No embeddings found"

You need to rebuild embeddings:

```bash
railway run python scripts/build_embeddings.py
```

---

## 📊 Model Comparison

| Aspect | 384-dim (faster) | 768-dim (better) |
|--------|------------------|------------------|
| **Model** | `keepitreal/vietnamese-sbert` | `hiieu/halong_embedding` |
| **Accuracy** | Good | Better |
| **Speed** | Faster | Slower |
| **Memory** | ~200MB | ~500MB |
| **Railway Plan** | Starter OK | Developer+ |
| **Setup Time** | 5 minutes | 20 minutes |

---

## ✅ Verification

After applying the fix, test it:

```bash
# Test locally with Railway DATABASE_URL
export DATABASE_URL="<railway-postgres-url>"
python test_railway_config.py
```

Or test the API:

```bash
curl -X POST https://your-app.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quy định thi là gì?", "session_id": "test"}'
```

Should return a response without the dimension error.

---

## 📚 Related Documentation

- [VECTOR_DIMENSION_FIX.md](VECTOR_DIMENSION_FIX.md) - Comprehensive fix guide
- [scripts/fix_vector_dimension.py](scripts/fix_vector_dimension.py) - Migration script
- [scripts/check_vector_dimension.py](scripts/check_vector_dimension.py) - Diagnostic script

---

**Created:** 2025-12-25  
**Last Updated:** 2025-12-25
