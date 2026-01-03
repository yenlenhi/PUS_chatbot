Dưới đây là README ngắn gọn (dạng profile) về bạn – người xây dựng hệ thống University Chatbot ở trên:

---

## 👋 Truong Van Khai (VanKhaiii · Hi Hi)

**Computer Science — Present**
University of Information Technology (UIT), VNU-HCM — Viet Nam

Mình là **Trương Văn Khai**, hiện đang học Computer Science tại UIT (ĐHQG-HCM). Mình là người thiết kế và triển khai hệ thống **University Chatbot** dựa trên **RAG (Retrieval-Augmented Generation)**, tập trung vào việc giúp sinh viên tra cứu **quy định, thủ tục, biểu mẫu** từ kho tài liệu chính thức của trường một cách **nhanh – đúng – có nguồn trích dẫn**.

### 🔧 What I built

* **University Chatbot Architecture (RAG + Vector DB)**
  Pipeline gồm: *question normalization → hybrid retrieval (dense+BM25) → reranking (cross-encoder) → context assembly → Gemini generation → attachment matching*.
* **Auto ingestion**: theo dõi thư mục PDF, xử lý/chunking thông minh, sinh embeddings và lưu vào hệ thống.
* **Admin dashboard**: quản trị tài liệu/chunks/attachments + analytics cơ bản.
* **Modern stack**:

  * Frontend: **Next.js 15 (React 19) + TypeScript + Tailwind**
  * Backend: **FastAPI (Python)**
  * Data: **PostgreSQL 16 + pgvector**, **Redis**
  * Models: **Vietnamese SBERT + Cross-Encoder + Gemini 2.0 Flash**
  * Infra: **Docker / Docker Compose**

### 🎯 Interests

* RAG systems, hybrid search, reranking
* Vector databases (pgvector/FAISS), indexing & retrieval quality
* Building AI products with production-ready architecture

### 📫 Contact

**Email:** [truongvankhai0906@gmail.com](mailto:truongvankhai0906@gmail.com)
**GitHub:** VanKhaiii

---
