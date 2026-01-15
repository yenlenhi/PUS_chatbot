# Railway Deployment Guide với Supabase PostgreSQL

**Hướng dẫn deploy University Chatbot lên Railway sử dụng Supabase làm database**

---

## 📋 Tổng Quan

Hệ thống này được thiết kế để deploy lên Railway với:
- **Database**: Supabase PostgreSQL (với pgvector extension)
- **Redis**: Railway Redis addon hoặc Upstash Redis
- **Storage**: Supabase Storage cho file uploads
- **Volume**: Railway Volume mount tại `/data` cho embeddings và logs

---

## 🚀 Bước 1: Chuẩn Bị Supabase Database

### 1.1. Tạo Project trên Supabase

1. Truy cập [https://supabase.com](https://supabase.com)
2. Tạo project mới
3. Chọn region gần nhất (Singapore cho VN)
4. Đợi database provisioning hoàn tất

### 1.2. Enable pgvector Extension

Vào **SQL Editor** trong Supabase Dashboard, chạy:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension
SELECT * FROM pg_available_extensions WHERE name = 'vector';
```

### 1.3. Lấy Database Connection String

Vào **Settings** → **Database** → **Connection string**:

```
URI (Direct connection):
postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres
```

**⚠️ Lưu ý**: 
- Supabase cung cấp 2 loại connection:
  - **Direct**: Dùng cho Railway (pooling: false)
  - **Pooling**: Dùng cho serverless functions
- Railway cần dùng **Direct connection** (port 5432)

### 1.4. Setup Supabase Storage

1. Vào **Storage** trong Supabase Dashboard
2. Tạo bucket mới: `chat-attachments`
3. Cấu hình:
   - Public: **No** (private bucket)
   - File size limit: 10MB
   - Allowed MIME types: `image/*`

4. Lấy credentials:
   - **Settings** → **API**
   - Copy `SUPABASE_URL` (Project URL)
   - Copy `SUPABASE_SERVICE_KEY` (service_role key - dùng cho server)
   - Copy `SUPABASE_ANON_KEY` (anon key - dùng cho client)

---

## 🚂 Bước 2: Setup Railway Project

### 2.1. Tạo Project trên Railway

1. Truy cập [https://railway.app](https://railway.app)
2. Click **New Project**
3. Chọn **Deploy from GitHub repo**
4. Authorize và chọn repository `uni_bot`

### 2.2. Add Redis Service

1. Click **+ New Service**
2. Chọn **Redis**
3. Railway sẽ tự động provision Redis và tạo `REDIS_URL`

### 2.3. Add Volume for Persistent Storage

1. Click vào service `uni_bot`
2. Vào tab **Volumes**
3. Click **+ New Volume**
4. Cấu hình:
   - **Mount Path**: `/data`
   - **Size**: 1GB - 5GB (tùy số lượng PDFs)

**Volume Structure:**
```
/data
├── pdfs/                 # PDF documents
├── new_pdf/              # Watch directory for auto-ingestion
├── processed/            # Processed PDFs
├── embeddings/
│   ├── faiss_index.index
│   ├── faiss_index.metadata
│   └── backup/
└── logs/
```

---

## ⚙️ Bước 3: Configure Environment Variables

### 3.1. Railway Environment Variables

Vào **Variables** tab, thêm các biến sau:

#### **🔴 CRITICAL - Database**
```bash
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres
```
**Lưu ý**: Railway tự động inject `RAILWAY_DATABASE_URL` nếu bạn dùng Railway Postgres. Nhưng ở đây chúng ta dùng Supabase nên cần set `DATABASE_URL` manually.

#### **🔴 CRITICAL - Supabase Storage**
```bash
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...  # service_role key (SECRET!)
SUPABASE_ANON_KEY=eyJhbGci...      # anon key
SUPABASE_STORAGE_BUCKET=chat-attachments
```

#### **🔴 CRITICAL - Security**
```bash
# Generate strong secret key: openssl rand -hex 32
JWT_SECRET_KEY=<64-character-hex-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

HTTPS_ONLY=true
TLS_MIN_VERSION=1.2
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-domain.com
```

#### **Redis** (Auto-configured by Railway)
```bash
# Railway automatically provides:
REDIS_URL=redis://default:password@redis.railway.internal:6379
```

#### **LLM Provider**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...
ENABLE_GEMINI_NORMALIZATION=true

# Optional: Ollama (nếu deploy Ollama service riêng)
# OLLAMA_BASE_URL=https://ollama-service.railway.app
```

#### **Railway Volume**
```bash
RAILWAY_VOLUME_MOUNT=/data
```

#### **API Configuration**
```bash
API_HOST=0.0.0.0
PORT=8000  # Railway tự động inject PORT variable

LOG_LEVEL=INFO
LOG_FILE=/data/logs/chatbot.log

CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=15
SIMILARITY_THRESHOLD=0.35

ENABLE_REDIS_CACHE=true
REDIS_CACHE_TTL=86400
```

### 3.2. Copy Từ Template

File `.env.railway` đã được tạo sẵn, copy các giá trị vào Railway Variables UI.

---

## 🔧 Bước 4: Configure Railway Settings

### 4.1. Build Configuration

Railway sử dụng `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "bash railway_startup.sh",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Key Points:**
- `NIXPACKS`: Auto-detect Python và install dependencies
- `startCommand`: Chạy startup script để init database trước khi start server
- `healthcheckPath`: Railway ping `/health` endpoint
- Timeout 300s: Cho phép database init chậm lần đầu

### 4.2. Startup Script

File `railway_startup.sh` xử lý:
1. Check database connection
2. Run database migrations/init (users table)
3. Build FAISS embeddings nếu chưa có
4. Start FastAPI server

---

## 🗄️ Bước 5: Initialize Database

### 5.1. Tự Động (Recommended)

Railway startup script sẽ tự động chạy:
```bash
python scripts/init_user_database.py
```

Kiểm tra logs để confirm:
```
✅ PostgreSQL connection successful
✅ Tables created successfully
✅ Admin user created: admin
✅ Regular user created: user
```

### 5.2. Manual (Nếu cần)

Connect vào Railway service:

```bash
# Railway CLI
railway run python scripts/init_user_database.py
```

Hoặc qua **Railway Shell**:
1. Vào service → **Shell** tab
2. Chạy:
```bash
cd /app
python scripts/init_user_database.py
```

### 5.3. Verify Database

Kiểm tra trong Supabase SQL Editor:

```sql
-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check users
SELECT id, username, email, disabled, created_at 
FROM users;

-- Check user roles
SELECT u.username, ur.role 
FROM users u 
JOIN user_roles ur ON u.id = ur.user_id;

-- Check document chunks (sau khi upload PDFs)
SELECT COUNT(*) FROM document_chunks;
```

---

## 📦 Bước 6: Build Embeddings

### 6.1. Upload PDFs

**Option A: Railway Volume Upload**

Sử dụng Railway CLI:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Upload PDFs
railway run python -c "
import shutil
from pathlib import Path
pdfs = Path('/data/pdfs')
pdfs.mkdir(parents=True, exist_ok=True)
# Copy từ local
for pdf in Path('./data/pdfs').glob('*.pdf'):
    shutil.copy(pdf, pdfs / pdf.name)
"
```

**Option B: API Upload (Recommended)**

Sử dụng admin API endpoint:
```bash
# Get admin token
TOKEN=$(curl -X POST "https://your-app.railway.app/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123"}' \
  | jq -r '.access_token')

# Upload PDF with checksum
CHECKSUM=$(sha256sum document.pdf | awk '{print $1}')

curl -X POST "https://your-app.railway.app/api/admin/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Checksum: $CHECKSUM" \
  -H "X-Checksum-Algorithm: sha256" \
  -F "file=@document.pdf"
```

### 6.2. Build Embeddings

Railway startup script tự động chạy:
```bash
python scripts/build_embeddings.py
```

Hoặc trigger manually qua API:
```bash
curl -X POST "https://your-app.railway.app/api/admin/rebuild-embeddings" \
  -H "Authorization: Bearer $TOKEN"
```

### 6.3. Monitor Progress

Check logs trong Railway Dashboard:
```
Processing PDFs...
✅ Loaded 50 chunks from document1.pdf
✅ Loaded 75 chunks from document2.pdf
Building FAISS index...
✅ FAISS index saved: 2500 vectors
✅ Embeddings ready!
```

---

## 🔍 Bước 7: Testing & Verification

### 7.1. Health Check

```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "embeddings": "ready",
  "vector_count": 2500
}
```

### 7.2. Authentication Test

```bash
# Login
curl -X POST "https://your-app.railway.app/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123"}'
```

Response:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "email": "admin@example.com",
    "roles": ["admin", "user"]
  }
}
```

### 7.3. Chat API Test

```bash
TOKEN="<your-token>"

curl -X POST "https://your-app.railway.app/api/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Điều kiện xét tuyển vào trường là gì?",
    "conversation_id": "test-123"
  }'
```

Expected response:
```json
{
  "answer": "Điều kiện xét tuyển vào trường bao gồm...",
  "sources": [
    {
      "chunk_id": "abc123",
      "content": "...",
      "similarity_score": 0.85,
      "metadata": {
        "source": "tuyen_sinh_2024.pdf",
        "page": 5
      }
    }
  ],
  "conversation_id": "test-123"
}
```

### 7.4. API Documentation

Truy cập Swagger UI:
```
https://your-app.railway.app/docs
```

---

## 🔒 Bước 8: Security Hardening

### 8.1. Change Default Passwords

**CRITICAL**: Đổi passwords ngay sau khi deploy!

```bash
TOKEN="<admin-token>"

curl -X POST "https://your-app.railway.app/api/users/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Admin123",
    "new_password": "YourStrongPassword!2024"
  }'
```

### 8.2. Configure CORS

Update `ALLOWED_ORIGINS` trong Railway Variables:
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com
```

### 8.3. Enable HTTPS Only

```bash
HTTPS_ONLY=true
```

Railway tự động cung cấp SSL certificate.

### 8.4. Setup Rate Limiting

Trong Railway Variables:
```bash
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

---

## 📊 Monitoring & Logging

### 9.1. Railway Logs

View logs real-time:
```bash
railway logs
```

Hoặc trong Railway Dashboard → **Logs** tab.

### 9.2. Application Logs

Logs được lưu trong Volume:
```bash
railway run cat /data/logs/chatbot.log
```

### 9.3. Database Monitoring

Supabase Dashboard → **Database** → **Query Performance**

Monitor:
- Active connections
- Query performance
- Slow queries
- Index usage

### 9.4. Redis Monitoring

Railway Redis Dashboard:
- Memory usage
- Hit/Miss ratio
- Connected clients

---

## 🔄 Backup & Recovery

### 10.1. Supabase Automatic Backups

Supabase Pro plan có daily backups.

**Free tier**: Setup manual backups.

### 10.2. Manual Database Backup

```bash
# Dump database
railway run pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Upload to Supabase Storage
railway run python scripts/backup_to_supabase.py
```

### 10.3. Volume Backup

Railway Volumes are **not backed up automatically**.

Backup embeddings:
```bash
railway run tar -czf embeddings_backup.tar.gz /data/embeddings
```

Download backup:
```bash
railway connect
# Then use scp or railway volume export
```

---

## 🐛 Troubleshooting

### Issue 1: Database Connection Failed

**Symptom:**
```
❌ PostgreSQL connection failed: could not connect to server
```

**Solutions:**
1. Verify `DATABASE_URL` trong Railway Variables
2. Check Supabase database status
3. Ensure using **Direct connection** (not Pooling)
4. Test connection:
```bash
railway run python -c "from config.settings import DATABASE_URL; print(DATABASE_URL)"
```

### Issue 2: pgvector Extension Not Found

**Symptom:**
```
ERROR: extension "vector" does not exist
```

**Solution:**
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue 3: Volume Not Mounted

**Symptom:**
```
FileNotFoundError: /data/embeddings/faiss_index.index
```

**Solutions:**
1. Verify Volume mounted at `/data`
2. Check `RAILWAY_VOLUME_MOUNT=/data` in Variables
3. Rebuild embeddings:
```bash
railway run python scripts/build_embeddings.py
```

### Issue 4: Redis Connection Timeout

**Symptom:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solutions:**
1. Check Redis service is running
2. Verify `REDIS_URL` is set
3. Test connection:
```bash
railway run python -c "
import redis
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
print(r.ping())
"
```

### Issue 5: Slow Startup (>300s timeout)

**Symptom:**
```
Deployment failed: Health check timeout
```

**Solutions:**
1. Increase `healthcheckTimeout` trong `railway.json`:
```json
"healthcheckTimeout": 600
```
2. Pre-build embeddings locally và upload Volume
3. Reduce `TOP_K_RESULTS` trong RAG config

---

## 📈 Scaling Recommendations

### Performance Optimization

1. **Redis Caching**: Đã enable, giảm 80% database queries
2. **Embeddings**: Store trong Redis cho fast retrieval
3. **Connection Pooling**: 
   ```python
   pool_size=10
   max_overflow=20
   ```

### Vertical Scaling

Railway Plan tiers:
- **Hobby**: 512MB RAM, 0.5 vCPU
- **Pro**: 8GB RAM, 8 vCPU (recommended cho production)

### Horizontal Scaling

Enable trong `railway.json`:
```json
"numReplicas": 2
```

**Lưu ý**: Cần Redis cho session sharing giữa replicas.

---

## 🔗 Related Documentation

- [SECURITY_ASSESSMENT.md](../SECURITY_ASSESSMENT.md) - Security checklist
- [USER_MANAGEMENT_SETUP.md](USER_MANAGEMENT_SETUP.md) - User management guide
- [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md) - Operations procedures

---

## 📧 Support

Nếu gặp vấn đề:
1. Check Railway logs: `railway logs`
2. Check Supabase logs trong Dashboard
3. Review [Troubleshooting](#-troubleshooting) section
4. Create GitHub issue với logs đầy đủ

---

**Last Updated**: 15/01/2026  
**Deployment Platform**: Railway  
**Database**: Supabase PostgreSQL  
**Status**: Production Ready ✅
