# 🚀 Quick Railway Deployment Reference

## ⚡ Quick Fixes Applied

### 1. ✅ Fixed SQLAlchemy Dialect Error
**File:** `config/settings.py`
```python
# Auto-convert postgres:// to postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
```

### 2. ✅ Added Redis URL Support
**File:** `config/settings.py`
```python
# Parse Railway Redis URL
REDIS_URL = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL")
if REDIS_URL:
    parsed = urllib.parse.urlparse(REDIS_URL)
    REDIS_HOST = parsed.hostname or "localhost"
    REDIS_PORT = parsed.port or 6379
    REDIS_PASSWORD = parsed.password
    REDIS_DB = int(parsed.path[1:]) if parsed.path else 0
```

### 3. ✅ Updated Redis Connection
**Files:** `src/services/cache_service.py`, `src/services/embedding_service.py`
- Added `password` parameter support
- Added connection timeout handling

---

## 🔧 Railway Setup Checklist

### Step 1: Add Redis (Khuyến nghị)
```bash
Railway Dashboard → New → Database → Add Redis
```
Railway sẽ tự động set:
- `REDIS_URL`
- `REDIS_PRIVATE_URL`

### Step 2: Set Environment Variables
```bash
# Required
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here

# Optional (nếu muốn dùng Vietnamese model)
HF_TOKEN=your_huggingface_token

# Optional (tắt cache nếu không dùng Redis)
ENABLE_REDIS_CACHE=false
```

### Step 3: Deploy
```bash
git add .
git commit -m "Fix Railway deployment issues"
git push
```

Railway sẽ tự động:
- Detect PostgreSQL (đã có)
- Build với nixpacks
- Deploy backend

---

## 🧪 Test Local với Railway Config

### 1. Copy Database URL từ Railway
```bash
Railway Dashboard → PostgreSQL → Connect → Copy DATABASE_URL
```

### 2. Set Local Environment
```bash
# PowerShell
$env:DATABASE_URL="postgresql://postgres:..."
$env:LLM_PROVIDER="gemini"
$env:GEMINI_API_KEY="your_key"

# Optional: Copy Redis URL
$env:REDIS_URL="redis://default:..."
```

### 3. Run Tests
```bash
# Test config
python test_railway_config.py

# Test server
uvicorn main:app --reload
```

---

## 📊 Current Status

| Component | Status | Note |
|-----------|--------|------|
| PostgreSQL | ✅ Fixed | Auto-convert URL scheme |
| Redis | ⚠️ Optional | Add via Railway Dashboard |
| Embedding | ⚠️ Fallback | Using `all-MiniLM-L6-v2` |
| LLM | ✅ Ready | Set `GEMINI_API_KEY` |

---

## 🐛 Common Issues

### Issue 1: "Can't load plugin: sqlalchemy.dialects:postgres"
**Fixed:** ✅ Auto-converts `postgres://` to `postgresql://`

### Issue 2: "Connection refused localhost:6379"
**Options:**
1. Add Redis via Railway (khuyến nghị)
2. Set `ENABLE_REDIS_CACHE=false` (no cache mode)

### Issue 3: "vietnamese-embedding-v1 not found"
**Status:** Using fallback model `all-MiniLM-L6-v2`
**Impact:** Hoạt động nhưng kém chính xác với tiếng Việt

**Options:**
1. Keep fallback (nhanh, ổn định)
2. Set `HF_TOKEN` để download Vietnamese model (chậm hơn nhưng chính xác hơn)

---

## 📝 Next Steps

1. **Deploy lên Railway**
   ```bash
   git push
   ```

2. **Check logs**
   ```bash
   railway logs
   ```

3. **Test API**
   ```bash
   curl https://your-app.railway.app/api/v1/health
   ```

4. **Add Redis** (optional nhưng khuyến nghị)
   - Railway Dashboard → Add Redis
   - Redeploy tự động

5. **Monitor performance**
   - Check response times
   - Check embedding quality
   - Consider upgrading to Vietnamese model if needed

---

## 🆘 Need Help?

Check full guide: [RAILWAY_FIX_GUIDE.md](RAILWAY_FIX_GUIDE.md)

---

*Last updated: 24/12/2024*
