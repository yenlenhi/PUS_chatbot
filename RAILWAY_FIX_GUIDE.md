# 🚂 Railway Deployment Fix Guide

## ✅ Các Vấn Đề Đã Fix

### 1. ✅ SQLAlchemy PostgreSQL Dialect Error

**Lỗi:** `Can't load plugin: sqlalchemy.dialects:postgres`

**Nguyên nhân:** Railway cung cấp `DATABASE_URL` với scheme `postgres://`, nhưng SQLAlchemy 1.4+ yêu cầu `postgresql://`

**Giải pháp:** Đã thêm code auto-fix trong `config/settings.py`:

```python
# Fix Railway's postgres:// URL scheme to postgresql:// for SQLAlchemy 1.4+
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
```

---

## ⚠️ Các Vấn Đề Cần Xử Lý Trên Railway

### 2. ⚠️ Vietnamese Embedding Model Error

**Lỗi hiện tại:**
```
bkai-foundation-models/vietnamese-embedding-v1 is not a local folder and is not a valid model identifier
```

**Tình trạng:** Đã fallback sang `all-MiniLM-L6-v2` (model tiếng Anh)

**Giải pháp:**

#### Option A: Sử dụng model fallback (Khuyến nghị cho nhanh)
- Hệ thống đã tự động fallback sang `all-MiniLM-L6-v2`
- Hoạt động ổn định nhưng **kém chính xác với tiếng Việt**

#### Option B: Sử dụng model tiếng Việt từ Hugging Face
1. Đăng nhập Hugging Face trên Railway:
   ```bash
   huggingface-cli login --token YOUR_HF_TOKEN
   ```

2. Hoặc set environment variable:
   ```bash
   HF_TOKEN=your_hugging_face_token
   ```

3. Model sẽ được download lần đầu và cache lại

#### Option C: Pre-download model vào volume
1. Tạo Railway Volume
2. Download model trước vào volume
3. Set `TRANSFORMERS_CACHE` environment variable

---

### 3. ⚠️ Redis Connection Error

**Lỗi hiện tại:**
```
Error 111 connecting to localhost:6379. Connection refused.
```

**Tình trạng:** Hệ thống chạy ở **no-cache mode** (không crash nhưng chậm hơn)

**Giải pháp:**

#### Option A: Thêm Redis service trên Railway (Khuyến nghị)

1. **Add Redis Plugin:**
   - Vào Railway Dashboard
   - Click "New" → "Database" → "Add Redis"
   - Railway sẽ tự động tạo và set các biến:
     - `REDIS_URL`
     - `REDIS_PRIVATE_URL`

2. **Update `config/settings.py`** để sử dụng Railway Redis:

```python
# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL")

if REDIS_URL:
    # Parse Redis URL (format: redis://user:pass@host:port/db)
    import urllib.parse
    parsed = urllib.parse.urlparse(REDIS_URL)
    REDIS_HOST = parsed.hostname or "localhost"
    REDIS_PORT = parsed.port or 6379
    REDIS_PASSWORD = parsed.password
    REDIS_DB = int(parsed.path[1:]) if parsed.path and len(parsed.path) > 1 else 0
else:
    # Local fallback
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
```

3. **Update Redis connection code** trong `src/services/cache_service.py`:

```python
def _connect(self):
    """Connect to Redis"""
    try:
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=REDIS_DECODE_RESPONSES,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        self.redis.ping()
        log.info("✅ Redis connected successfully")
    except Exception as e:
        log.error(f"❌ Failed to connect to Redis: {e}")
        log.warning("⚠️ Cache service will operate in no-cache mode")
        self.redis = None
```

#### Option B: Disable Redis (No cache)

Set environment variable trên Railway:
```bash
ENABLE_REDIS_CACHE=false
```

Hệ thống sẽ tiếp tục hoạt động nhưng không có cache.

---

## 📋 Checklist Deploy Railway

### 1. Environment Variables Cần Thiết

```bash
# LLM Provider
LLM_PROVIDER=gemini  # hoặc "ollama" nếu có Ollama service
GEMINI_API_KEY=your_gemini_api_key

# Database (Railway tự động set)
DATABASE_URL=postgresql://...  # Railway auto-generates
POSTGRES_HOST=...  # Railway auto-generates
POSTGRES_PASSWORD=...  # Railway auto-generates
POSTGRES_USER=...  # Railway auto-generates

# Redis (nếu dùng Redis plugin)
REDIS_URL=redis://...  # Railway auto-generates

# Optional: Hugging Face Token (nếu dùng Vietnamese model)
HF_TOKEN=your_hugging_face_token

# Railway Volume (nếu dùng)
RAILWAY_VOLUME_MOUNT=/data
```

### 2. Railway Services Cần Thiết

- [x] **Web Service** (Backend FastAPI)
- [x] **PostgreSQL Database** (tự động)
- [ ] **Redis** (khuyến nghị - thêm qua Add Redis)
- [ ] **Volume** (optional - để lưu PDFs/models)

### 3. Build & Deploy Settings

**Nixpacks Configuration** (`nixpacks.toml`):

```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install --upgrade pip", "pip install -r requirements.txt"]

[phases.build]
cmds = []

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 🧪 Testing

### Test locally với Railway DATABASE_URL:

1. Copy `DATABASE_URL` từ Railway dashboard
2. Chạy local:

```bash
# Set DATABASE_URL
$env:DATABASE_URL="postgresql://postgres:..."

# Test connection
python test_postgres_connection.py

# Run server
uvicorn main:app --reload
```

### Test trên Railway:

```bash
# View logs
railway logs

# Check environment
railway run env

# SSH vào container (nếu cần)
railway run bash
```

---

## 🔍 Debug Commands

### 1. Check Database Connection
```python
from config.settings import DATABASE_URL
print(f"DATABASE_URL: {DATABASE_URL}")
```

### 2. Check Redis Connection
```python
import redis
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
r.ping()
```

### 3. Check Model Loading
```python
from src.services.embedding_service import EmbeddingService
service = EmbeddingService()
print(f"Model loaded: {service.model}")
```

---

## 📊 Performance Tips

### 1. Model Loading

- **Fallback model** (`all-MiniLM-L6-v2`): ~90MB, load nhanh
- **Vietnamese model**: ~500MB, load chậm hơn
- **Khuyến nghị:** Dùng fallback model cho dev, Vietnamese model cho production

### 2. Redis Cache

- **Với Redis:** Response time ~100-200ms (cached)
- **Không Redis:** Response time ~1-2s (no cache)
- **Khuyến nghị:** Bật Redis cho production

### 3. Railway Resources

- **Starter Plan:** 512MB RAM, đủ cho fallback model
- **Pro Plan:** 8GB RAM, chạy được Vietnamese model
- **Khuyến nghị:** Start với fallback model, upgrade sau

---

## ✅ Quick Fix Checklist

1. [x] **Fix SQLAlchemy dialect error** → Code đã fix tự động
2. [ ] **Add Redis service** → Railway Dashboard → Add Redis
3. [ ] **Update Redis config** → Thêm code parse `REDIS_URL`
4. [ ] **Set GEMINI_API_KEY** → Railway Environment Variables
5. [ ] **Test deployment** → Check logs & test chat API

---

## 🆘 Common Errors & Solutions

### Error: "pool pre-ping failed"
**Solution:** Database đang restart, đợi vài giây

### Error: "too many connections"
**Solution:** Giảm `pool_size` trong `postgres_database_service.py`

### Error: "Out of memory"
**Solution:** 
- Dùng fallback model (`all-MiniLM-L6-v2`)
- Upgrade Railway plan
- Disable embedding cache

### Error: "Connection timeout"
**Solution:**
- Check DATABASE_URL đúng format
- Check firewall rules
- Check network connectivity

---

## 📞 Support

- Railway Docs: https://docs.railway.app/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- FastAPI Docs: https://fastapi.tiangolo.com/
- pgvector Docs: https://github.com/pgvector/pgvector

---

*Cập nhật: 24/12/2024*
