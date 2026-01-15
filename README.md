# University Chatbot - Hệ Thống Chatbot Tuyển Sinh

Hệ thống chatbot tư vấn tuyển sinh cho Trường Đại học An ninh Nhân dân sử dụng công nghệ RAG (Retrieval-Augmented Generation).

---

## 📋 Mục Lục

1. [Giới thiệu](#giới-thiệu)
2. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
3. [Cài đặt & Triển khai](#cài-đặt--triển-khai)
4. [Cấu hình hệ thống](#cấu-hình-hệ-thống)
5. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
6. [API Reference](#api-reference)
7. [Triển khai Production](#triển-khai-production)
8. [Xử lý sự cố](#xử-lý-sự-cố)

---

## Giới Thiệu

### Tính năng chính

| Tính năng | Mô tả |
|-----------|-------|
| 🤖 **Trả lời tự động** | Sử dụng AI để trả lời câu hỏi về tuyển sinh |
| 🔍 **Tìm kiếm thông minh** | Semantic search trong tài liệu tuyển sinh |
| 🇻🇳 **Hỗ trợ tiếng Việt** | Tối ưu hóa embedding và xử lý tiếng Việt |
| 🔐 **Bảo mật** | JWT authentication, RBAC, HTTPS |
| 📊 **Analytics** | Theo dõi và phân tích câu hỏi người dùng |
| 🔄 **RESTful API** | Dễ dàng tích hợp với ứng dụng khác |

### Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS
┌─────────────────────────────▼───────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Auth Module │  │  RAG Engine │  │ User Management         │  │
│  └─────────────┘  └──────┬──────┘  └─────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
┌─────────┐         ┌─────────────┐        ┌─────────┐
│ Supabase│         │   Gemini/   │        │  Redis  │
│PostgreSQL│        │   Ollama    │        │  Cache  │
│+ pgvector│         └─────────────┘        └─────────┘
└─────────┘
```

---

## Yêu Cầu Hệ Thống

### 1. Yêu cầu phần cứng

#### Môi trường Development

| Thành phần | Tối thiểu | Khuyến nghị |
|------------|-----------|-------------|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 20 GB SSD | 50 GB SSD |
| **GPU** | Không bắt buộc | NVIDIA GPU 8GB+ (cho Ollama local) |

#### Môi trường Production (Railway)

| Thành phần | Tier | Khuyến nghị |
|------------|------|-------------|
| **Compute** | Hobby | Pro (8GB RAM, 8 vCPU) |
| **PostgreSQL** | Supabase Free | Supabase Pro |
| **Redis** | Railway Redis | 100MB+ |
| **Volume** | 1 GB | 5 GB (cho PDFs và embeddings) |

### 2. Yêu cầu phần mềm

#### Hệ điều hành
- **Windows**: 10/11 (64-bit)
- **Linux**: Ubuntu 20.04+, Debian 11+
- **macOS**: 12.0+ (Monterey)

#### Runtime & Tools

| Phần mềm | Phiên bản | Mục đích |
|----------|-----------|----------|
| **Python** | 3.11+ | Runtime chính |
| **Conda/Pip** | Latest | Quản lý packages |
| **Git** | 2.30+ | Version control |
| **Docker** | 24.0+ | Containerization (optional) |
| **Node.js** | 18+ | Frontend development |

#### Database & Services

| Service | Phiên bản | Mục đích |
|---------|-----------|----------|
| **PostgreSQL** | 15+ | Database chính (via Supabase) |
| **pgvector** | 0.5+ | Vector similarity search |
| **Redis** | 7.0+ | Caching layer |

#### LLM Provider (chọn 1)

| Provider | Model | Yêu cầu |
|----------|-------|---------|
| **Gemini** (Khuyến nghị) | gemini-2.0-flash | API Key từ Google AI Studio |
| **Ollama** (Local) | llama3, qwen2.5 | 16GB+ RAM, GPU khuyến nghị |

---

## Cài Đặt & Triển Khai

### Bước 1: Clone Repository

```bash
# Clone project
git clone https://github.com/yenlenhi/PUS_chatbot.git
cd PUS_chatbot

# Hoặc tên khác nếu có
git clone <your-repo-url>
cd uni_bot
```

### Bước 2: Tạo môi trường Python

#### Option A: Sử dụng Conda (Khuyến nghị)

```bash
# Tạo environment với Python 3.11
conda create -n uni_bot python=3.11 -y

# Kích hoạt environment
conda activate uni_bot

# Verify Python version
python --version
# Output: Python 3.11.x
```

#### Option B: Sử dụng venv

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
.\venv\Scripts\activate

# Kích hoạt (Linux/macOS)
source venv/bin/activate
```

### Bước 3: Cài đặt Dependencies (Build)

```bash
# Cài đặt tất cả dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|langchain|faiss"
```

**Dependencies chính:**

| Package | Version | Mục đích |
|---------|---------|----------|
| fastapi | 0.104.1 | Web framework |
| langchain | 0.1.0 | RAG pipeline |
| faiss-cpu | 1.12.0 | Vector database |
| sentence-transformers | 3.0.1 | Vietnamese embeddings |
| sqlalchemy | 2.0.23 | ORM |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| redis | 5.0.1 | Cache client |
| python-jose | 3.3.0 | JWT handling |

### Bước 4: Cấu hình Environment Variables

```bash
# Copy template
cp .env.example .env

# Hoặc cho Railway deployment
cp .env.railway .env
```

**Chỉnh sửa file `.env`:**

```bash
# ===== DATABASE (Supabase PostgreSQL) =====
DATABASE_URL=postgresql://postgres:[PASSWORD]@[PROJECT].supabase.co:5432/postgres

# ===== SUPABASE STORAGE =====
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_STORAGE_BUCKET=chat-attachments

# ===== SECURITY (CRITICAL!) =====
# Generate: python scripts/generate_jwt_secret.py
JWT_SECRET_KEY=your-64-character-hex-string-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ===== LLM PROVIDER =====
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...

# Alternative: Ollama (local)
# LLM_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3

# ===== REDIS (Optional - Railway auto-provides) =====
# REDIS_URL=redis://localhost:6379

# ===== API CONFIG =====
API_HOST=0.0.0.0
API_PORT=8000
HTTPS_ONLY=false
ALLOWED_ORIGINS=*
```

### Bước 5: Khởi tạo Database

```bash
# Verify database connection
python scripts/verify_railway_connection.py

# Expected output:
# ✅ PostgreSQL connected
# ✅ pgvector extension is INSTALLED
# ✅ Write permissions verified
```

```bash
# Khởi tạo bảng users và tạo admin account
python scripts/init_user_database.py

# Expected output:
# ✅ Tables created successfully
# ✅ Admin user created: admin
# ✅ Regular user created: user
```

**Default credentials (ĐỔI NGAY SAU KHI CÀI ĐẶT!):**

| Username | Password | Roles |
|----------|----------|-------|
| admin | Admin123 | admin, user |
| user | User1234 | user |

### Bước 6: Xử lý dữ liệu PDF

```bash
# Đặt file PDF vào thư mục data/pdfs/
# Ví dụ: data/pdfs/tuyen_sinh_2025.pdf

# Xử lý và tạo chunks
python scripts/process_pdfs.py

# Xây dựng embeddings và FAISS index
python scripts/build_embeddings.py

# Verify embeddings
python -c "import faiss; index = faiss.read_index('data/embeddings/faiss_index.index'); print(f'Vectors: {index.ntotal}')"
```

### Bước 7: Chạy Server

```bash
# Development mode (với auto-reload)
python main.py

# Hoặc sử dụng uvicorn trực tiếp
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Verify server:**

```bash
# Health check
curl http://localhost:8000/health
# {"status":"healthy","service":"University Chatbot API","version":"1.0.0"}

# API Documentation
# Mở browser: http://localhost:8000/docs
```

---

## Cấu Hình Hệ Thống

### 1. Cấu hình chính (config/settings.py)

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Optional |
| `JWT_SECRET_KEY` | Secret key cho JWT tokens | Required |
| `LLM_PROVIDER` | "gemini" hoặc "ollama" | gemini |
| `EMBEDDING_MODEL` | Mô hình embedding | bkai-foundation-models/vietnamese-embedding-v1 |

### 2. Cấu hình RAG

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `CHUNK_SIZE` | Kích thước mỗi chunk (tokens) | 500 |
| `CHUNK_OVERLAP` | Overlap giữa các chunks | 50 |
| `TOP_K_RESULTS` | Số kết quả trả về | 15 |
| `SIMILARITY_THRESHOLD` | Ngưỡng similarity tối thiểu | 0.35 |
| `DENSE_WEIGHT` | Trọng số dense retrieval | 0.7 |

### 3. Cấu hình Security

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `HTTPS_ONLY` | Bắt buộc HTTPS | false (dev), true (prod) |
| `ALLOWED_ORIGINS` | CORS origins | * |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `RATE_LIMIT_REQUESTS` | Max requests/window | 100 |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | 60 |

### 4. Cấu hình Redis Cache

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `ENABLE_REDIS_CACHE` | Bật/tắt caching | true |
| `REDIS_CACHE_TTL` | Cache TTL (seconds) | 86400 |
| `REDIS_CACHE_PREFIX` | Prefix cho cache keys | unibot: |

---

## Hướng Dẫn Sử Dụng

### 1. Xử lý PDF mới

```bash
# Thêm PDF vào thư mục watch
cp new_document.pdf data/new_pdf/

# Xử lý incremental
python scripts/process_incremental_pdfs.py

# Hoặc rebuild toàn bộ
python scripts/build_embeddings.py
```

### 2. Quản lý Users

```bash
# Đăng nhập lấy token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123"}'

# Đổi password
curl -X POST "http://localhost:8000/api/users/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password":"Admin123","new_password":"NewSecurePassword123"}'
```

### 3. Chat API

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Điều kiện tuyển sinh vào trường là gì?",
    "conversation_id": "optional-id"
  }'
```

---

## API Reference

### Authentication

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/auth/login` | POST | Đăng nhập (JSON) |
| `/auth/token` | POST | Đăng nhập (OAuth2 form) |

### User Management

| Endpoint | Method | Auth | Mô tả |
|----------|--------|------|-------|
| `/api/users/me` | GET | User | Thông tin user hiện tại |
| `/api/users/change-password` | POST | User | Đổi password |
| `/api/users/admin/users` | GET | Admin | Danh sách users |
| `/api/users/admin/users` | POST | Admin | Tạo user mới |
| `/api/users/admin/users/{id}` | PUT | Admin | Cập nhật user |
| `/api/users/admin/users/{id}` | DELETE | Admin | Xóa user |

### Chat & Search

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/v1/chat` | POST | Chat với AI |
| `/api/v1/search` | POST | Tìm kiếm documents |
| `/api/v1/stats` | GET | Thống kê hệ thống |

### System

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc documentation |

---

## Triển Khai Production

### Railway + Supabase Deployment

#### 1. Setup Supabase

```sql
-- Chạy trong SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

Copy connection string: `Settings → Database → Connection string (Direct)`

#### 2. Setup Railway

1. Connect GitHub repository
2. Add **Redis** service
3. Add **Volume** mount tại `/data` (2GB+)
4. Configure **Environment Variables**:

```bash
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=<generate-new>
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
GEMINI_API_KEY=...
ALLOWED_ORIGINS=https://your-frontend.com
HTTPS_ONLY=true
RAILWAY_VOLUME_MOUNT=/data
```

#### 3. Deploy

```bash
git push origin main
# Railway auto-deploys
```

#### 4. Verify

```bash
curl https://your-app.railway.app/health
```

📚 **Chi tiết**: [docs/deployment/RAILWAY_SUPABASE_DEPLOYMENT.md](docs/deployment/RAILWAY_SUPABASE_DEPLOYMENT.md)

---

## Xử Lý Sự Cố

### 1. Database Connection Failed

```bash
# Verify DATABASE_URL
python -c "from config.settings import DATABASE_URL; print(DATABASE_URL[:50])"

# Test connection
python scripts/verify_railway_connection.py
```

**Nguyên nhân thường gặp:**
- Sai connection string (dùng Pooling thay vì Direct)
- Supabase project paused
- IP không được whitelist

### 2. pgvector Extension Missing

```sql
-- Chạy trong Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 3. Embeddings Not Found

```bash
# Rebuild embeddings
python scripts/build_embeddings.py

# Verify
ls -la data/embeddings/
```

### 4. Authentication Failed

```bash
# Verify JWT secret
python -c "from config.settings import JWT_SECRET_KEY; print(len(JWT_SECRET_KEY))"
# Should be 64 characters

# Re-init users
python scripts/init_user_database.py
```

### 5. Memory Issues

```bash
# Reduce batch size trong config
EMBEDDING_BATCH_SIZE=16

# Monitor memory
python -c "import psutil; print(f'{psutil.virtual_memory().percent}%')"
```

---

## Cấu Trúc Thư Mục

```
uni_bot/
├── 📁 config/
│   └── settings.py           # Cấu hình hệ thống
├── 📁 data/
│   ├── pdfs/                 # File PDF nguồn
│   ├── new_pdf/              # Watch directory
│   ├── processed/            # Chunks đã xử lý
│   └── embeddings/           # FAISS index
├── 📁 docs/
│   ├── deployment/           # Hướng dẫn deploy
│   └── guides/               # Các hướng dẫn khác
├── 📁 frontend/              # Next.js frontend
├── 📁 scripts/
│   ├── init_user_database.py # Khởi tạo database
│   ├── build_embeddings.py   # Xây dựng embeddings
│   ├── process_pdfs.py       # Xử lý PDF
│   └── verify_railway_connection.py
├── 📁 src/
│   ├── api/                  # FastAPI routes
│   ├── auth/                 # JWT authentication
│   ├── middleware/           # Security middleware
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic
│   └── utils/                # Utilities
├── 📁 tests/                 # Unit tests
├── .env.example              # Template environment
├── .env.railway              # Railway template
├── main.py                   # Application entry
├── railway.json              # Railway config
├── railway_startup.sh        # Startup script
└── requirements.txt          # Dependencies
```

---

## Development

### Chạy Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

### Code Formatting

```bash
black src/ scripts/ main.py
flake8 src/ scripts/ main.py
```

### Generate JWT Secret

```bash
python scripts/generate_jwt_secret.py
```

---

## Đóng Góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "Add new feature"`
4. Push to branch: `git push origin feature/new-feature`
5. Tạo Pull Request

---

## License

MIT License - Xem [LICENSE](LICENSE) để biết thêm chi tiết.

---

## Liên Hệ & Hỗ Trợ

- 📚 **Documentation**: [docs/](docs/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 📧 **Email**: support@example.com

---

**Phiên bản**: 1.0.0  
**Cập nhật**: 15/01/2026  
**Trạng thái**: Production Ready ✅
