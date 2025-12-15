# KIẾN TRÚC KỸ THUẬT HỆ THỐNG CHATBOT ĐẠI HỌC

## 1. TỔNG QUAN HỆ THỐNG

### 1.1. Giới thiệu
Hệ thống Chatbot Đại học (University Chatbot) là một ứng dụng AI hỗ trợ sinh viên truy vấn thông tin về quy định, thủ tục và chính sách của trường đại học. Hệ thống sử dụng kỹ thuật RAG (Retrieval-Augmented Generation) kết hợp với vector database để cung cấp câu trả lời chính xác từ kho tài liệu của trường.

### 1.2. Mục tiêu
- **Tự động hóa**: Giảm tải công việc cho phòng ban hành chính
- **Chính xác**: Trả lời dựa trên tài liệu chính thức của trường
- **Nhanh chóng**: Phản hồi ngay lập tức 24/7
- **Hỗ trợ file**: Tự động đính kèm forms/templates phù hợp
- **Đa ngôn ngữ**: Hỗ trợ tiếng Việt và tiếng Anh

### 1.3. Công nghệ chính
- **Backend**: Python 3.10+ với FastAPI
- **Frontend**: Next.js 15 (React 19) với TypeScript
- **Database**: PostgreSQL 16 với pgvector extension
- **AI Models**: 
  - Sentence Transformers (Vietnamese SBERT)
  - Google Gemini 2.0 Flash
  - Cross-Encoder (MS-MARCO MiniLM)
- **Cache**: Redis
- **Container**: Docker & Docker Compose
- **Vector Search**: FAISS + pgvector

---

## 2. KIẾN TRÚC TỔNG THỂ

### 2.1. Sơ đồ kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │   Web Browser    │              │   Mobile App     │         │
│  │   (Next.js)      │              │   (Future)       │         │
│  └──────────────────┘              └──────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                         │   │
│  │  - CORS Middleware                                       │   │
│  │  - Security Headers                                      │   │
│  │  - Checksum Validation                                   │   │
│  │  - Authentication (JWT)                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  RAG Service   │  │ Ingestion       │  │ Analytics       │  │
│  │  - Query       │  │ Service         │  │ Service         │  │
│  │  - Retrieval   │  │ - PDF Watch     │  │ - Tracking      │  │
│  │  - Generation  │  │ - Auto Process  │  │ - Reporting     │  │
│  └────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Hybrid         │  │ Attachment      │  │ Memory          │  │
│  │ Retrieval      │  │ Service         │  │ Service         │  │
│  │ - Dense        │  │ - File Upload   │  │ - Context       │  │
│  │ - Sparse (BM25)│  │ - Link Chunks   │  │ - History       │  │
│  └────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Embedding      │  │ Gemini Service  │  │ Cache Service   │  │
│  │ Service        │  │ - LLM API       │  │ - Redis         │  │
│  │ - SBERT        │  │ - Normalize     │  │ - TTL           │  │
│  └────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  PostgreSQL    │  │  Redis Cache    │  │  File Storage   │  │
│  │  - pgvector    │  │  - Embeddings   │  │  - PDFs         │  │
│  │  - Chunks      │  │  - Sessions     │  │  - Forms        │  │
│  │  - Documents   │  │  - Analytics    │  │  - Attachments  │  │
│  └────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2. Luồng xử lý chính

#### A. Luồng Chat Query
```
User Input → Frontend
    ↓
API Gateway (Authentication, Validation)
    ↓
RAG Service
    ├→ Question Normalization (Gemini)
    ├→ Embedding Service (Create query embedding)
    ├→ Hybrid Retrieval Service
    │   ├→ Dense Search (pgvector cosine similarity)
    │   └→ Sparse Search (BM25)
    ├→ Reranking (Cross-Encoder)
    ├→ Context Assembly
    ├→ LLM Generation (Gemini)
    └→ Attachment Matching
    ↓
Response with Answer + Sources + Attachments
```

#### B. Luồng Ingestion (Document Processing)
```
PDF File → data/new_pdf/
    ↓
Ingestion Service (Watchdog)
    ↓
PDF Processor
    ├→ Extract Text
    ├→ Extract Headings
    └→ Smart Chunking
    ↓
Embedding Service
    └→ Create embeddings for each chunk
    ↓
PostgreSQL Database
    ├→ Save chunks
    ├→ Save embeddings (pgvector)
    └→ Update document status
```

---

## 3. KIẾN TRÚC CHI TIẾT CÁC LAYER

### 3.1. Frontend Layer (Next.js)

#### Cấu trúc thư mục
```
frontend/
├── src/
│   ├── app/                    # App Router (Next.js 15)
│   │   ├── page.tsx           # Home (Chat interface)
│   │   ├── admin/             # Admin dashboard
│   │   │   ├── page.tsx       # Admin overview
│   │   │   ├── documents/     # Document management
│   │   │   ├── attachments/   # File management
│   │   │   ├── analytics/     # Analytics dashboard
│   │   │   └── settings/      # System settings
│   │   └── api/               # API routes (if needed)
│   ├── components/            # React components
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   ├── InputBox.tsx
│   │   ├── AttachmentCard.tsx
│   │   └── ...
│   ├── lib/                   # Utilities
│   │   ├── api.ts            # API client
│   │   └── utils.ts
│   └── styles/               # CSS/Tailwind
└── public/                   # Static assets
```

#### Công nghệ Frontend
- **Framework**: Next.js 15.3 (React 19)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **Charts**: Recharts 3.5
- **Markdown**: react-markdown + remark-gfm
- **Syntax Highlighting**: react-syntax-highlighter
- **Icons**: Lucide React
- **HTTP Client**: Axios

#### Tính năng chính
1. **Chat Interface**
   - Real-time typing indicators
   - Message history
   - Source citations
   - Attachment downloads
   - Markdown rendering

2. **Admin Dashboard**
   - Document upload & management
   - Chunk viewer & editor
   - Attachment management
   - Analytics & metrics
   - User management

3. **Responsive Design**
   - Mobile-first approach
   - Adaptive layouts
   - Touch-friendly UI

### 3.2. Backend Layer (FastAPI)

#### Cấu trúc thư mục
```
src/
├── api/                      # API Routes
│   ├── routes.py            # Main routes
│   ├── auth_routes.py       # Authentication
│   └── admin_routes.py      # Admin endpoints
├── services/                # Business Logic
│   ├── rag_service.py       # RAG pipeline
│   ├── hybrid_retrieval_service.py
│   ├── embedding_service.py
│   ├── ingestion_service.py
│   ├── attachment_service.py
│   ├── analytics_service.py
│   ├── memory_service.py
│   └── cache_service.py
├── models/                  # Data Models
│   ├── database_models.py   # SQLAlchemy models
│   └── api_models.py        # Pydantic models
├── middleware/             # Middleware
│   ├── checksum_middleware.py
│   ├── https_middleware.py
│   └── auth_middleware.py
├── utils/                  # Utilities
│   └── logger.py
└── auth/                   # Authentication
    └── jwt_handler.py
```

#### Công nghệ Backend
- **Framework**: FastAPI 0.104
- **ASGI Server**: Uvicorn
- **ORM**: SQLAlchemy 2.0 + SQLModel
- **Database Driver**: psycopg2-binary
- **Vector Extension**: pgvector
- **Validation**: Pydantic 2.5
- **Authentication**: PyJWT, python-jose
- **Logging**: Loguru
- **File Watching**: Watchdog

#### API Endpoints chính

**Chat Endpoints**
```
POST   /api/v1/chat              # Send chat message
POST   /api/v1/chat/stream       # Streaming chat
GET    /api/v1/chat/history      # Get chat history
DELETE /api/v1/chat/session      # Clear session
```

**Document Management**
```
POST   /api/v1/documents/upload  # Upload PDF
GET    /api/v1/documents         # List documents
GET    /api/v1/documents/{id}    # Get document details
DELETE /api/v1/documents/{id}    # Delete document
POST   /api/v1/documents/reprocess  # Reprocess document
```

**Attachment Management**
```
POST   /api/v1/attachments/upload    # Upload file
GET    /api/v1/attachments           # List attachments
GET    /api/v1/attachments/{id}      # Get attachment
GET    /api/v1/attachments/download/{id}  # Download
DELETE /api/v1/attachments/{id}      # Delete (soft)
POST   /api/v1/attachments/{id}/link-chunks  # Link to chunks
```

**Analytics**
```
GET    /api/v1/analytics/stats       # Overall statistics
GET    /api/v1/analytics/queries     # Query analytics
GET    /api/v1/analytics/documents   # Document analytics
GET    /api/v1/analytics/feedback    # Feedback summary
```

**Admin**
```
GET    /api/v1/admin/chunks          # List chunks
PUT    /api/v1/admin/chunks/{id}     # Update chunk
DELETE /api/v1/admin/chunks/{id}     # Delete chunk
POST   /api/v1/admin/rebuild-index   # Rebuild search index
```

### 3.3. Database Layer (PostgreSQL + pgvector)

#### Database Schema

**Bảng `documents`**
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_hash VARCHAR(64),
    total_chunks INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);
```

**Bảng `chunks`**
```sql
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER,
    heading TEXT,
    metadata JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Bảng `embeddings`**
```sql
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER UNIQUE REFERENCES chunks(id) ON DELETE CASCADE,
    embedding vector(384),  -- Vietnamese SBERT dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Bảng `document_attachments`**
```sql
CREATE TABLE document_attachments (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    description TEXT,
    keywords TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Bảng `chunk_attachments`** (Many-to-Many)
```sql
CREATE TABLE chunk_attachments (
    chunk_id INTEGER REFERENCES chunks(id) ON DELETE CASCADE,
    attachment_id INTEGER REFERENCES document_attachments(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (chunk_id, attachment_id)
);
```

**Bảng `conversations`**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Bảng `analytics_queries`**
```sql
CREATE TABLE analytics_queries (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    query TEXT NOT NULL,
    answer TEXT,
    confidence FLOAT,
    retrieved_chunks INTEGER,
    response_time FLOAT,
    feedback VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Bảng `analytics_documents`**
```sql
CREATE TABLE analytics_documents (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    views INTEGER DEFAULT 0,
    chunk_retrievals INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Indexes quan trọng
```sql
-- Vector similarity search (IVFFlat index)
CREATE INDEX embeddings_embedding_idx 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Fast keyword search
CREATE INDEX idx_attachments_keywords 
ON document_attachments 
USING GIN (keywords);

-- Fast chunk lookup
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_active ON chunks(is_active);

-- Fast analytics queries
CREATE INDEX idx_analytics_queries_session ON analytics_queries(session_id);
CREATE INDEX idx_analytics_queries_created ON analytics_queries(created_at);
```

### 3.4. Cache Layer (Redis)

#### Redis Usage
```
Cache Structure:
├── embedding:{text_hash}          # Cached embeddings (TTL: 7 days)
├── query:{query_hash}             # Cached query results (TTL: 1 hour)
├── session:{session_id}           # Session data (TTL: 24 hours)
└── analytics:{date}               # Daily analytics (TTL: 30 days)
```

#### Configuration
```python
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_CACHE_TTL = 604800  # 7 days
ENABLE_REDIS_CACHE = True
```

---

## 4. CÁC KỸ THUẬT AI/ML ĐƯỢC SỬ DỤNG

### 4.1. RAG (Retrieval-Augmented Generation)

RAG là kỹ thuật kết hợp retrieval (truy xuất) và generation (sinh văn bản):

#### Quy trình RAG
```
1. INDEXING PHASE (Offline)
   PDF Documents
      ↓
   Text Extraction + Chunking
      ↓
   Embedding Generation (SBERT)
      ↓
   Store in Vector Database (pgvector)

2. RETRIEVAL PHASE (Online)
   User Query
      ↓
   Query Normalization (Gemini)
      ↓
   Query Embedding (SBERT)
      ↓
   Hybrid Search (Dense + Sparse)
      ↓
   Reranking (Cross-Encoder)
      ↓
   Top-K Relevant Chunks

3. GENERATION PHASE (Online)
   Retrieved Context + Query
      ↓
   Prompt Engineering
      ↓
   LLM Generation (Gemini)
      ↓
   Formatted Answer + Citations
```

#### Ưu điểm của RAG
- **Grounded**: Câu trả lời dựa trên tài liệu thực tế
- **Up-to-date**: Có thể cập nhật knowledge base mà không cần retrain
- **Transparent**: Có thể trích dẫn nguồn
- **Cost-effective**: Không cần fine-tuning LLM

### 4.2. Hybrid Retrieval (Dense + Sparse)

#### Dense Retrieval (Vector Search)
```python
# Sử dụng pgvector với cosine similarity
SELECT chunk_id, 
       1 - (embedding <=> query_embedding) as similarity
FROM embeddings
WHERE 1 - (embedding <=> query_embedding) > threshold
ORDER BY similarity DESC
LIMIT k
```

**Ưu điểm**:
- Tìm được semantic similarity (ngữ nghĩa tương tự)
- Hiệu quả với câu hỏi phức tạp
- Cross-lingual (tìm được cả khi ngôn ngữ khác nhau)

**Nhược điểm**:
- Kém với exact keyword matching
- Tốn tài nguyên tính toán

#### Sparse Retrieval (BM25)
```python
# BM25 algorithm
score = IDF * (f * (k1 + 1)) / (f + k1 * (1 - b + b * (|D| / avgdl)))

# Where:
# f = term frequency in document
# |D| = document length
# avgdl = average document length
# k1, b = tuning parameters
```

**Ưu điểm**:
- Tốt với exact keyword matching
- Nhanh, hiệu quả
- Giải thích được (explainable)

**Nhược điểm**:
- Không hiểu semantic
- Phụ thuộc vào term overlap

#### Hybrid Fusion
```python
# Reciprocal Rank Fusion (RRF)
score_hybrid = α * score_dense + (1 - α) * score_sparse

# Where α = DENSE_WEIGHT (default: 0.7)
```

### 4.3. Embedding Models

#### Vietnamese SBERT
```
Model: keepitreal/vietnamese-sbert
Dimension: 384
Language: Vietnamese (optimized)
Task: Sentence similarity
Base: Sentence-BERT
```

**Đặc điểm**:
- Huấn luyện trên corpus tiếng Việt
- Hiệu quả với câu dài
- Fast inference (GPU/CPU)

**Cách sử dụng**:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('keepitreal/vietnamese-sbert')
embedding = model.encode("Quy định về nghỉ học")
# Output: [384-dimensional vector]
```

### 4.4. Cross-Encoder Reranking

#### MS-MARCO MiniLM-L6-v2
```
Model: cross-encoder/ms-marco-MiniLM-L-6-v2
Task: Reranking
Input: [query, document] pairs
Output: Relevance score (0-1)
```

**Quy trình Reranking**:
```
Initial Retrieval (100 chunks)
    ↓
Fast First-stage: Hybrid Search
    ↓
Top-20 candidates
    ↓
Slow Second-stage: Cross-Encoder
    ↓
Top-5 most relevant chunks
```

**Lý do sử dụng**:
- Cross-Encoder xem xét tương tác giữa query và document
- Chính xác hơn Bi-Encoder (SBERT)
- Nhưng chậm hơn → chỉ dùng cho reranking

### 4.5. LLM Integration

#### Google Gemini 2.0 Flash
```
Model: gemini-2.0-flash-exp
Context Window: 1M tokens
Output Tokens: 8192
Temperature: 0.7
```

**Use Cases trong hệ thống**:

1. **Question Normalization**
```python
# Chuẩn hóa câu hỏi trước khi search
Original: "cho tôi xin form đơn nghỉ học đi"
Normalized: "form đơn xin nghỉ học"
```

2. **Answer Generation**
```python
# Sinh câu trả lời từ context
prompt = f"""
Context: {retrieved_chunks}
Question: {user_query}
Answer in Vietnamese, cite sources.
"""
```

3. **Suggested Questions**
```python
# Tạo câu hỏi gợi ý dựa trên context
prompt = "Generate 3 follow-up questions..."
```

### 4.6. Smart Chunking Strategy

#### Heading-based Chunking
```python
# Ưu tiên giữ nguyên cấu trúc heading
Chunk 1: [Heading 1] + Content under Heading 1
Chunk 2: [Heading 2] + Content under Heading 2
...
```

#### Overlapping Chunks
```python
# Tạo overlap để tránh mất context
Chunk Size: 500 characters
Overlap: 50 characters

Example:
Chunk 1: [0:500]
Chunk 2: [450:950]    # 50 chars overlap
Chunk 3: [900:1400]
```

#### Metadata Enrichment
```python
chunk_metadata = {
    "document_id": 123,
    "heading": "Quy định về nghỉ học",
    "page_number": 5,
    "chunk_index": 2,
    "file_name": "quy_che_dao_tao.pdf"
}
```

---

## 5. BẢO MẬT VÀ AUTHENTICATION

### 5.1. JWT Authentication

#### Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "username": "admin",
    "role": "admin",
    "exp": 1735890000,
    "iat": 1735803600
  },
  "signature": "..."
}
```

#### Flow
```
1. Login: POST /api/v1/auth/login
   → Returns: { access_token, token_type, expires_in }

2. Protected Request: 
   Header: Authorization: Bearer <token>

3. Token Validation:
   - Verify signature
   - Check expiration
   - Extract user info

4. Refresh: POST /api/v1/auth/refresh
   → Returns: New access_token
```

### 5.2. Security Middleware

#### HTTPS Redirect
```python
# Force HTTPS in production
if not request.url.scheme == "https":
    redirect(https_url)
```

#### Security Headers
```python
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Strict-Transport-Security"] = "max-age=31536000"
```

#### Checksum Validation
```python
# Verify request integrity
checksum = hashlib.sha256(request.body).hexdigest()
if checksum != request.headers["X-Checksum"]:
    raise InvalidChecksumError()
```

### 5.3. CORS Configuration
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Development
    "https://chatbot.university.edu.vn"  # Production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)
```

---

## 6. PERFORMANCE & OPTIMIZATION

### 6.1. Caching Strategy

#### Multi-level Cache
```
Level 1: Redis (7 days TTL)
   - Embeddings
   - Frequent queries
   
Level 2: In-memory (Process lifetime)
   - Model weights
   - BM25 index
   
Level 3: Database (Permanent)
   - All data
```

#### Cache Hit Rate
```python
# Target: 80%+ cache hit rate
cache_hit_rate = cache_hits / (cache_hits + cache_misses)
```

### 6.2. Database Optimization

#### Connection Pooling
```python
# SQLAlchemy connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

#### Query Optimization
```sql
-- Use EXPLAIN ANALYZE to check query plans
EXPLAIN ANALYZE
SELECT * FROM embeddings
WHERE 1 - (embedding <=> query_vec) > 0.7
ORDER BY embedding <=> query_vec
LIMIT 10;

-- Expected: Index Scan using embeddings_embedding_idx
```

### 6.3. Async Processing

#### Background Tasks
```python
@app.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile
):
    # Save file immediately
    save_file(file)
    
    # Process in background
    background_tasks.add_task(
        process_document, 
        file.filename
    )
    
    return {"status": "processing"}
```

#### File Watcher (Ingestion Service)
```python
# Watchdog monitors data/new_pdf/
observer = Observer()
observer.schedule(handler, path, recursive=False)
observer.start()

# Auto-process new PDFs
def on_created(event):
    process_pdf(event.src_path)
```

### 6.4. Response Time Targets

```
Endpoint                  Target Time
─────────────────────────────────────
GET  /health              < 50ms
POST /chat                < 2000ms
POST /chat/stream         < 500ms (first token)
GET  /documents           < 200ms
POST /documents/upload    < 500ms (sync part)
GET  /analytics/stats     < 300ms
```

---

## 7. MONITORING & LOGGING

### 7.1. Logging Strategy

#### Log Levels
```python
# Loguru configuration
log.add(
    "logs/app_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time} | {level} | {message}"
)
```

#### Log Categories
```
- INFO: Normal operations
- WARNING: Degraded performance, cache misses
- ERROR: Failed requests, exceptions
- CRITICAL: System failures, data corruption
```

### 7.2. Analytics Tracking

#### Metrics Tracked
```python
- Query count per session
- Average response time
- Cache hit rate
- Document retrieval frequency
- User feedback (thumbs up/down)
- Error rate
- Confidence scores distribution
```

#### Dashboard Metrics
```
- Total queries (daily/weekly/monthly)
- Popular queries
- Average confidence score
- Most accessed documents
- User satisfaction rate
- System uptime
```

---

## 8. DEPLOYMENT & DEVOPS

### 8.1. Docker Configuration

#### docker-compose.yml
```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: uni_bot_db
      POSTGRES_USER: uni_bot_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_postgres.sql:/docker-entrypoint-initdb.d/01-init.sql
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build: .
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://uni_bot_user:${POSTGRES_PASSWORD}@postgres:5432/uni_bot_db
      REDIS_HOST: redis
    ports:
      - "8000:8000"
  
  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "3000:3000"
```

### 8.2. Environment Variables

```bash
# .env file
# Database
POSTGRES_USER=uni_bot_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=uni_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
ENABLE_REDIS_CACHE=true

# LLM
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MAX_OUTPUT_TOKENS=8192
ENABLE_GEMINI_NORMALIZATION=true

# API
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000

# Security
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Embedding
EMBEDDING_MODEL=keepitreal/vietnamese-sbert
EMBEDDING_DIMENSION=384

# Retrieval
TOP_K_RESULTS=5
DENSE_WEIGHT=0.7
DENSE_SIMILARITY_THRESHOLD=0.7
SPARSE_SIMILARITY_THRESHOLD=0.5
```

### 8.3. Deployment Steps

#### Development
```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install

# 2. Start PostgreSQL
docker-compose up -d postgres

# 3. Run migrations
python scripts/migrate_database_schema.py

# 4. Start backend
python main.py

# 5. Start frontend
cd frontend && npm run dev
```

#### Production
```bash
# 1. Build Docker images
docker-compose build

# 2. Start all services
docker-compose up -d

# 3. Check health
curl http://localhost:8000/health

# 4. View logs
docker-compose logs -f backend
```

---

## 9. SCALABILITY & FUTURE IMPROVEMENTS

### 9.1. Current Limitations
- Single server deployment
- No load balancing
- Limited to 10MB file uploads
- No CDN for attachments
- In-memory BM25 index (RAM-limited)

### 9.2. Scaling Strategy

#### Horizontal Scaling
```
Load Balancer (nginx)
    ├→ Backend Instance 1
    ├→ Backend Instance 2
    └→ Backend Instance 3
        ↓
PostgreSQL Primary-Replica
Redis Cluster
Object Storage (S3)
```

#### Vertical Scaling
- Increase RAM for embedding models
- Add GPU for faster inference
- Scale PostgreSQL (more connections)

### 9.3. Future Enhancements

1. **Advanced RAG**
   - Query decomposition
   - Multi-hop reasoning
   - Self-reflective RAG

2. **Multimodal Support**
   - Image understanding (charts, diagrams)
   - Table extraction
   - Form recognition

3. **Advanced Analytics**
   - A/B testing framework
   - User behavior analysis
   - Predictive maintenance

4. **Enhanced Security**
   - OAuth2 integration
   - Rate limiting per user
   - API key management
   - Audit logging

5. **Performance**
   - GraphQL API
   - Websocket for real-time
   - Edge caching (CloudFlare)
   - Model quantization

---

## 10. KẾT LUẬN

### 10.1. Điểm mạnh của hệ thống
✅ **Chính xác**: RAG đảm bảo trả lời dựa trên tài liệu thực tế  
✅ **Nhanh**: Hybrid retrieval + caching cho response time < 2s  
✅ **Linh hoạt**: Dễ dàng thêm tài liệu mới không cần retrain  
✅ **Transparent**: Citation và source tracking  
✅ **Modern stack**: Next.js + FastAPI + PostgreSQL + AI  

### 10.2. Challenges đã giải quyết
🔧 Vietnamese language support  
🔧 Hybrid search (dense + sparse)  
🔧 Smart attachment matching  
🔧 Real-time document ingestion  
🔧 Conversation memory  

### 10.3. Technology Stack Summary
```
Frontend:  Next.js 15 + React 19 + TypeScript + Tailwind
Backend:   FastAPI + Python 3.10+
Database:  PostgreSQL 16 + pgvector
Cache:     Redis 7
AI:        Sentence-BERT + Gemini + Cross-Encoder
Infra:     Docker + Docker Compose
```

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: University Chatbot Development Team
