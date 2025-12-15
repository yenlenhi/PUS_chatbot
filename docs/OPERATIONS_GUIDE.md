# HƯỚNG DẪN VẬN HÀNH HỆ THỐNG

## 1. YÊU CẦU HỆ THỐNG

### 1.1. Phần cứng tối thiểu

**Development Environment**
- CPU: 4 cores (Intel i5/AMD Ryzen 5 hoặc tương đương)
- RAM: 8GB (khuyến nghị 16GB)
- Storage: 20GB trống (SSD khuyến nghị)
- GPU: Không bắt buộc (nhưng tăng tốc embedding generation)

**Production Environment**
- CPU: 8 cores
- RAM: 16GB (khuyến nghị 32GB)
- Storage: 50GB+ SSD
- GPU: NVIDIA GPU với CUDA support (khuyến nghị để tăng tốc)
- Network: 100Mbps+ stable connection

### 1.2. Phần mềm cần thiết

```
- Python 3.10 hoặc mới hơn
- Node.js 18+ và npm/yarn
- PostgreSQL 16+ (hoặc Docker)
- Redis 7+ (hoặc Docker)
- Docker & Docker Compose (khuyến nghị)
- Git
```

### 1.3. Tài khoản bên ngoài cần thiết

- **Google Gemini API Key**: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- **Hugging Face Account**: Để download embedding models (miễn phí)

---

## 2. CÀI ĐẶT HỆ THỐNG

### 2.1. Cài đặt bằng Docker (Khuyến nghị)

#### Bước 1: Clone repository
```bash
git clone https://github.com/VanKhaiii/UniChatBot.git
cd UniChatBot
```

#### Bước 2: Tạo file .env
```bash
# Copy file .env mẫu
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

Nội dung file .env:
```bash
# Database Configuration
POSTGRES_USER=uni_bot_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=uni_bot_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_CACHE_TTL=604800
ENABLE_REDIS_CACHE=true

# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent
GEMINI_MAX_OUTPUT_TOKENS=8192
GEMINI_TEMPERATURE=0.7
ENABLE_GEMINI_NORMALIZATION=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Security
JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Admin User (First Time Setup)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com

# Embedding Model
EMBEDDING_MODEL=keepitreal/vietnamese-sbert
EMBEDDING_DIMENSION=384

# Retrieval Settings
TOP_K_RESULTS=5
DENSE_WEIGHT=0.7
DENSE_SIMILARITY_THRESHOLD=0.7
SPARSE_SIMILARITY_THRESHOLD=0.5
```

#### Bước 3: Build và start containers
```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Kiểm tra logs
docker-compose logs -f
```

#### Bước 4: Verify installation
```bash
# Check containers status
docker-compose ps

# Should see:
# - uni_bot_postgres (healthy)
# - uni_bot_redis (running)
# - uni_bot_backend (running)
# - uni_bot_frontend (running)

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

#### Bước 5: Khởi tạo database
```bash
# Run database migrations
docker-compose exec backend python scripts/migrate_database_schema.py

# Verify database
docker-compose exec postgres psql -U uni_bot_user -d uni_bot_db -c "\dt"
```

### 2.2. Cài đặt Manual (Không dùng Docker)

#### Bước 1: Cài đặt PostgreSQL

**Windows:**
```powershell
# Download PostgreSQL 16 from https://www.postgresql.org/download/windows/
# Install và chọn port 5432

# Cài pgvector extension
# Download từ: https://github.com/pgvector/pgvector/releases
# Hoặc compile từ source
```

**Ubuntu/Debian:**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql-16 postgresql-contrib-16

# Install pgvector
sudo apt install postgresql-16-pgvector

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
# Install via Homebrew
brew install postgresql@16
brew install pgvector

# Start PostgreSQL
brew services start postgresql@16
```

Tạo database:
```bash
# Login as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE uni_bot_db;
CREATE USER uni_bot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE uni_bot_db TO uni_bot_user;

# Enable pgvector extension
\c uni_bot_db
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

#### Bước 2: Cài đặt Redis

**Windows:**
```powershell
# Download Redis from: https://github.com/microsoftarchive/redis/releases
# Hoặc dùng WSL2

# Hoặc dùng Docker
docker run -d -p 6379:6379 redis:7-alpine
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

#### Bước 3: Cài đặt Python dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Activate
# Windows:
.\venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; import sentence_transformers; print('OK')"
```

#### Bước 4: Cài đặt Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production (optional)
npm run build
```

#### Bước 5: Tạo file .env

```bash
# Tạo file .env ở root directory
# Copy nội dung từ phần 2.1 Bước 2
# Thay đổi:
POSTGRES_HOST=localhost
REDIS_HOST=localhost
```

#### Bước 6: Run migrations

```bash
# Activate venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Run migration script
python scripts/migrate_database_schema.py

# Verify
python scripts/check_sqlite_data.py
```

#### Bước 7: Start services

```bash
# Terminal 1: Backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Redis (if not running as service)
redis-server

# Terminal 4: PostgreSQL (if not running as service)
postgres -D /path/to/data
```

---

## 3. CẤU HÌNH HỆ THỐNG

### 3.1. Cấu hình Database

#### PostgreSQL Performance Tuning

Edit `postgresql.conf`:
```conf
# Memory Settings
shared_buffers = 256MB          # 25% of RAM
effective_cache_size = 1GB      # 50-75% of RAM
work_mem = 16MB
maintenance_work_mem = 128MB

# Connection Settings
max_connections = 100

# Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Query Planner
random_page_cost = 1.1          # For SSD
effective_io_concurrency = 200  # For SSD

# pgvector specific
shared_preload_libraries = 'vector'
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

#### Database Backup Strategy

**Daily Backup:**
```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backup/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="uni_bot_db"

# Create backup
pg_dump -U uni_bot_user -h localhost $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

Add to crontab:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup_db.sh
```

**Restore from backup:**
```bash
# Uncompress
gunzip backup_20241209_020000.sql.gz

# Restore
psql -U uni_bot_user -h localhost uni_bot_db < backup_20241209_020000.sql
```

### 3.2. Cấu hình Redis

Edit `redis.conf`:
```conf
# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (optional for cache)
save ""
appendonly no

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300

# Security
requirepass your_redis_password
bind 127.0.0.1

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

### 3.3. Cấu hình Backend

Edit `config/settings.py` để tùy chỉnh:

```python
# Retrieval Settings
TOP_K_RESULTS = 5                    # Số chunks trả về
DENSE_WEIGHT = 0.7                   # Trọng số vector search (0-1)
DENSE_SIMILARITY_THRESHOLD = 0.7     # Ngưỡng similarity cho dense
SPARSE_SIMILARITY_THRESHOLD = 0.5    # Ngưỡng similarity cho sparse

# Chunking Settings
CHUNK_SIZE = 500                     # Kích thước chunk (characters)
CHUNK_OVERLAP = 50                   # Overlap giữa chunks

# LLM Settings
GEMINI_MAX_OUTPUT_TOKENS = 8192      # Max tokens cho response
GEMINI_TEMPERATURE = 0.7             # Creativity (0-1)

# Cache Settings
REDIS_CACHE_TTL = 604800             # 7 days in seconds
ENABLE_REDIS_CACHE = True            # Enable/disable cache

# File Upload
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [".doc", ".docx", ".xlsx", ".xls", ".pdf"]
```

### 3.4. Cấu hình Frontend

Edit `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_MAX_UPLOAD_SIZE=10485760
```

---

## 4. QUẢN LÝ TÀI LIỆU

### 4.1. Upload tài liệu mới

#### Cách 1: Qua Admin Interface

1. Truy cập: `http://localhost:3000/admin`
2. Đăng nhập với admin credentials
3. Chọn "Documents" từ sidebar
4. Click "Upload New Document"
5. Chọn file PDF và upload
6. Hệ thống tự động:
   - Extract text
   - Chunk content
   - Generate embeddings
   - Index vào database

#### Cách 2: Qua API

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

#### Cách 3: Auto-ingestion (Khuyến nghị)

1. Copy file PDF vào thư mục `data/new_pdf/`
2. Ingestion Service tự động detect và process
3. Check logs để xem tiến trình:
```bash
tail -f logs/app_*.log | grep "Processing PDF"
```

### 4.2. Xem danh sách tài liệu

```bash
# Via API
curl -X GET "http://localhost:8000/api/v1/documents" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Via CLI
docker-compose exec backend python scripts/check_db_documents.py
```

### 4.3. Xóa tài liệu

**Soft Delete (Khuyến nghị):**
```bash
# Document sẽ bị đánh dấu is_active=false
curl -X DELETE "http://localhost:8000/api/v1/documents/{document_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Hard Delete:**
```sql
-- Connect to database
docker-compose exec postgres psql -U uni_bot_user -d uni_bot_db

-- Delete document và tất cả chunks/embeddings liên quan
DELETE FROM documents WHERE id = 123;
```

### 4.4. Reprocess tài liệu

Khi cần xử lý lại tài liệu với chunking strategy mới:

```bash
# Reprocess single document
curl -X POST "http://localhost:8000/api/v1/documents/{id}/reprocess" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Reprocess all documents
python scripts/process_pdfs.py
```

---

## 5. QUẢN LÝ ATTACHMENTS

### 5.1. Upload file đính kèm

```bash
curl -X POST "http://localhost:8000/api/v1/attachments/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@FORM_XIN_NGHI_HOC.doc" \
  -F "description=Form xin nghỉ học có phép quá 5 ngày" \
  -F "keywords=form,nghỉ học,đơn xin nghỉ,xin phép"
```

### 5.2. Link attachment với chunks

```bash
curl -X POST "http://localhost:8000/api/v1/attachments/{id}/link-chunks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_ids": [123, 124, 125],
    "relevance_score": 1.0
  }'
```

### 5.3. List attachments

```bash
curl -X GET "http://localhost:8000/api/v1/attachments?keywords=form,nghỉ học" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 6. MONITORING VÀ TROUBLESHOOTING

### 6.1. Health Check

```bash
# Backend health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "models": "loaded"
}
```

### 6.2. Xem Logs

**Docker:**
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

**Manual installation:**
```bash
# Backend logs
tail -f logs/app_*.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log

# Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### 6.3. Common Issues

#### Issue 1: Backend không start được

**Triệu chứng:**
```
RuntimeError: Could not connect to database
```

**Giải pháp:**
```bash
# 1. Check PostgreSQL running
docker-compose ps postgres
# hoặc
sudo systemctl status postgresql

# 2. Check connection
psql -U uni_bot_user -h localhost -d uni_bot_db

# 3. Verify credentials in .env
cat .env | grep POSTGRES

# 4. Check logs
docker-compose logs postgres
```

#### Issue 2: Embedding model không load được

**Triệu chứng:**
```
Failed to load embedding model: keepitreal/vietnamese-sbert
```

**Giải pháp:**
```bash
# 1. Check disk space
df -h

# 2. Manual download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('keepitreal/vietnamese-sbert')"

# 3. Use fallback model
# Edit .env:
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

#### Issue 3: Redis connection failed

**Triệu chứng:**
```
Cache service not connected, running without cache
```

**Giải pháp:**
```bash
# 1. Check Redis running
docker-compose ps redis
# hoặc
sudo systemctl status redis

# 2. Test connection
redis-cli ping
# Expected: PONG

# 3. Disable cache nếu không cần
# Edit .env:
ENABLE_REDIS_CACHE=false
```

#### Issue 4: Gemini API errors

**Triệu chứng:**
```
Error calling Gemini API: 401 Unauthorized
```

**Giải pháp:**
```bash
# 1. Verify API key
curl -H "Content-Type: application/json" \
  -H "x-goog-api-key: YOUR_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'

# 2. Check quota
# Visit: https://makersuite.google.com/app/apikey

# 3. Use Ollama as fallback
# Edit .env:
LLM_PROVIDER=ollama
```

#### Issue 5: Slow query response

**Triệu chứng:**
- Response time > 5 seconds
- Timeout errors

**Giải pháp:**
```bash
# 1. Check cache hit rate
docker-compose exec backend python -c "
from src.services.cache_service import CacheService
cache = CacheService()
print(cache.stats())
"

# 2. Check database indexes
docker-compose exec postgres psql -U uni_bot_user -d uni_bot_db -c "
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('embeddings', 'chunks');
"

# 3. Rebuild BM25 index
curl -X POST "http://localhost:8000/api/v1/admin/rebuild-index" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Reduce TOP_K_RESULTS
# Edit .env:
TOP_K_RESULTS=3
```

#### Issue 6: Out of memory

**Triệu chứng:**
```
Killed
MemoryError
```

**Giải pháp:**
```bash
# 1. Check memory usage
docker stats

# 2. Limit Docker memory
# Edit docker-compose.yml:
services:
  backend:
    mem_limit: 4g
    
# 3. Use smaller model
EMBEDDING_MODEL=all-MiniLM-L6-v2  # 384 dim
# Instead of: sentence-transformers/paraphrase-multilingual-mpnet-base-v2  # 768 dim

# 4. Reduce batch size
# Edit config/settings.py:
EMBEDDING_BATCH_SIZE = 16  # default: 32
```

### 6.4. Performance Monitoring

#### Monitor response times

```bash
# Via logs
grep "Response time" logs/app_*.log | tail -20

# Via analytics API
curl -X GET "http://localhost:8000/api/v1/analytics/performance" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Monitor database size

```bash
docker-compose exec postgres psql -U uni_bot_user -d uni_bot_db -c "
SELECT 
    pg_size_pretty(pg_database_size('uni_bot_db')) as db_size,
    pg_size_pretty(pg_total_relation_size('embeddings')) as embeddings_size,
    pg_size_pretty(pg_total_relation_size('chunks')) as chunks_size;
"
```

#### Monitor cache hit rate

```python
# scripts/check_cache_stats.py
from src.services.cache_service import CacheService

cache = CacheService()
stats = cache.stats()

print(f"Cache Hit Rate: {stats['hit_rate']:.2%}")
print(f"Total Keys: {stats['keys']}")
print(f"Memory Used: {stats['memory_used']}")
```

---

## 7. BACKUP VÀ RECOVERY

### 7.1. Backup Strategy

**Full Backup (Nightly):**
```bash
#!/bin/bash
# scripts/full_backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/$DATE"
mkdir -p $BACKUP_DIR

# 1. Database backup
docker-compose exec -T postgres pg_dump -U uni_bot_user uni_bot_db | gzip > $BACKUP_DIR/database.sql.gz

# 2. Files backup
tar -czf $BACKUP_DIR/data.tar.gz data/

# 3. Config backup
tar -czf $BACKUP_DIR/config.tar.gz .env config/

# 4. Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR s3://your-bucket/backups/$DATE/ --recursive

echo "Backup completed: $BACKUP_DIR"
```

**Incremental Backup:**
```bash
# Chỉ backup files mới/thay đổi trong 24h qua
find data/ -mtime -1 -type f | tar -czf incremental_$(date +%Y%m%d).tar.gz -T -
```

### 7.2. Restore from Backup

```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_DATE="20241209"
BACKUP_DIR="/backup/$BACKUP_DATE"

# 1. Stop services
docker-compose down

# 2. Restore database
gunzip < $BACKUP_DIR/database.sql.gz | docker-compose exec -T postgres psql -U uni_bot_user uni_bot_db

# 3. Restore files
tar -xzf $BACKUP_DIR/data.tar.gz -C ./

# 4. Restore config
tar -xzf $BACKUP_DIR/config.tar.gz -C ./

# 5. Restart services
docker-compose up -d

echo "Restore completed"
```

### 7.3. Disaster Recovery Plan

**Scenario 1: Database corruption**
```bash
# 1. Stop backend
docker-compose stop backend

# 2. Restore database from latest backup
./scripts/restore.sh

# 3. Verify data integrity
python scripts/check_data_integrity.py

# 4. Restart backend
docker-compose start backend
```

**Scenario 2: Complete system failure**
```bash
# 1. Provision new server
# 2. Install Docker & dependencies
# 3. Clone repository
# 4. Restore from backup
./scripts/restore.sh
# 5. Verify and start
docker-compose up -d
```

---

## 8. SCALING & OPTIMIZATION

### 8.1. Horizontal Scaling

#### Setup Load Balancer (nginx)

**nginx.conf:**
```nginx
upstream backend {
    least_conn;
    server backend1:8000 weight=1;
    server backend2:8000 weight=1;
    server backend3:8000 weight=1;
}

server {
    listen 80;
    server_name chatbot.university.edu.vn;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**docker-compose.yml (scaled):**
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
  
  backend:
    build: .
    deploy:
      replicas: 3
    depends_on:
      - postgres
      - redis
```

Start with scale:
```bash
docker-compose up -d --scale backend=3
```

### 8.2. Database Optimization

#### Vacuum and Analyze
```bash
# Weekly maintenance
docker-compose exec postgres psql -U uni_bot_user -d uni_bot_db -c "
VACUUM ANALYZE embeddings;
VACUUM ANALYZE chunks;
VACUUM ANALYZE documents;
"
```

#### Reindex
```bash
docker-compose exec postgres psql -U uni_bot_user -d uni_bot_db -c "
REINDEX TABLE embeddings;
REINDEX TABLE chunks;
"
```

### 8.3. Cache Optimization

#### Increase Redis memory
```bash
# Edit redis.conf
maxmemory 4gb
```

#### Preload popular queries
```python
# scripts/preload_cache.py
from src.services.rag_service import RAGService

rag = RAGService()
popular_queries = [
    "Quy định về nghỉ học",
    "Học bổng khuyến khích học tập",
    "Thời gian đăng ký học phần"
]

for query in popular_queries:
    rag.query(query, session_id="preload")
    print(f"Cached: {query}")
```

---

## 9. SECURITY BEST PRACTICES

### 9.1. Production Checklist

- [ ] Change default passwords
- [ ] Use strong JWT secret (32+ characters)
- [ ] Enable HTTPS
- [ ] Set up firewall rules
- [ ] Enable database SSL
- [ ] Restrict CORS origins
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption

### 9.2. Secure Configuration

**Enable SSL for PostgreSQL:**
```conf
# postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

**Redis authentication:**
```conf
# redis.conf
requirepass your_strong_redis_password
```

**Update .env:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
REDIS_PASSWORD=your_strong_redis_password
```

---

## 10. MAINTENANCE SCHEDULE

### 10.1. Daily Tasks
- [ ] Check system health (`curl /health`)
- [ ] Monitor error logs
- [ ] Review query analytics
- [ ] Check disk space

### 10.2. Weekly Tasks
- [ ] Database vacuum and analyze
- [ ] Clear old logs (keep 30 days)
- [ ] Review slow queries
- [ ] Check backup integrity

### 10.3. Monthly Tasks
- [ ] Update dependencies
- [ ] Security audit
- [ ] Performance review
- [ ] User feedback analysis
- [ ] Database size optimization

### 10.4. Quarterly Tasks
- [ ] Disaster recovery drill
- [ ] Major version updates
- [ ] Architecture review
- [ ] Capacity planning

---

## 11. DEPLOYMENT SCRIPTS

### 11.1. Start/Stop Scripts

**start.sh:**
```bash
#!/bin/bash
set -e

echo "Starting University Chatbot..."

# Check .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

# Start services
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Health check
curl -f http://localhost:8000/health || exit 1

echo "✅ System started successfully"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
```

**stop.sh:**
```bash
#!/bin/bash
echo "Stopping University Chatbot..."
docker-compose down
echo "✅ System stopped"
```

**restart.sh:**
```bash
#!/bin/bash
./stop.sh
sleep 5
./start.sh
```

### 11.2. Update Script

**update.sh:**
```bash
#!/bin/bash
set -e

echo "Updating University Chatbot..."

# Backup before update
./scripts/full_backup.sh

# Pull latest code
git pull origin master

# Rebuild images
docker-compose build

# Restart services with new images
docker-compose up -d

# Run migrations
docker-compose exec backend python scripts/migrate_database_schema.py

echo "✅ Update completed successfully"
```

---

## 12. APPENDIX

### 12.1. Useful Commands

```bash
# View running processes
docker-compose ps

# View resource usage
docker stats

# Access backend shell
docker-compose exec backend bash

# Access database shell
docker-compose exec postgres psql -U uni_bot_user -d uni_bot_db

# View frontend logs
docker-compose logs -f frontend

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Remove all containers and volumes
docker-compose down -v
```

### 12.2. Python Utilities

```bash
# Check database status
python scripts/check_db_documents.py

# Check data integrity
python scripts/check_data_integrity.py

# Test embedding service
python -c "from src.services.embedding_service import EmbeddingService; e = EmbeddingService(); print(e.create_embedding('test'))"

# Test RAG pipeline
python -c "from src.services.rag_service import RAGService; r = RAGService(); print(r.query('Quy định nghỉ học', 'test'))"
```

### 12.3. Database Queries

```sql
-- Count documents
SELECT COUNT(*) FROM documents WHERE is_active = true;

-- Count chunks
SELECT COUNT(*) FROM chunks WHERE is_active = true;

-- Top accessed documents
SELECT d.filename, COUNT(aq.id) as query_count
FROM documents d
JOIN chunks c ON d.id = c.document_id
JOIN analytics_queries aq ON aq.query LIKE '%' || c.content || '%'
GROUP BY d.id
ORDER BY query_count DESC
LIMIT 10;

-- Average confidence score
SELECT AVG(confidence) FROM analytics_queries;

-- Queries without good results (confidence < 0.5)
SELECT query, confidence, created_at
FROM analytics_queries
WHERE confidence < 0.5
ORDER BY created_at DESC
LIMIT 20;
```

---

**Document Version**: 1.0.0  
**Last Updated**: December 2025  
**Contact**: admin@university.edu.vn
