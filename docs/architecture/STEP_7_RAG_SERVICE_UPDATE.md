# 🔄 Bước 7: Cập Nhật RAG Service

Hướng dẫn chi tiết để cập nhật `src/services/rag_service.py` để sử dụng PostgreSQL + Hybrid Retrieval.

## 📋 Tổng Quan Thay Đổi

### Cũ (SQLite + FAISS)
```python
# Sử dụng SQLite database
from src.services.database_service import DatabaseService

# Sử dụng FAISS vector search
from src.services.faiss_service import FAISSService

# Sử dụng BM25 từ file
self.bm25_index = load_bm25_index()
```

### Mới (PostgreSQL + Hybrid Retrieval)
```python
# Sử dụng PostgreSQL database
from src.services.postgres_database_service import PostgresDatabaseService

# Sử dụng Hybrid Retrieval (dense + sparse)
from src.services.hybrid_retrieval_service import HybridRetrievalService

# Tích hợp Ingestion Service
from src.services.ingestion_service import IngestionService
```

## 🔧 Các Thay Đổi Cần Làm

### 1. Import Statements
**Thêm**:
```python
from src.services.postgres_database_service import PostgresDatabaseService
from src.services.hybrid_retrieval_service import HybridRetrievalService
from src.services.ingestion_service import IngestionService
```

**Xóa hoặc Comment**:
```python
# from src.services.database_service import DatabaseService  # OLD
# from src.services.faiss_service import FAISSService  # OLD
```

### 2. Initialization (__init__)
**Thay đổi**:
```python
# OLD
self.db_service = DatabaseService()
self.faiss_service = FAISSService()

# NEW
self.db_service = PostgresDatabaseService()
self.hybrid_retrieval = HybridRetrievalService(
    self.db_service, 
    self.embedding_service
)
self.ingestion_service = IngestionService(
    self.db_service,
    self.embedding_service,
    self.pdf_processor,
    self.hybrid_retrieval
)
```

### 3. Retrieval Method
**Thay đổi `retrieve_relevant_chunks()` method**:

```python
# OLD
def retrieve_relevant_chunks(self, query: str, top_k: int = 5):
    # Generate embedding
    query_embedding = self.embedding_service.generate_embedding(query)
    
    # Search FAISS
    faiss_results = self.faiss_service.search(query_embedding, top_k)
    
    # Get chunks from database
    chunks = [self.db_service.get_chunk_by_id(chunk_id) for chunk_id, _ in faiss_results]
    
    return chunks

# NEW
def retrieve_relevant_chunks(self, query: str, top_k: int = 5):
    # Generate embedding
    query_embedding = self.embedding_service.generate_embedding(query)
    
    # Hybrid search (dense + sparse)
    results = self.hybrid_retrieval.hybrid_search(
        query=query,
        query_embedding=query_embedding,
        top_k=top_k
    )
    
    return results
```

### 4. Initialization on Startup
**Thêm**:
```python
# Initialize ingestion service
if AUTO_INGEST_ON_STARTUP:
    log.info("🔄 Running initial PDF ingestion...")
    asyncio.run(self.ingestion_service.process_directory())
    log.info("✅ Initial ingestion completed")

# Start file watcher
self.ingestion_service.start_watching()
```

### 5. Shutdown Cleanup
**Thêm**:
```python
def shutdown(self):
    """Cleanup on shutdown"""
    # Stop file watcher
    if self.ingestion_service:
        self.ingestion_service.stop_watching()
    
    # Close database connection
    if self.db_service:
        self.db_service.close()
```

## 📝 Detailed Changes

### Method: `generate_answer()`
**Thay đổi**:
- Sử dụng `hybrid_retrieval.hybrid_search()` thay vì FAISS search
- Kết quả sẽ có thêm `dense_score` và `sparse_score`
- Cập nhật `sources` formatting

```python
# OLD
chunks = self.retrieve_relevant_chunks(query, top_k=5)
sources = [chunk['source_file'] for chunk in chunks]

# NEW
results = self.retrieve_relevant_chunks(query, top_k=5)
sources = [result['source'] for result in results]
context = "\n".join([result['content'] for result in results])
```

### Method: `rerank_results()`
**Có thể xóa hoặc đơn giản hóa**:
- Hybrid retrieval đã có reranking built-in
- Nếu cần thêm reranking, có thể sử dụng CrossEncoder

```python
# Có thể giữ cho advanced reranking
def rerank_results(self, results, query):
    # Use CrossEncoder for additional reranking
    # Optional: chỉ dùng nếu cần precision cao
    pass
```

### Method: `save_conversation()`
**Cập nhật**:
- Lưu vào PostgreSQL conversations table thay vì in-memory dict

```python
# OLD
self.conversations[conversation_id] = {
    'messages': [...],
    'timestamp': datetime.now()
}

# NEW
self.db_service.save_conversation(
    conversation_id=conversation_id,
    user_message=message,
    assistant_response=response,
    sources=sources,
    confidence=confidence
)
```

## 🧪 Testing Checklist

Sau khi cập nhật, cần test:

- [ ] PostgreSQL connection hoạt động
- [ ] Chunks được lưu vào database
- [ ] Embeddings được tạo và lưu
- [ ] Dense search hoạt động
- [ ] Sparse search hoạt động
- [ ] Hybrid search kết hợp cả hai
- [ ] Conversation history được lưu
- [ ] PDF ingestion tự động hoạt động
- [ ] File watcher phát hiện PDF mới
- [ ] API endpoints hoạt động đúng

## 📊 Performance Considerations

### Dense Search (pgvector)
- Sử dụng IVFFlat index cho tốc độ
- Có thể switch sang HNSW nếu cần tốt hơn
- Cosine similarity: `1 - (embedding <=> query_embedding)`

### Sparse Search (BM25)
- In-memory index, rất nhanh
- Rebuild khi có chunks mới
- Tốt cho keyword matching

### Hybrid Combination
- Configurable weights (default: 70% dense, 30% sparse)
- Có thể tune dựa trên use case
- Cân bằng semantic + keyword matching

## 🚀 Deployment Steps

1. **Backup dữ liệu cũ** (SQLite)
   ```bash
   cp data/embeddings/chatbot.db data/embeddings/chatbot.db.backup
   ```

2. **Cập nhật RAG Service**
   - Edit `src/services/rag_service.py`
   - Thay đổi imports
   - Cập nhật methods

3. **Test locally**
   ```bash
   powershell python test_postgres_connection.py
   powershell python -m pytest tests/
   ```

4. **Migrate dữ liệu** (nếu cần)
   - Tạo script để migrate từ SQLite sang PostgreSQL
   - Hoặc re-ingest tất cả PDFs

5. **Deploy**
   - Restart backend
   - Monitor logs
   - Verify functionality

## 📚 Reference

- `src/services/postgres_database_service.py` - Database operations
- `src/services/hybrid_retrieval_service.py` - Hybrid search
- `src/services/ingestion_service.py` - PDF ingestion
- `config/settings.py` - Configuration

## 🆘 Common Issues

### Issue: "No module named 'pgvector'"
**Solution**: 
```bash
pip install pgvector
```

### Issue: "PostgreSQL connection refused"
**Solution**:
```bash
docker-compose ps  # Check if running
docker-compose logs postgres  # Check logs
```

### Issue: "Hybrid search returns empty results"
**Solution**:
- Kiểm tra chunks đã được insert
- Kiểm tra embeddings đã được tạo
- Kiểm tra BM25 index đã được build

## ✅ Completion Checklist

- [ ] Imports updated
- [ ] Initialization updated
- [ ] Retrieval methods updated
- [ ] Conversation storage updated
- [ ] Ingestion service integrated
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Ready for deployment

---

**Next Step**: Bước 8 - Test & Verify hệ thống

