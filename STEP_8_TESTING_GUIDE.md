# 🧪 Bước 8: Testing & Verification Guide

Hướng dẫn chi tiết để test và verify hệ thống Data Layer mới.

## 📋 Testing Phases

### Phase 1: Infrastructure Testing
### Phase 2: Service Testing
### Phase 3: Integration Testing
### Phase 4: End-to-End Testing

---

## Phase 1: Infrastructure Testing

### 1.1 PostgreSQL Connection Test

**File**: `test_postgres_connection.py` (đã tạo)

```bash
# Chạy test
powershell python test_postgres_connection.py
```

**Kiểm tra**:
- ✅ PostgreSQL connection successful
- ✅ pgvector extension installed
- ✅ Database tables created
- ✅ Services can be imported

### 1.2 Docker Containers Status

```bash
# Kiểm tra containers
docker-compose ps

# Kiểm tra logs
docker-compose logs postgres
docker-compose logs pgadmin
```

**Kỳ vọng**:
- `uni_bot_postgres` - HEALTHY
- `uni_bot_pgadmin` - running (optional)

### 1.3 Database Schema Verification

```bash
# Kết nối tới database
docker exec -it uni_bot_postgres psql -U uni_bot_user -d uni_bot_db

# Kiểm tra tables
\dt

# Kiểm tra extensions
SELECT * FROM pg_extension WHERE extname = 'vector';

# Kiểm tra indexes
\di

# Thoát
\q
```

---

## Phase 2: Service Testing

### 2.1 PostgreSQL Database Service Test

**Tạo file**: `test_postgres_service.py`

```python
import asyncio
from src.services.postgres_database_service import PostgresDatabaseService
from src.models.schemas import DocumentChunk

async def test_database_service():
    # Initialize service
    db_service = PostgresDatabaseService()
    
    # Test insert chunks
    chunks = [
        DocumentChunk(
            content="Test content 1",
            source_file="test.pdf",
            page_number=1,
            chunk_index=0,
            word_count=3,
            char_count=15
        ),
        DocumentChunk(
            content="Test content 2",
            source_file="test.pdf",
            page_number=1,
            chunk_index=1,
            word_count=3,
            char_count=15
        )
    ]
    
    chunk_ids = db_service.insert_chunks(chunks)
    print(f"✅ Inserted {len(chunk_ids)} chunks")
    
    # Test get chunks
    all_chunks = db_service.get_all_chunks()
    print(f"✅ Retrieved {len(all_chunks)} chunks")
    
    # Test stats
    stats = db_service.get_database_stats()
    print(f"✅ Database stats: {stats}")
    
    # Cleanup
    db_service.delete_chunks_by_file("test.pdf")
    print("✅ Cleanup completed")

# Run test
asyncio.run(test_database_service())
```

**Chạy test**:
```bash
powershell python test_postgres_service.py
```

### 2.2 Embedding Service Test

**Tạo file**: `test_embedding_service.py`

```python
from src.services.embedding_service import EmbeddingService

def test_embedding_service():
    service = EmbeddingService()
    
    # Test single embedding
    text = "Đây là một bài kiểm tra"
    embedding = service.generate_embedding(text)
    print(f"✅ Generated embedding with shape: {embedding.shape}")
    
    # Test batch embeddings
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = service.generate_embeddings(texts)
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # Verify dimension
    assert embedding.shape[0] == 384, "Embedding dimension should be 384"
    print("✅ Embedding dimension correct (384)")

test_embedding_service()
```

**Chạy test**:
```bash
powershell python test_embedding_service.py
```

### 2.3 Hybrid Retrieval Service Test

**Tạo file**: `test_hybrid_retrieval.py`

```python
import numpy as np
from src.services.postgres_database_service import PostgresDatabaseService
from src.services.embedding_service import EmbeddingService
from src.services.hybrid_retrieval_service import HybridRetrievalService
from src.models.schemas import DocumentChunk

def test_hybrid_retrieval():
    # Initialize services
    db_service = PostgresDatabaseService()
    embedding_service = EmbeddingService()
    
    # Insert test chunks
    chunks = [
        DocumentChunk(
            content="Trường Đại học An ninh Nhân dân là một trường đại học hàng đầu",
            source_file="test.pdf",
            page_number=1,
            chunk_index=0,
            word_count=10,
            char_count=60
        ),
        DocumentChunk(
            content="Tuyển sinh năm 2024 có nhiều ngành đào tạo mới",
            source_file="test.pdf",
            page_number=2,
            chunk_index=1,
            word_count=9,
            char_count=45
        )
    ]
    
    chunk_ids = db_service.insert_chunks(chunks)
    
    # Generate embeddings
    embeddings = embedding_service.generate_embeddings(
        [chunk.content for chunk in chunks]
    )
    db_service.insert_embeddings(chunk_ids, embeddings)
    
    # Initialize hybrid retrieval
    hybrid_retrieval = HybridRetrievalService(db_service, embedding_service)
    
    # Test hybrid search
    query = "Trường đại học tuyển sinh"
    query_embedding = embedding_service.generate_embedding(query)
    
    results = hybrid_retrieval.hybrid_search(
        query=query,
        query_embedding=query_embedding,
        top_k=5
    )
    
    print(f"✅ Hybrid search found {len(results)} results")
    for result in results:
        print(f"   - Score: {result['combined_score']:.4f}")
        print(f"     Dense: {result['dense_score']:.4f}, Sparse: {result['sparse_score']:.4f}")
    
    # Cleanup
    db_service.delete_chunks_by_file("test.pdf")
    print("✅ Cleanup completed")

test_hybrid_retrieval()
```

**Chạy test**:
```bash
powershell python test_hybrid_retrieval.py
```

---

## Phase 3: Integration Testing

### 3.1 PDF Ingestion Test

**Tạo file**: `test_ingestion.py`

```python
import asyncio
from pathlib import Path
from src.services.postgres_database_service import PostgresDatabaseService
from src.services.embedding_service import EmbeddingService
from src.services.pdf_processor import PDFProcessor
from src.services.ingestion_service import IngestionService

async def test_ingestion():
    # Initialize services
    db_service = PostgresDatabaseService()
    embedding_service = EmbeddingService()
    pdf_processor = PDFProcessor()
    
    ingestion_service = IngestionService(
        db_service,
        embedding_service,
        pdf_processor
    )
    
    # Test processing directory
    pdf_dir = Path("data/pdfs")
    if pdf_dir.exists():
        processed = await ingestion_service.process_directory(pdf_dir)
        print(f"✅ Processed {processed} PDF files")
        
        # Check database
        stats = db_service.get_database_stats()
        print(f"✅ Database stats: {stats}")
    else:
        print("⚠️ No PDF directory found")

asyncio.run(test_ingestion())
```

**Chạy test**:
```bash
powershell python test_ingestion.py
```

---

## Phase 4: End-to-End Testing

### 4.1 Full RAG Pipeline Test

**Tạo file**: `test_rag_pipeline.py`

```python
import asyncio
from src.services.rag_service import RAGService

async def test_rag_pipeline():
    # Initialize RAG service
    rag_service = RAGService()
    
    # Test queries
    test_queries = [
        "Trường đại học An ninh Nhân dân có những ngành nào?",
        "Điều kiện tuyển sinh là gì?",
        "Học phí bao nhiêu tiền?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        
        try:
            response = await rag_service.generate_answer(query)
            
            print(f"✅ Answer: {response['answer'][:100]}...")
            print(f"   Confidence: {response['confidence']:.2f}")
            print(f"   Sources: {response['sources']}")
            print(f"   Processing time: {response['processing_time']:.2f}s")
            
        except Exception as e:
            print(f"❌ Error: {e}")

asyncio.run(test_rag_pipeline())
```

**Chạy test**:
```bash
powershell python test_rag_pipeline.py
```

### 4.2 API Endpoint Test

**Tạo file**: `test_api_endpoints.py`

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health: {response.json()}")

def test_chat():
    """Test chat endpoint"""
    payload = {
        "message": "Trường đại học An ninh Nhân dân là gì?",
        "conversation_id": "test-123"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    
    print(f"✅ Chat response:")
    print(f"   Answer: {result['answer'][:100]}...")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Sources: {result['sources']}")

def test_search():
    """Test search endpoint"""
    payload = {
        "query": "tuyển sinh",
        "top_k": 5
    }
    
    response = requests.post(f"{BASE_URL}/search", json=payload)
    result = response.json()
    
    print(f"✅ Search found {len(result['results'])} results")

# Run tests
print("Testing API Endpoints...\n")
test_health()
test_chat()
test_search()
```

**Chạy test**:
```bash
# Đảm bảo backend đang chạy
powershell python main.py

# Trong terminal khác
powershell python test_api_endpoints.py
```

---

## 📊 Test Results Checklist

### Infrastructure
- [ ] PostgreSQL connection successful
- [ ] pgvector extension installed
- [ ] All tables created
- [ ] Indexes created

### Services
- [ ] Database service CRUD operations work
- [ ] Embedding service generates correct dimensions
- [ ] Hybrid retrieval combines dense + sparse
- [ ] Ingestion service processes PDFs

### Integration
- [ ] PDF ingestion works end-to-end
- [ ] Chunks inserted correctly
- [ ] Embeddings generated and stored
- [ ] BM25 index built

### End-to-End
- [ ] RAG pipeline works
- [ ] Chat endpoint returns answers
- [ ] Search endpoint returns results
- [ ] Conversation history saved

---

## 🚀 Performance Benchmarks

### Expected Performance
- Dense search: < 100ms
- Sparse search: < 50ms
- Hybrid search: < 150ms
- Embedding generation: < 500ms
- Full RAG pipeline: < 2s

### Monitoring
```bash
# Monitor PostgreSQL
docker exec -it uni_bot_postgres psql -U uni_bot_user -d uni_bot_db
SELECT * FROM pg_stat_statements;

# Monitor application logs
tail -f logs/chatbot.log
```

---

## ✅ Completion Checklist

- [ ] All infrastructure tests pass
- [ ] All service tests pass
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] Performance meets expectations
- [ ] Documentation updated
- [ ] Ready for production deployment

---

**Next Step**: Production Deployment

