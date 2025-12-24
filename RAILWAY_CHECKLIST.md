# ✅ Railway Deployment Checklist

> Quick checklist để deploy lên Railway

## 🔧 Code Changes (Đã Hoàn Thành)

- [x] Fix PostgreSQL dialect error (`config/settings.py`)
- [x] Add Railway Redis URL support (`config/settings.py`)
- [x] Update Redis connection with password (`cache_service.py`, `embedding_service.py`)
- [x] Create deployment documentation
- [x] Create test script (`test_railway_config.py`)
- [x] Local test passed (4/6 - expected for no local DB)

## 📦 Pre-Deployment

- [ ] All code committed to Git
- [ ] Pushed to GitHub/GitLab
- [ ] `requirements.txt` up to date
- [ ] `nixpacks.toml` exists (if using custom config)

## 🚀 Railway Setup

### 1. Create Project
- [ ] Login to [Railway.app](https://railway.app/)
- [ ] Create new project from GitHub repo
- [ ] Select `uni_bot` repository

### 2. Add Databases
- [ ] PostgreSQL auto-added or manually add
- [ ] Redis added (recommended)
- [ ] Verify `DATABASE_URL` is set
- [ ] Verify `REDIS_URL` is set (if added)

### 3. Environment Variables

**Required:**
- [ ] `LLM_PROVIDER=gemini`
- [ ] `GEMINI_API_KEY=your_key_here`

**Recommended:**
- [ ] `EMBEDDING_MODEL=hiieu/halong_embedding`
- [ ] `ENABLE_REDIS_CACHE=true`
- [ ] `LOG_LEVEL=INFO`
- [ ] `TOP_K_RESULTS=15`

**Optional:**
- [ ] `HF_TOKEN` (if using private models)
- [ ] `RAILWAY_VOLUME_MOUNT=/data` (if using volume)

### 4. Deploy
- [ ] Click "Deploy" or wait for auto-deploy
- [ ] Monitor build logs
- [ ] Wait for deployment to complete (2-5 minutes)

## ✅ Verification

### Check Logs
- [ ] Open Railway logs
- [ ] Look for: `✅ PostgreSQL connection successful`
- [ ] Look for: `✅ Embedding model loaded successfully`
- [ ] Look for: `✅ Redis connected successfully`
- [ ] Look for: `Uvicorn running on 0.0.0.0:PORT`

### Test API
- [ ] Generate Railway domain
- [ ] Test health endpoint: `GET /`
- [ ] Test chat endpoint: `POST /api/v1/chat`

```bash
# Health check
curl https://your-app.railway.app/

# Chat test
curl -X POST https://your-app.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào"}'
```

## 🔍 Common Issues

| Issue | Solution |
|-------|----------|
| ❌ SQLAlchemy dialect error | ✅ Already fixed in code |
| ❌ Redis connection refused | Add Redis plugin or set `ENABLE_REDIS_CACHE=false` |
| ❌ Out of memory | Use lighter model: `all-MiniLM-L6-v2` |
| ❌ Build timeout | Check `requirements.txt` for heavy packages |
| ❌ 404 errors | Check domain and routes |

## 📊 Success Criteria

**Deployment is successful when:**

✅ Build completes without errors  
✅ PostgreSQL connected  
✅ Embedding service loaded  
✅ API responds to requests  
✅ Chat functionality works  

**Optional but recommended:**

🟡 Redis connected  
🟡 Custom domain configured  
🟡 Frontend deployed and connected  
🟡 PDFs uploaded and indexed  

## 🎯 Post-Deployment

- [ ] Upload PDF documents
- [ ] Test chat with Vietnamese questions
- [ ] Configure frontend to use backend URL
- [ ] Deploy frontend (Vercel/Railway)
- [ ] Set up monitoring/alerts
- [ ] Configure custom domain (optional)

## 📚 Documentation Reference

- **Detailed Guide:** [DEPLOY_TO_RAILWAY.md](DEPLOY_TO_RAILWAY.md)
- **Quick Fix:** [RAILWAY_QUICK_FIX.md](RAILWAY_QUICK_FIX.md)
- **Full Guide:** [RAILWAY_FIX_GUIDE.md](RAILWAY_FIX_GUIDE.md)
- **Test Script:** `python test_railway_config.py`

## 🆘 Need Help?

1. Check Railway logs: `railway logs`
2. Review error messages
3. Consult documentation files
4. Check Railway Discord/Support

---

**Current Status:** ✅ Code ready to deploy!

**Next Step:** Push to GitHub and create Railway project

---

*Generated: 24/12/2024*
