# 🚀 Railway Deployment Quick Reference

**Last Updated**: 15/01/2026  
**For**: University Chatbot deployment on Railway + Supabase

---

## ⚡ Quick Start (5 phút)

### 1. Supabase Setup (2 phút)
```bash
# 1. Tạo project trên https://supabase.com
# 2. Vào SQL Editor, chạy:
CREATE EXTENSION IF NOT EXISTS vector;

# 3. Copy DATABASE_URL từ Settings → Database
postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres
```

### 2. Railway Setup (3 phút)
```bash
# 1. Connect GitHub repo tại https://railway.app
# 2. Add Redis service: Click "+ New Service" → Redis
# 3. Add Volume: Click service → Volumes → New Volume
#    - Mount path: /data
#    - Size: 2GB
```

### 3. Environment Variables
Copy từ `.env.railway` vào Railway Variables tab:

**CRITICAL (Must set):**
```bash
DATABASE_URL=postgresql://postgres:...@...supabase.co:5432/postgres
JWT_SECRET_KEY=$(openssl rand -hex 32)  # Generate new!
GEMINI_API_KEY=AIzaSy...
SUPABASE_URL=https://...supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

**Important:**
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app
HTTPS_ONLY=true
```

### 4. Deploy
```bash
# Railway auto-deploys on push
git push origin main

# Monitor logs
railway logs
```

---

## 📋 Pre-Deploy Checklist

- [ ] **Supabase**: pgvector extension enabled
- [ ] **Railway**: Redis + Volume configured
- [ ] **ENV**: DATABASE_URL set correctly (Direct connection, not Pooling)
- [ ] **ENV**: JWT_SECRET_KEY generated (NOT default value)
- [ ] **ENV**: SUPABASE_URL + SUPABASE_SERVICE_KEY set
- [ ] **ENV**: GEMINI_API_KEY set (hoặc OLLAMA_BASE_URL nếu dùng Ollama)
- [ ] **ENV**: ALLOWED_ORIGINS points to your frontend domain
- [ ] **Code**: railway_startup.sh has execute permission (`chmod +x`)

---

## 🔍 Post-Deploy Verification

### 1. Check Health Endpoint
```bash
curl https://your-app.railway.app/health
# Expected: {"status": "healthy", ...}
```

### 2. Check Database Connection
```bash
railway run python scripts/verify_railway_connection.py
```

### 3. Test Login
```bash
curl -X POST "https://your-app.railway.app/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123"}'
```

### 4. Check Logs
```bash
railway logs
# Look for:
# ✅ PostgreSQL connection successful
# ✅ Tables created successfully
# ✅ Admin user created
# ✅ Starting FastAPI server...
```

---

## 🔧 Common Issues & Fixes

### ❌ "Database connection failed"
```bash
# Check DATABASE_URL format
railway run python -c "from config.settings import DATABASE_URL; print(DATABASE_URL)"

# Should be: postgresql:// (not postgres://)
# Should be Direct connection (port 5432)
```

**Fix:**
1. Verify DATABASE_URL trong Railway Variables
2. Use Supabase **Direct connection** string (not Pooling)
3. Check Supabase database status trong dashboard

### ❌ "pgvector extension not found"
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### ❌ "Health check timeout"
```json
// Increase timeout in railway.json
{
  "deploy": {
    "healthcheckTimeout": 600
  }
}
```

**Root causes:**
- Database init taking too long
- Building embeddings on first start
- Cold start delay

**Solutions:**
1. Pre-build embeddings locally, upload to Volume
2. Increase timeout to 600s
3. Split init into separate job

### ❌ "JWT secret key is insecure"
```bash
# Generate new key
openssl rand -hex 32

# Set in Railway Variables
JWT_SECRET_KEY=<generated-key>

# Redeploy
railway up
```

### ❌ "CORS error from frontend"
```bash
# Check ALLOWED_ORIGINS
railway run python -c "from config.settings import ALLOWED_ORIGINS; print(ALLOWED_ORIGINS)"

# Should include frontend domain
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com
```

### ❌ "Volume not mounted"
```bash
# Check mount path
railway run ls -la /data

# Should show:
# drwxr-xr-x  pdfs/
# drwxr-xr-x  embeddings/
# drwxr-xr-x  logs/

# If empty, verify RAILWAY_VOLUME_MOUNT=/data in Variables
```

---

## 🔒 Security Post-Deploy (CRITICAL!)

### 1. Change Default Passwords
```bash
# Get token
TOKEN=$(curl -X POST "https://your-app.railway.app/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123"}' \
  | jq -r '.access_token')

# Change admin password
curl -X POST "https://your-app.railway.app/api/users/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Admin123",
    "new_password": "YourStrongPassword!2024"
  }'

# Change user password
TOKEN_USER=$(curl -X POST "https://your-app.railway.app/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"User123"}' \
  | jq -r '.access_token')

curl -X POST "https://your-app.railway.app/api/users/change-password" \
  -H "Authorization: Bearer $TOKEN_USER" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "User123",
    "new_password": "AnotherStrongPassword!2024"
  }'
```

### 2. Verify JWT Secret
```bash
railway run python -c "
from config.settings import JWT_SECRET_KEY
if 'change-this' in JWT_SECRET_KEY.lower():
    print('❌ USING DEFAULT SECRET!')
else:
    print('✅ Custom secret key set')
"
```

### 3. Verify HTTPS
```bash
curl -I https://your-app.railway.app/health
# Check for:
# HTTP/2 200
# strict-transport-security: max-age=31536000
```

---

## 📦 Upload PDFs & Build Embeddings

### Option 1: API Upload (Recommended)
```bash
# Get admin token
TOKEN="<your-admin-token>"

# Upload PDF
CHECKSUM=$(sha256sum document.pdf | awk '{print $1}')
curl -X POST "https://your-app.railway.app/api/admin/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Checksum: $CHECKSUM" \
  -H "X-Checksum-Algorithm: sha256" \
  -F "file=@document.pdf"

# Rebuild embeddings
curl -X POST "https://your-app.railway.app/api/admin/rebuild-embeddings" \
  -H "Authorization: Bearer $TOKEN"
```

### Option 2: Railway Volume Upload
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Upload files
railway run bash -c "
  mkdir -p /data/pdfs
  # Then manually copy files via Railway shell
"
```

### Option 3: Pre-build Locally
```bash
# Build embeddings locally
python scripts/build_embeddings.py

# Upload embeddings directory to Railway Volume
# (Manual: Use Railway CLI or volume export/import)
```

---

## 📊 Monitoring Commands

```bash
# View logs real-time
railway logs --follow

# Check database
railway run python scripts/verify_railway_connection.py

# List users
railway run python -c "
from src.services.user_service import get_user_service
service = get_user_service()
users, total = service.list_users(0, 100)
for u in users:
    print(f'{u.username}: {u.roles}')
"

# Check embeddings
railway run python -c "
import faiss
index = faiss.read_index('/data/embeddings/faiss_index.index')
print(f'Vectors: {index.ntotal}')
"

# Test chat API
TOKEN="<your-token>"
curl -X POST "https://your-app.railway.app/api/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Điều kiện tuyển sinh là gì?"}'
```

---

## 🔄 Update & Redeploy

```bash
# Make changes locally
git add .
git commit -m "Update: description"
git push origin main

# Railway auto-deploys
# Monitor deployment
railway logs --follow

# Verify deployment
curl https://your-app.railway.app/health
```

---

## 📚 Full Documentation

- **Detailed Guide**: [docs/deployment/RAILWAY_SUPABASE_DEPLOYMENT.md](RAILWAY_SUPABASE_DEPLOYMENT.md)
- **Security Assessment**: [docs/SECURITY_ASSESSMENT.md](../SECURITY_ASSESSMENT.md)
- **User Management**: [docs/USER_MANAGEMENT_SETUP.md](../USER_MANAGEMENT_SETUP.md)
- **Environment Template**: [.env.railway](.env.railway)

---

## 🆘 Need Help?

1. **Check logs**: `railway logs`
2. **Verify connection**: `railway run python scripts/verify_railway_connection.py`
3. **Review docs**: [RAILWAY_SUPABASE_DEPLOYMENT.md](RAILWAY_SUPABASE_DEPLOYMENT.md)
4. **Check Railway status**: https://status.railway.app/
5. **Check Supabase status**: https://status.supabase.com/

---

**Status**: ✅ Production Ready  
**Platform**: Railway  
**Database**: Supabase PostgreSQL  
**Redis**: Railway Redis  
**Storage**: Railway Volume (2GB+)
