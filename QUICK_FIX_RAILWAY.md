# 🚨 RAILWAY QUICK FIX - Embedding Model Error

## ⚡ Giải pháp nhanh (5 phút)

### 1️⃣ Vào Railway Dashboard → Variables → Thêm/Sửa:

```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
```

### 2️⃣ Vào Railway PostgreSQL → Run SQL:

```sql
DROP TABLE IF EXISTS chunk_embeddings CASCADE;

CREATE TABLE chunk_embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER UNIQUE NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON chunk_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 3️⃣ Redeploy:

- Click **Redeploy** trong Railway dashboard
- Đợi deploy xong (~2-3 phút)

### 4️⃣ Upload lại PDFs:

- Vào `https://your-app.railway.app/admin`
- Upload PDFs → Embeddings sẽ tự động tạo

---

## ✅ Kiểm tra logs thành công:

```
✅ Embedding model loaded successfully
✅ Fallback embedding model loaded: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

---

## 🎯 Alternative - Model tốt hơn (nếu có RAM đủ):

```env
EMBEDDING_MODEL=bkai-foundation-models/vietnamese-embedding-v1
EMBEDDING_DIMENSION=768
```

Và đổi SQL thành `vector(768)` thay vì `vector(384)`

---

**Xem chi tiết tại**: `RAILWAY_EMBEDDING_FIX.md`
