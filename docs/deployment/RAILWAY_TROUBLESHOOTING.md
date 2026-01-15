# Railway Deployment Troubleshooting Guide

## ❌ Lỗi: Healthcheck Failed - Service Unavailable

### Triệu chứng
```
[93mAttempt #14 failed with service unavailable[0m
[91m1/1 replicas never became healthy![0m
[91mHealthcheck failed![0m
```

### Nguyên nhân thường gặp

#### 1. **Environment Variables thiếu hoặc sai** 🔴 CRITICAL

**Kiểm tra trên Railway Dashboard:**

```bash
# Bắt buộc phải có:
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=<64-char-hex-string>
GEMINI_API_KEY=AIzaSy...
SUPABASE_URL=https://[project].supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
SUPABASE_ANON_KEY=eyJhbGci...

# Railway tự động cung cấp:
PORT=<auto-assigned>
RAILWAY_VOLUME_MOUNT=/data (nếu có volume)
```

**Test cách kiểm tra:**
```bash
# Trong Railway CLI:
railway variables

# Hoặc check trong Dashboard:
# Project → Variables → Ensure all required vars are set
```

#### 2. **Database Connection Failed** 🔴 HIGH

**Nguyên nhân:**
- Sai DATABASE_URL (dùng Direct thay vì Pooling)
- Supabase project bị pause
- Network timeout

**Fix:**

```bash
# 1. Vào Supabase Dashboard
# 2. Project Settings → Database → Connection string
# 3. Chọn "Connection Pooling" (6543) KHÔNG phải Direct (5432)
# 4. Copy và paste vào Railway Variables:

DATABASE_URL=postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# 5. Unpause project nếu bị pause:
# Supabase Dashboard → Pause/Resume Project
```

#### 3. **Server Start Failed - Code Error** 🔴 HIGH

**Check logs để tìm stack trace:**

```bash
# Railway CLI:
railway logs

# Tìm errors như:
# - ImportError: No module named 'xxx'
# - ModuleNotFoundError
# - SyntaxError
# - AttributeError
```

**Common errors:**

```python
# Error: ModuleNotFoundError: No module named 'config'
# Fix: Ensure requirements.txt has all dependencies

# Error: AttributeError: 'PostgresDatabaseService' object has no attribute 'get_connection'
# Fix: Use self.db.engine.connect() instead

# Error: ValidationError: String should have at least 8 characters
# Fix: Passwords phải >= 8 ký tự
```

#### 4. **Port Binding Issues** 🟡 MEDIUM

```bash
# Railway tự động set PORT
# KHÔNG hard-code port trong code

# ✅ ĐÚNG:
PORT = int(os.getenv("PORT", 8000))

# ❌ SAI:
PORT = 8000  # This will fail on Railway
```

#### 5. **Startup Script Timeout** 🟡 MEDIUM

**Vấn đề:** Script chạy quá lâu (>5 phút) khiến healthcheck timeout

**Fix:** Đã tạo `railway_startup_simple.sh` để start nhanh hơn

---

## 🔧 Các bước Debug

### Bước 1: Check Railway Logs

```bash
railway login
railway link
railway logs --follow
```

**Tìm errors đầu tiên trong logs:**
- Python traceback
- Database connection errors
- Missing environment variables

### Bước 2: Verify Environment Variables

```bash
railway variables
```

**Checklist:**
- [ ] DATABASE_URL có đúng format và port 6543?
- [ ] JWT_SECRET_KEY có 64 ký tự?
- [ ] GEMINI_API_KEY có prefix AIzaSy?
- [ ] SUPABASE_URL có https://[project].supabase.co?
- [ ] REDIS_URL (optional) có đúng format?

### Bước 3: Test Database Connection Local

```bash
# Set environment variable
$env:DATABASE_URL="postgresql://..."

# Run verification script
python scripts/verify_railway_connection.py
```

Expected output:
```
✅ PostgreSQL connected
✅ pgvector extension is INSTALLED
✅ Write permissions verified
```

### Bước 4: Test Server Local

```bash
# Activate environment
conda activate uni_bot

# Start server với Railway env vars
$env:PORT="8000"
$env:DATABASE_URL="<your-supabase-url>"
python main.py

# Test healthcheck
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "University Chatbot API",
  "version": "1.0.0"
}
```

### Bước 5: Re-deploy với Simple Startup

**Đã thực hiện (commit ecc0e2b):**
- ✅ Tạo `railway_startup_simple.sh` (skip database init)
- ✅ Update `railway.json` để dùng simple startup
- ✅ Tạo `init_db_manual.sh` để init database sau

**Railway sẽ auto-deploy khi push lên GitHub**

Sau khi deploy thành công:
```bash
# Run database init manually
railway run bash init_db_manual.sh
```

---

## 🚀 Quick Fix Checklist

### Immediate Actions:

1. **Verify DATABASE_URL** 🔴
   ```bash
   railway variables get DATABASE_URL
   # Should be: postgresql://postgres.[PROJECT]:****@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

2. **Check Supabase Project Status** 🔴
   - Dashboard → Ensure project is NOT paused
   - Database → Pooler should be enabled

3. **Regenerate JWT Secret** 🔴
   ```bash
   python scripts/generate_jwt_secret.py
   railway variables set JWT_SECRET_KEY=<generated-key>
   ```

4. **Trigger Re-deploy** 🟡
   ```bash
   git commit --allow-empty -m "trigger redeploy"
   git push origin main
   ```

5. **Watch Deployment** 🟢
   ```bash
   railway logs --follow
   ```

---

## 📊 Expected Log Output (Success)

```
==========================================
🚂 Railway Startup (Simple Mode)
==========================================

[1/2] Environment Check...
DATABASE_URL: postgresql://postgres.thess...
PORT: 8000
RAILWAY_VOLUME_MOUNT: /data

[2/2] Starting FastAPI server...
==========================================

INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

```
====================
Starting Healthcheck
====================
Path: /health
Retry window: 5m0s

✅ Healthcheck passed!
Deployment successful!
```

---

## 🆘 Still Failing? Advanced Debug

### Enable Debug Logging

Sửa `railway_startup_simple.sh`:
```bash
exec python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --log-level debug \
    --access-log  # Enable access logs
```

### Check Railway Service Logs

```bash
railway logs --service <service-name> --environment production
```

### Inspect Container

```bash
# SSH into Railway container (if available)
railway shell

# Check Python version
python3 --version

# Check installed packages
pip list | grep -E "fastapi|langchain|sqlalchemy"

# Test imports
python3 -c "import main; print('OK')"
```

### Force Rebuild

```bash
# Clear build cache
railway up --service <service-name>

# Or trigger via GitHub
git commit --allow-empty -m "force rebuild"
git push origin main
```

---

## 📞 Support Resources

1. **Railway Discord**: https://discord.gg/railway
2. **Railway Docs**: https://docs.railway.app/
3. **Supabase Discord**: https://discord.supabase.com/
4. **Project Docs**: `docs/deployment/RAILWAY_SUPABASE_DEPLOYMENT.md`

---

## ✅ Success Checklist

Khi deployment thành công, bạn sẽ thấy:

- [ ] Railway Dashboard shows "Healthy" status
- [ ] Logs show "Application startup complete"
- [ ] Healthcheck passes (200 OK)
- [ ] `curl https://your-app.railway.app/health` returns JSON
- [ ] `curl https://your-app.railway.app/docs` shows Swagger UI

**Next steps after successful deployment:**
```bash
# 1. Initialize database
railway run bash init_db_manual.sh

# 2. Test authentication
curl -X POST https://your-app.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123"}'

# 3. Upload PDFs (via Swagger UI or API)

# 4. Build embeddings
curl -X POST https://your-app.railway.app/api/admin/rebuild-embeddings \
  -H "Authorization: Bearer <token>"
```

---

**Last Updated**: 15/01/2026  
**Commit**: ecc0e2b - Simplified Railway startup for debugging
