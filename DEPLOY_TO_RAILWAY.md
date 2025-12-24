# 🚀 Deploy to Railway - Step by Step Guide

## ✅ Pre-Deployment Checklist

- [x] Fixed SQLAlchemy PostgreSQL dialect error
- [x] Added Railway Redis URL support
- [x] Updated Redis connection with password
- [x] Local test passed (4/6 tests - expected)
- [x] Embedding model working: `hiieu/halong_embedding`
- [x] LLM configured: Gemini with API key

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare Git Repository

```bash
# Make sure all changes are committed
git status

# If you have uncommitted changes
git add .
git commit -m "Fix Railway deployment - PostgreSQL dialect and Redis support"

# Push to your repository
git push origin main  # or your branch name
```

### Step 2: Create Railway Project

1. Go to [Railway.app](https://railway.app/)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `uni_bot` repository
5. Railway will automatically detect it's a Python project

### Step 3: Add PostgreSQL Database

Railway should auto-detect and add PostgreSQL. If not:

1. In your Railway project dashboard
2. Click **"New"** → **"Database"** → **"Add PostgreSQL"**
3. Railway automatically creates and sets:
   - `DATABASE_URL`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`
   - `POSTGRES_HOST`

✅ **Our fix handles Railway's `postgres://` scheme automatically!**

### Step 4: Add Redis (Recommended)

1. Click **"New"** → **"Database"** → **"Add Redis"**
2. Railway automatically sets:
   - `REDIS_URL`
   - `REDIS_PRIVATE_URL`

✅ **Our code automatically parses Railway's Redis URL!**

### Step 5: Set Environment Variables

In Railway dashboard → Your service → **Variables** tab:

#### Required:
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

#### Optional (Recommended):
```bash
# Embedding model (current working model)
EMBEDDING_MODEL=hiieu/halong_embedding

# Or use fallback for faster deployment
# EMBEDDING_MODEL=all-MiniLM-L6-v2

# Enable/disable features
ENABLE_REDIS_CACHE=true
ENABLE_GEMINI_NORMALIZATION=true

# RAG Configuration
TOP_K_RESULTS=15
SIMILARITY_THRESHOLD=0.35

# Logging
LOG_LEVEL=INFO
```

#### For Vietnamese Embedding Models (Optional):
```bash
# If you want to use Vietnamese models that require authentication
HF_TOKEN=your_huggingface_token
```

### Step 6: Configure Build Settings (Usually Auto-Detected)

Railway uses `nixpacks.toml` automatically. Verify it exists:

**nixpacks.toml:**
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install --upgrade pip", "pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

### Step 7: Deploy!

1. Click **"Deploy"** (or wait for auto-deploy)
2. Railway will:
   - Install dependencies from `requirements.txt`
   - Run database migrations automatically (pgvector extension)
   - Start the FastAPI server

### Step 8: Monitor Deployment

```bash
# View logs in real-time
railway logs

# Or in Railway Dashboard → Deployments → View Logs
```

**Look for these success messages:**
```
✅ PostgreSQL connection successful
✅ pgvector extension is installed
✅ Embedding model loaded successfully
✅ Redis connected successfully (if added)
✅ Uvicorn running on 0.0.0.0:PORT
```

### Step 9: Get Your API URL

1. Railway Dashboard → Your service
2. Click **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Your API will be at: `https://your-app-name.railway.app`

### Step 10: Test Your API

```bash
# Health check
curl https://your-app-name.railway.app/

# Or test chat endpoint
curl -X POST https://your-app-name.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào"}'
```

---

## 🔍 Troubleshooting

### Issue: Build fails with "Out of Memory"

**Solution:**
1. Use lighter embedding model:
   ```bash
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```
2. Or upgrade Railway plan

### Issue: "Connection refused" to PostgreSQL

**Check:**
- DATABASE_URL is set by Railway
- Our auto-fix converts `postgres://` to `postgresql://`
- Wait 30-60 seconds for database to initialize

### Issue: "pgvector extension not found"

**Solution:**
```sql
-- Run in Railway PostgreSQL console
CREATE EXTENSION IF NOT EXISTS vector;
```

Or code will auto-create on first connection.

### Issue: Slow response times

**Solution:**
1. Add Redis for caching (Step 4)
2. Check embedding model size
3. Monitor Railway metrics

### Issue: 404 errors

**Check:**
- Frontend is deployed separately (Next.js)
- Backend URL in frontend `.env`:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

---

## 📊 Expected Deployment Results

### ✅ Success Indicators:

- Build completes without errors
- PostgreSQL connects successfully
- Embedding model loads (may take 1-2 minutes first time)
- Redis connects (if added)
- API responds to health checks

### ⚠️ Warnings (Non-Critical):

- "Fallback model loaded" - OK if Vietnamese model not available
- "Cache service not connected" - OK if Redis not added
- "Running without cache" - OK but slower

### ❌ Critical Errors:

- "Can't load plugin: sqlalchemy.dialects:postgres" - **FIXED by our code**
- "Connection refused" lasting >5 minutes - Check environment variables
- "Out of memory" - Upgrade plan or use lighter model

---

## 🎯 Post-Deployment Tasks

### 1. Initialize Database

```bash
# Upload your PDF documents
# Use Railway's web interface or CLI

railway run python scripts/ingest_documents.py
```

### 2. Configure Frontend

Update frontend environment variables:
```bash
# In your Next.js project
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

Deploy frontend to Vercel/Railway.

### 3. Monitor Performance

- Check Railway metrics dashboard
- Monitor response times
- Check error rates
- Verify embedding quality

### 4. Set Up Domain (Optional)

1. Railway Dashboard → Settings → Networking
2. Add custom domain
3. Configure DNS (CNAME or A record)

---

## 💰 Railway Pricing Considerations

### Starter Plan ($5/month):
- 512MB RAM
- 1GB Disk
- **Recommended:** Use `all-MiniLM-L6-v2` model

### Developer Plan ($20/month):
- 8GB RAM
- 10GB Disk
- **Can use:** `hiieu/halong_embedding` or Vietnamese models

### Optimization Tips:
- Use Redis to reduce embedding computations
- Enable caching for frequently asked questions
- Monitor resource usage in Railway dashboard

---

## 🔗 Useful Links

- **Railway Docs:** https://docs.railway.app/
- **Railway Status:** https://status.railway.app/
- **Railway CLI:** https://docs.railway.app/develop/cli
- **Support:** Railway Discord or GitHub Issues

---

## ✅ Deployment Complete Checklist

- [ ] Git repository pushed
- [ ] Railway project created
- [ ] PostgreSQL added and connected
- [ ] Redis added (optional but recommended)
- [ ] Environment variables set (GEMINI_API_KEY, etc.)
- [ ] Deployment successful
- [ ] Health check passes
- [ ] Chat API responds correctly
- [ ] Frontend connected to backend
- [ ] PDFs uploaded and processed
- [ ] Monitoring configured

---

## 🎉 You're Ready!

Your Railway deployment should now be working! Check logs for any issues and refer to [RAILWAY_FIX_GUIDE.md](RAILWAY_FIX_GUIDE.md) for detailed troubleshooting.

**Support:**
- Check Railway logs: `railway logs`
- Review [RAILWAY_QUICK_FIX.md](RAILWAY_QUICK_FIX.md)
- Test locally: `python test_railway_config.py`

---

*Last updated: 24/12/2024*
