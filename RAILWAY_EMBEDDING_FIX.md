# 🚀 Railway Embedding Model Fix Guide

## 🔴 Vấn đề / Problem

Gặp lỗi khi deploy trên Railway:
```
❌ Failed to load embedding model: keepitreal/vietnamese-sbert does not appear to have a file named pytorch_model.bin, model.safetensors, tf_model.h5, model.ckpt or flax_model.msgpack.
```

**Nguyên nhân**: Model `keepitreal/vietnamese-sbert` không khả dụng hoặc có vấn đề với files trên Hugging Face.

---

## ✅ Giải pháp / Solution

### Bước 1: Cập nhật Environment Variables trên Railway

Truy cập **Railway Dashboard** → Chọn **Project** → Vào tab **Variables**, thêm/sửa:

```env
EMBEDDING_MODEL=bkai-foundation-models/vietnamese-embedding-v1
EMBEDDING_DIMENSION=768
```

**Hoặc** nếu bạn muốn model nhẹ hơn (cho plan thấp hơn):

```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
```

### Bước 2: Xóa và Rebuild Embeddings Database

Khi đổi EMBEDDING_MODEL, bạn **PHẢI** rebuild lại embeddings vì dimension có thể khác nhau.

#### Option A: Xóa trực tiếp trên Railway (Nhanh nhất)

1. Vào Railway **Database** → PostgreSQL
2. Chạy SQL commands:

```sql
-- Xóa bảng embeddings cũ
DROP TABLE IF EXISTS chunk_embeddings CASCADE;

-- Tạo lại bảng với dimension mới (768 cho vietnamese-embedding-v1)
CREATE TABLE chunk_embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER UNIQUE NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding vector(768),  -- Đổi thành 384 nếu dùng MiniLM-L12-v2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tạo index cho tìm kiếm vector
CREATE INDEX ON chunk_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

**Lưu ý**: Nếu dùng `paraphrase-multilingual-MiniLM-L12-v2`, đổi `vector(768)` thành `vector(384)`

#### Option B: Reset toàn bộ database (Nếu muốn clean slate)

```sql
-- ⚠️ XÓA TẤT CẢ DỮ LIỆU (Cẩn thận!)
DROP TABLE IF EXISTS chunk_embeddings CASCADE;
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;

-- Sau đó chạy lại migration scripts để tạo lại tables
```

### Bước 3: Rebuild Embeddings

Sau khi đã xóa và tạo lại bảng, upload lại PDFs hoặc chạy script rebuild:

#### Từ Local (Nếu có Railway CLI):

```bash
# Kết nối đến Railway
railway login
railway link

# Chạy script rebuild embeddings
railway run python scripts/build_embeddings.py
```

#### Hoặc Upload PDFs qua Admin Interface:

1. Truy cập `https://your-app.railway.app/admin`
2. Vào **Documents Management**
3. Upload lại các PDFs → Hệ thống sẽ tự động tạo embeddings mới

---

## 🎯 Các Model Được Khuyến Nghị / Recommended Models

| Model | Dimension | Language | Memory | Accuracy | Railway Plan |
|-------|-----------|----------|--------|----------|--------------|
| **bkai-foundation-models/vietnamese-embedding-v1** | 768 | Vietnamese | ~2GB | ⭐⭐⭐⭐⭐ | Developer+ |
| **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2** | 384 | Multilingual | ~500MB | ⭐⭐⭐⭐ | Starter+ |
| **intfloat/multilingual-e5-base** | 768 | Multilingual | ~1.5GB | ⭐⭐⭐⭐⭐ | Developer+ |
| **all-MiniLM-L6-v2** | 384 | English | ~400MB | ⭐⭐⭐ | Starter |

### 💡 Khuyến nghị theo Railway Plan:

- **Starter Plan (512MB RAM)**: Dùng `paraphrase-multilingual-MiniLM-L12-v2` (384D)
- **Developer Plan (8GB+ RAM)**: Dùng `bkai-foundation-models/vietnamese-embedding-v1` (768D)
- **Pro Plan**: Dùng `bkai-foundation-models/vietnamese-embedding-v1` hoặc `intfloat/multilingual-e5-base`

---

## 🔧 Troubleshooting

### 1. Lỗi "Dimension mismatch" sau khi đổi model

```
ERROR: dimension mismatch: expected 384, got 768
```

**Giải pháp**: Xóa và tạo lại bảng `chunk_embeddings` với dimension đúng (xem Bước 2 ở trên)

### 2. Lỗi "Out of memory" khi load model

```
RuntimeError: CUDA out of memory
```

**Giải pháp**: 
- Đổi sang model nhẹ hơn (384D thay vì 768D)
- Hoặc upgrade Railway plan

### 3. Model load rất chậm (> 5 phút)

**Nguyên nhân**: Railway đang download model từ Hugging Face lần đầu

**Giải pháp**: Đợi cho đến khi download xong. Lần sau sẽ dùng cached model, nhanh hơn nhiều.

---

## 📝 Kiểm Tra Sau Khi Deploy

Sau khi deploy xong, kiểm tra logs:

```
✅ Embedding model loaded successfully
✅ Hybrid retrieval service initialized
```

Test query để đảm bảo hoạt động:

```bash
curl -X POST https://your-app.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Điều kiện tuyển sinh là gì?",
    "conversation_id": "test-123"
  }'
```

---

## 📚 Tài liệu liên quan

- [Hugging Face Models](https://huggingface.co/models)
- [Railway Docs - Environment Variables](https://docs.railway.app/develop/variables)
- [PostgreSQL pgvector Extension](https://github.com/pgvector/pgvector)

---

## 🆘 Cần Hỗ Trợ?

Nếu vẫn gặp lỗi, kiểm tra:
1. Railway logs: `railway logs`
2. PostgreSQL logs trong Railway dashboard
3. Đảm bảo `EMBEDDING_DIMENSION` khớp với model đã chọn
