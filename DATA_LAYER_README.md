# 🐘 Uni Bot Data Layer - PostgreSQL + pgvector Migration

## 📌 Tóm Tắt

Hệ thống Uni Bot đã được cải thiện với Data Layer mới sử dụng **PostgreSQL + pgvector** thay vì SQLite + FAISS. Hệ thống mới hỗ trợ:

- ✅ **Hybrid Retrieval**: Kết hợp dense (semantic) + sparse (keyword) search
- ✅ **Automatic Ingestion**: Tự động phát hiện và xử lý PDF mới
- ✅ **Better Scalability**: PostgreSQL hỗ trợ concurrent connections
- ✅ **Persistent Storage**: Dữ liệu được lưu trữ an toàn
- ✅ **Performance**: Vector indexes cho tìm kiếm nhanh

---

## 🚀 Quick Start (5 Phút)

### 1️⃣ Setup PostgreSQL
```bash
# Copy environment file
cp .env.example .env

# Start Docker containers
docker-compose up -d

# Verify
docker-compose ps
```

### 2️⃣ Install Dependencies
```bash
conda activate uni_bot
pip install -r requirements.txt
```

### 3️⃣ Test Connection
```bash
powershell python test_postgres_connection.py
```

**Kỳ vọng**: ✅ All tests passed!

---

## 📚 Documentation

### 🔧 Setup & Configuration
- **[POSTGRES_SETUP_GUIDE.md](POSTGRES_SETUP_GUIDE.md)** - Chi tiết setup PostgreSQL + pgvector

### 📊 Architecture & Migration
- **[DATA_LAYER_MIGRATION_SUMMARY.md](DATA_LAYER_MIGRATION_SUMMARY.md)** - Tổng quan migration
- **[DATA_LAYER_IMPLEMENTATION_COMPLETE.md](DATA_LAYER_IMPLEMENTATION_COMPLETE.md)** - Tóm tắt hoàn thành

### 🔄 Implementation Steps
- **[STEP_7_RAG_SERVICE_UPDATE.md](STEP_7_RAG_SERVICE_UPDATE.md)** - Cập nhật RAG Service
- **[STEP_8_TESTING_GUIDE.md](STEP_8_TESTING_GUIDE.md)** - Testing guide

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Frontend (Next.js)                    │
│   - Chat Interface                      │
│   - Document Display                    │
└──────────────┬──────────────────────────┘
               │ HTTP/REST API
┌──────────────▼──────────────────────────┐
│   Backend (FastAPI)                     │
│   - RAG Service (Orchestrator)          │
│   - Embedding Service                   │
│   - Hybrid Retrieval Service            │
│   - Ingestion Service                   │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│ PG   │  │pgvec │  │BM25  │
│ DB   │  │tor   │  │Index │
└──────┘  └──────┘  └──────┘
```

---

## 🔄 Hybrid Retrieval System

### Dense Search (pgvector)
- **Công nghệ**: Vector similarity search
- **Tốc độ**: < 100ms
- **Ưu điểm**: Semantic understanding

### Sparse Search (BM25)
- **Công nghệ**: Keyword-based ranking
- **Tốc độ**: < 50ms
- **Ưu điểm**: Exact keyword matching

### Combined Score
```
score = 0.7 * dense_score + 0.3 * sparse_score
```

---

## 📁 New Files Created

### Services
```
src/services/
├── postgres_database_service.py    # PostgreSQL operations
├── hybrid_retrieval_service.py     # Dense + Sparse search
└── ingestion_service.py            # Automatic PDF processing
```

### Configuration
```
├── docker-compose.yml              # Docker setup
├── scripts/init_postgres.sql       # Database schema
├── config/settings.py              # Updated config
└── .env.example                    # Environment variables
```

### Testing
```
├── test_postgres_connection.py     # Connection test
└── STEP_8_TESTING_GUIDE.md        # Testing guide
```

---

## ⚙️ Configuration

### PostgreSQL
```env
POSTGRES_USER=uni_bot_user
POSTGRES_PASSWORD=uni_bot_password
POSTGRES_DB=uni_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Hybrid Retrieval
```env
DENSE_WEIGHT=0.7                    # 70% dense, 30% sparse
DENSE_SIMILARITY_THRESHOLD=0.35
SPARSE_SIMILARITY_THRESHOLD=0.1
```

### Ingestion Service
```env
PDF_WATCH_DIR=data/pdfs
PROCESSED_PDF_DIR=data/processed
INGESTION_CHECK_INTERVAL=60
AUTO_INGEST_ON_STARTUP=true
```

---

## 🧪 Testing

### Phase 1: Infrastructure
```bash
powershell python test_postgres_connection.py
```

### Phase 2: Services
```bash
powershell python test_postgres_service.py
powershell python test_embedding_service.py
powershell python test_hybrid_retrieval.py
```

### Phase 3: Integration
```bash
powershell python test_ingestion.py
```

### Phase 4: End-to-End
```bash
powershell python test_rag_pipeline.py
powershell python test_api_endpoints.py
```

---

## 📊 Performance

| Operation | Expected Time |
|-----------|---------------|
| Dense search | < 100ms |
| Sparse search | < 50ms |
| Hybrid search | < 150ms |
| Embedding generation | < 500ms |
| Full RAG pipeline | < 2s |

---

## 🆘 Troubleshooting

### PostgreSQL không khởi động
```bash
docker-compose down -v
docker-compose up -d
```

### pgvector extension không tìm thấy
```bash
docker exec -it uni_bot_postgres psql -U uni_bot_user -d uni_bot_db
CREATE EXTENSION IF NOT EXISTS vector;
```

### Connection refused
- Kiểm tra `.env` credentials
- Kiểm tra PostgreSQL container: `docker-compose ps`
- Kiểm tra port 5432 availability

---

## 📋 Implementation Status

### ✅ Completed (Bước 1-6)
- [x] Docker Compose setup
- [x] PostgreSQL + pgvector
- [x] Database schema
- [x] PostgreSQL Database Service
- [x] Hybrid Retrieval Service
- [x] Ingestion Service
- [x] Dependencies updated
- [x] Configuration updated

### 📅 TODO (Bước 7-8)
- [ ] Update RAG Service
- [ ] Test & Verification
- [ ] Production Deployment

---

## 🚀 Next Steps

1. **Đọc**: [STEP_7_RAG_SERVICE_UPDATE.md](STEP_7_RAG_SERVICE_UPDATE.md)
2. **Cập nhật**: `src/services/rag_service.py`
3. **Test**: Chạy test scripts
4. **Deploy**: Triển khai lên production

---

## 📞 Support

### Documentation
- [POSTGRES_SETUP_GUIDE.md](POSTGRES_SETUP_GUIDE.md) - Setup guide
- [STEP_7_RAG_SERVICE_UPDATE.md](STEP_7_RAG_SERVICE_UPDATE.md) - RAG update
- [STEP_8_TESTING_GUIDE.md](STEP_8_TESTING_GUIDE.md) - Testing guide

### External Resources
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

## 📝 Key Features

### 1. Automatic PDF Ingestion
- File watcher tự động phát hiện PDF mới
- Tự động extract text, create chunks
- Tự động generate embeddings
- Tự động insert vào database

### 2. Hybrid Search
- Dense search cho semantic understanding
- Sparse search cho keyword matching
- Configurable weights
- Better relevance

### 3. Scalability
- PostgreSQL concurrent connections
- Connection pooling
- Horizontal scaling support

### 4. Reliability
- ACID transactions
- Data persistence
- Backup & recovery

---

**Status**: ✅ Infrastructure Ready | 📅 Integration Pending

**Last Updated**: 2024-11-08