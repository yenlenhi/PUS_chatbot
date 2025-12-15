# CHƯƠNG 4: KIẾN TRÚC HỆ THỐNG & QUY TRÌNH RAG END-TO-END

(Đây là chương gộp của Chương 4, 5, 6: Kiến trúc hệ thống, Quy trình xử lý Document, và Quy trình RAG Retrieval.)

## MỤC LỤC

1. [Kiến trúc tổng thể](#41-kiến-trúc-tổng-thể)
2. [Kiến trúc Backend](#42-kiến-trúc-backend)
3. [Kiến trúc Frontend](#43-kiến-trúc-frontend)
4. [Kiến trúc Database](#44-kiến-trúc-database)
5. [Kiến trúc AI/ML Pipeline](#45-kiến-trúc-aiml-pipeline)
6. [Luồng dữ liệu toàn hệ thống](#46-luồng-dữ-liệu-toàn-hệ-thống)
7. [Quy trình xử lý Document](#47-quy-trình-xử-lý-document)
8. [Quy trình RAG Retrieval](#48-quy-trình-rag-retrieval)
9. [Thông số vận hành và tối ưu](#49-thông-số-vận-hành-và-tối-ưu)
10. [Monitoring & Observability](#410-monitoring--observability)

---

## 4.1. Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                               USER INTERFACE (FE)                           │
│      Next.js 15 + React 19 + Tailwind + shadcn/ui (Dashboard + Chat)        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (API Layer)                            │
│   FastAPI (Python) · Auth · Rate-limit · Validation · Orchestration         │
│   Routes: /chat, /documents, /analytics, /health                            │
└─────────────────────────────────────────────────────────────────────────────┘
   │                 │                         │                     │
   ▼                 ▼                         ▼                     ▼
┌─────────┐   ┌────────────────┐       ┌─────────────────┐   ┌────────────────────┐
│ RAG Svc │→→ │ Retrieval Svc  │ →→→   │ Embedding Svc    │   │ Ingestion Service  │
│         │    │ (Hybrid: vec+ │       │ (SBERT 384-d)    │   │ (Watchdog + OCR)   │
└─────────┘    │ BM25 + RRF)   │       └─────────────────┘   └────────────────────┘
                 │                                         │
                 ▼                                         ▼
           ┌──────────────┐                          ┌────────────────┐
           │ Postgres +   │                          │ Redis (cache)  │
           │ pgvector     │                          └────────────────┘
           └──────────────┘
```

- Giao diện người dùng gửi query và quản lý tài liệu
- Backend điều phối: truy xuất, sinh câu trả lời, xử lý document
- Database lưu chunks, embeddings, log; Redis làm caching

---

## 4.2. Kiến trúc Backend

- Framework: FastAPI (async)
- Các services chính:
  - `RAGService`: Điều phối toàn bộ pipeline trả lời
  - `RetrievalService`: Vector search + BM25 + RRF + Reranking
  - `EmbeddingService`: Tạo embeddings (Vietnamese SBERT 384-d)
  - `IngestionService`: Tự động đọc PDF, trích xuất text, chunking, lưu DB
  - `AnalyticsService`: Thống kê, log, sức khỏe hệ thống
- Bố cục router:
  - `/api/v1/chat` — xử lý truy vấn và trả lời
  - `/api/v1/documents/*` — upload, list, reprocess, delete
  - `/api/v1/analytics/*` — số liệu
  - `/api/v1/health` — health checks

---

## 4.3. Kiến trúc Frontend

- Next.js 15 (App Router) + React 19
- Phân tách:
  - `Chat UI`: nhập câu hỏi, hiển thị câu trả lời + trích dẫn nguồn
  - `Admin Dashboard`: upload PDF, xem trạng thái xử lý, thống kê
- UI components: Tailwind CSS + shadcn/ui
- API integration: `fetch`/`axios` đến backend

---

## 4.4. Kiến trúc Database

- PostgreSQL 16 + `pgvector`
- Bảng chính:
  - `documents` — metadata tài liệu, trạng thái xử lý
  - `chunks` — nội dung đã chunk, heading, page, metadata
  - `embeddings` — vector(384) cho từng chunk
- Indexing:
  - `ivfflat` trên `embeddings.embedding` (cosine ops)
  - B-tree/GiN cho truy vấn metadata và full-text (nếu cần)

---

## 4.5. Kiến trúc AI/ML Pipeline

- Embeddings: Vietnamese SBERT (384-d)
- Retrieval: Hybrid (Vector + BM25) với Reciprocal Rank Fusion (RRF)
- Reranking: Cross-Encoder (MS-MARCO MiniLM)
- Generation: Gemini 2.0 Flash
- OCR: Gemini Vision API (fallback pdfplumber/PyPDF2)

---

## 4.6. Luồng dữ liệu toàn hệ thống

```
User → Chat UI → /chat → RAGService
   ① Nhận query, normalize, tạo query embedding
   ② Retrieval: Vector search + BM25 → hợp nhất RRF → Top-K
   ③ Reranking: Cross-Encoder → Top-N
   ④ Context builder: định dạng nguồn, cắt ghép an toàn
   ⑤ LLM (Gemini): sinh câu trả lời + trích dẫn
   ⑥ Trả về FE + ghi analytics

Admin → Upload PDF/Drop vào folder
   ① IngestionService: detect file
   ② Extraction: Gemini Vision → pdfplumber → PyPDF2
   ③ HeadingChunker: tạo chunks (giữ ngữ cảnh, overlap)
   ④ Embeddings: batch encode + cache
   ⑤ Lưu DB + build index (pgvector, BM25)
   ⑥ Analytics/health cập nhật
```

---

## 4.7. Quy trình xử lý Document

### 4.7.1. Tổng quan
- Mục tiêu: chuyển PDF → text → chunks → embeddings → DB
- Chất lượng: ưu tiên heading-based chunking, giữ ngữ cảnh

### 4.7.2. Document Ingestion
- Phương thức:
  - Upload qua Admin Dashboard (API `/documents/upload`)
  - Auto-ingestion: copy vào `data/new_pdf/` (Watchdog)
  - Bulk: chạy `scripts/process_pdfs.py` (`--use-gemini`/`--no-gemini`)
- Tracking: `documents.status` = pending → processing → completed/failed

### 4.7.3. Text Extraction
- Chiến lược 3 lớp:
  - L1: Gemini Vision API (OCR chất lượng cao; chậm hơn)
  - L2: pdfplumber (giữ layout tốt; không OCR)
  - L3: PyPDF2 (nhanh; layout đơn giản)
- Đánh giá chất lượng text: word/line count, gibberish detection, confidence

### 4.7.4. Chunking Strategy
- Heading detection: số thứ tự (1., 1.1., I., A.), ALL CAPS
- Smart splitting: theo đoạn, giới hạn `min/max/target` size, overlap
- Metadata: `source_file`, `page_number`, `heading_text`, `word_count`, `char_count`

### 4.7.5. Embedding Generation
- Model: Vietnamese SBERT (384-d)
- Batch: 32 (tối ưu tốc độ)
- Cache: Redis (TTL 7 ngày) theo hash nội dung

### 4.7.6. Storage & Indexing
- Lưu `documents`, `chunks`, `embeddings`
- Tạo index `ivfflat (vector_cosine_ops)` trên embeddings
- Rebuild BM25 index sau khi thêm tài liệu

### 4.7.7. Auto-Ingestion Service
- Watchdog events: `on_created`, `on_modified`, `on_deleted`
- Xử lý async, delay nhẹ đảm bảo file ghi xong
- Khởi động watcher và optional startup ingestion

Tham chiếu chi tiết: `docs/DOCUMENT_PROCESSING_FLOW.md`

---

## 4.8. Quy trình RAG Retrieval

### 4.8.1. Query Processing
- Chuẩn hóa: lowercasing, loại bỏ ký tự thừa, xử lý dấu
- Tạo query embedding (SBERT)

### 4.8.2. Dense Retrieval (Vector Search)
- Tìm Top-K theo cosine similarity từ `embeddings`
- Index: `ivfflat` với `lists ≈ sqrt(rows)`

### 4.8.3. Sparse Retrieval (BM25)
- Tokenize corpus/chunk content
- BM25Okapi → điểm cho từng chunk

### 4.8.4. Hybrid Search (RRF)
- Gộp hai danh sách kết quả bằng Reciprocal Rank Fusion (k=60)
- Kết quả: danh sách hợp nhất theo điểm RRF

### 4.8.5. Cross-Encoder Reranking
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Chấm điểm cặp [query, chunk content]
- Chọn Top-N (ví dụ N=5)

### 4.8.6. Context Generation
- Định dạng: thêm nguồn (file, trang), tóm tắt ngắn, cắt ghép an toàn
- Kiểm soát độ dài: giới hạn tokens, loại bỏ trùng lặp

### 4.8.7. LLM Response Generation
- Model: Gemini 2.0 Flash (temperature=0.2)
- Prompt: hệ thống + context + câu hỏi
- Output: câu trả lời có trích dẫn nguồn

Tham chiếu lý thuyết: `docs/CHAPTER_3_THEORETICAL_FOUNDATION.md`

---

## 4.9. Thông số vận hành và tối ưu

- Embedding batch size: 32 (giảm nếu RAM hạn chế)
- IVFFlat lists: ~sqrt(rows) (100 cho 10K vectors)
- Top-K retrieval: 20; Top-N reranking: 5
- Gemini OCR: bật cho bản scan; tắt để tiết kiệm khi PDF có text
- Chunk target size: 1000 chars; overlap: 50 chars

---

## 4.10. Monitoring & Observability

- Logs: pipeline từng bước (ingestion, extraction, chunking, embeddings, retrieval)
- Health checks: DB, Redis, queue size, watcher directory
- Metrics: tổng documents, thời gian xử lý trung bình, cache hit rate
- Troubleshooting: quota Gemini, kết nối DB, bộ nhớ khi embedding

---

**Kết nối các chương:**
- Nền tảng lý thuyết: `docs/CHAPTER_3_THEORETICAL_FOUNDATION.md`
- Chi tiết xử lý document: `docs/DOCUMENT_PROCESSING_FLOW.md`

**Document Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: University Chatbot Development Team