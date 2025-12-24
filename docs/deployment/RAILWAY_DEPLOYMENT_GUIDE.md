# 🚂 HƯỚNG DẪN DEPLOY LÊN RAILWAY

> Hướng dẫn chi tiết deploy hệ thống Chatbot Tư vấn Tuyển sinh lên Railway

---

## 📋 TỔNG QUAN

### Kiến trúc Deploy

```
┌─────────────────────────────────────────────────────────────┐
│                      RAILWAY PROJECT                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Frontend   │  │   Backend    │  │  PostgreSQL  │       │
│  │   Next.js    │  │   FastAPI    │  │  + pgvector  │       │
│  │   Service    │  │   Service    │  │   Service    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                  │               │
│         └────────────────┼──────────────────┘               │
│                          │                                   │
│                   Internal Network                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Gemini API  │
                    │  (External)  │
                    └──────────────┘
```

### Chi phí ước tính
- **Hobby Plan**: $5/tháng (đủ cho demo)
- **2 tháng**: ~$10 USD (~250.000 VNĐ)

---

## 🚀 BƯỚC 1: CHUẨN BỊ

### 1.1. Tạo tài khoản Railway
1. Truy cập: https://railway.app
2. Đăng ký bằng GitHub (khuyến nghị)
3. Verify email

### 1.2. Cài đặt Railway CLI (Optional)
```bash
# Windows (PowerShell)
npm install -g @railway/cli

# Hoặc dùng scoop
scoop install railway
```

### 1.3. Đăng nhập CLI
```bash
railway login
```

---

## 🗄️ BƯỚC 2: TẠO DATABASE (PostgreSQL + pgvector)

### 2.1. Tạo Project mới
1. Vào Railway Dashboard
2. Click **"New Project"**
3. Chọn **"Empty Project"**
4. Đặt tên: `uni-bot-chatbot`

### 2.2. Thêm PostgreSQL
1. Trong project, click **"+ New"**
2. Chọn **"Database"** → **"PostgreSQL"**
3. Đợi database khởi tạo (~30 giây)

### 2.3. Kích hoạt pgvector
1. Click vào PostgreSQL service
2. Vào tab **"Data"** → **"Query"**
3. Chạy SQL:

```sql
-- Kích hoạt pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Kiểm tra
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 2.4. Lấy Connection String
1. Click PostgreSQL service
2. Vào tab **"Variables"**
3. Copy `DATABASE_URL` (dạng: `postgresql://postgres:xxx@xxx.railway.app:5432/railway`)

---

## ⚙️ BƯỚC 3: DEPLOY BACKEND (FastAPI)

### 3.1. Chuẩn bị code

Đảm bảo các file sau đã có trong thư mục gốc:
- ✅ `requirements.txt`
- ✅ `main.py`
- ✅ `railway.json`
- ✅ `Procfile`
- ✅ `nixpacks.toml`

### 3.2. Thêm Backend Service

**Cách 1: Qua GitHub (Khuyến nghị)**
1. Push code lên GitHub repository
2. Trong Railway project, click **"+ New"**
3. Chọn **"GitHub Repo"**
4. Chọn repository của bạn
5. Railway sẽ tự detect là Python project

**Cách 2: Qua CLI**
```bash
cd c:\TruongVanKhai\Project\uni_bot
railway link  # Chọn project
railway up    # Deploy
```

### 3.3. ⭐ Cấu hình Volume (LƯU TRỮ PDF)

> **Quan trọng:** Railway Volume giúp lưu trữ PDF files persistent, không bị mất khi redeploy!

1. Vào Backend service → **Settings**
2. Scroll xuống phần **"Volumes"**
3. Click **"+ Add Volume"**
4. Cấu hình:
   - **Mount Path:** `/data`
   - **Size:** `5GB` (đủ cho demo)
5. Click **"Add"**

```
📁 /data (Railway Volume - Persistent)
├── pdfs/        ← PDF files uploaded
├── new_pdf/     ← New PDFs to process
├── processed/   ← Processed PDFs
└── embeddings/  ← Embedding cache
```

### 3.4. Cấu hình Environment Variables

Vào Backend service → **Variables** → Thêm các biến:

```env
# Database (dùng Reference Variable)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-32-chars-min
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# ⭐ Railway Volume Mount Path
RAILWAY_VOLUME_MOUNT=/data

# CORS (sẽ cập nhật sau khi có Frontend URL)
CORS_ORIGINS=http://localhost:3000
```

### 3.5. Cấu hình Domain
1. Vào Backend service → **Settings**
2. Trong **Networking** → **Generate Domain**
3. Sẽ có domain dạng: `uni-bot-api-production.up.railway.app`

---

## 🖥️ BƯỚC 4: DEPLOY FRONTEND (Next.js)

### 4.1. Cập nhật Frontend Environment

Tạo file `frontend/.env.production`:
```env
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
NEXT_PUBLIC_APP_NAME=Chatbot Tư Vấn Tuyển Sinh
```

### 4.2. Deploy Frontend

**Cách 1: Qua Railway Dashboard**
1. Click **"+ New"** → **"GitHub Repo"**
2. Chọn repo, set **Root Directory** = `frontend`
3. Railway auto-detect Next.js

**Cách 2: Qua CLI**
```bash
cd c:\TruongVanKhai\Project\uni_bot\frontend
railway link
railway up
```

### 4.3. Cấu hình Frontend Variables

```env
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app/api
```

### 4.4. Generate Domain
- Vào Settings → Generate Domain
- Sẽ có: `uni-bot-frontend-production.up.railway.app`

---

## 🔧 BƯỚC 5: CẤU HÌNH CORS VÀ KẾT NỐI

### 5.1. Cập nhật Backend CORS

Quay lại Backend service → Variables, cập nhật:
```env
CORS_ORIGINS=https://your-frontend.up.railway.app,http://localhost:3000
FRONTEND_URL=https://your-frontend.up.railway.app
```

### 5.2. Cập nhật Frontend API URL

Frontend service → Variables:
```env
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

### 5.3. Redeploy cả 2 services
- Click **"Redeploy"** trên mỗi service

---

## 📊 BƯỚC 6: KHỞI TẠO DATABASE

### 6.1. Chạy Migration

Có thể chạy qua Railway CLI:
```bash
railway run python -c "from src.models.database import init_db; init_db()"
```

Hoặc vào PostgreSQL Query tab và chạy SQL tạo tables.

### 6.2. Import dữ liệu (nếu có)

```bash
# Export từ local
pg_dump -h localhost -U postgres uni_bot > backup.sql

# Import lên Railway (lấy connection string từ Railway)
psql "postgresql://postgres:xxx@xxx.railway.app:5432/railway" < backup.sql
```

---

## ✅ BƯỚC 7: KIỂM TRA

### 7.1. Test Backend API
```bash
# Health check
curl https://your-backend.up.railway.app/health

# Test chat API
curl -X POST https://your-backend.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào"}'
```

### 7.2. Test Frontend
- Truy cập: `https://your-frontend.up.railway.app`
- Thử chat với bot

---

## 🔍 TROUBLESHOOTING

### Lỗi thường gặp

**1. Build failed - Missing dependencies**
```bash
# Kiểm tra requirements.txt đầy đủ
pip freeze > requirements.txt
```

**2. Database connection refused**
```bash
# Kiểm tra DATABASE_URL đúng format
# Dùng Reference Variable: ${{Postgres.DATABASE_URL}}
```

**3. CORS error**
```bash
# Đảm bảo CORS_ORIGINS chứa đúng frontend URL
# Bao gồm cả http:// và https://
```

**4. pgvector not found**
```sql
-- Chạy trong PostgreSQL Query
CREATE EXTENSION IF NOT EXISTS vector;
```

**5. Port binding error**
```python
# Đảm bảo main.py dùng PORT từ env
import os
port = int(os.environ.get("PORT", 8000))
```

### Xem Logs
1. Click vào service
2. Vào tab **"Logs"**
3. Hoặc dùng CLI: `railway logs`

---

## 📱 CUSTOM DOMAIN (Optional)

Nếu muốn dùng domain riêng:

1. Vào Service → Settings → Custom Domain
2. Thêm domain: `chatbot.yourdomain.com`
3. Cấu hình DNS:
   - Type: CNAME
   - Name: chatbot
   - Value: `your-service.up.railway.app`

---

## 💡 TIPS TỐI ƯU

### 1. Giảm chi phí
```yaml
# Tắt service khi không dùng
# Railway tính tiền theo usage
```

### 2. Sleep mode
- Railway tự động sleep sau 15 phút không hoạt động (Hobby plan)
- Request đầu tiên sẽ mất ~10-20s để wake up

### 3. Monitor usage
- Vào Project Settings → Usage
- Theo dõi bandwidth và compute hours

---

## 🎉 HOÀN THÀNH!

Sau khi deploy thành công, bạn sẽ có:

| Service | URL |
|---------|-----|
| Frontend | `https://uni-bot-frontend-xxx.up.railway.app` |
| Backend | `https://uni-bot-api-xxx.up.railway.app` |
| API Docs | `https://uni-bot-api-xxx.up.railway.app/docs` |

---

## 📞 HỖ TRỢ

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: Tạo issue trong repo

---

*Cập nhật: Tháng 12/2024*
