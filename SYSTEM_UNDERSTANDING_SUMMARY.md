# 📚 Tóm Tắt Hiểu Sâu Hệ Thống Uni Bot

## 🎯 Hệ Thống Là Gì?

**Uni Bot** là một **Chatbot AI thông minh** giúp trả lời câu hỏi về tuyển sinh cho Trường Đại học An ninh Nhân dân. Nó sử dụng công nghệ **RAG (Retrieval-Augmented Generation)** để tìm kiếm thông tin chính xác từ tài liệu và tạo câu trả lời tự nhiên.

## 🔄 Cách Hoạt Động (Đơn Giản)

```
Người dùng hỏi → Tìm kiếm thông tin liên quan → Tạo câu trả lời → Hiển thị kết quả
```

### Chi Tiết:
1. **Nhận câu hỏi**: "Các ngành đào tạo là gì?"
2. **Chuyển thành vector**: Máy tính hiểu được
3. **Tìm kiếm**: Tìm 15 tài liệu tương tự nhất
4. **Xếp hạng**: Chọn 5 tài liệu tốt nhất
5. **Tạo câu trả lời**: Sử dụng AI để tạo câu trả lời tự nhiên
6. **Hiển thị**: Câu trả lời + nguồn tài liệu

## 🏗️ Kiến Trúc (3 Tầng)

```
┌─────────────────────────────────────────┐
│ Frontend (Next.js)                      │
│ - Chat Interface                        │
│ - Floating Button                       │
└─────────────────────────────────────────┘
              ↓ HTTP API
┌─────────────────────────────────────────┐
│ Backend (FastAPI)                       │
│ - RAG Service (Orchestrator)            │
│ - Embedding Service                     │
│ - Database Service                      │
│ - LLM Service                           │
└─────────────────────────────────────────┘
              ↓ SQL/Vector
┌─────────────────────────────────────────┐
│ Data Layer                              │
│ - SQLite Database                       │
│ - FAISS Vector Index                    │
│ - PDF Files                             │
└─────────────────────────────────────────┘
```

## 🧠 Các Khái Niệm Quan Trọng

### 1. Vector Embeddings
- Chuyển text thành dãy số (384 số)
- Cho phép máy tính hiểu ý nghĩa
- Ví dụ: "Các ngành đào tạo" ≈ "Ngành học của trường"

### 2. FAISS Index
- Lưu trữ tất cả vectors
- Tìm kiếm nhanh (10ms thay vì phải so sánh tất cả)
- Giống như chỉ mục trong sách

### 3. Reranking
- Lấy 15 kết quả từ FAISS
- Sử dụng AI để xếp hạng lại
- Chọn 5 tốt nhất

### 4. LLM (AI Model)
- Tạo câu trả lời tự nhiên
- Kết hợp thông tin từ nhiều tài liệu
- Ví dụ: Ollama (local) hoặc Gemini (cloud)

### 5. Conversation Memory
- Lưu lịch sử hội thoại
- Giúp AI hiểu context
- Cho phép hỏi tiếp theo

## 📊 Luồng Xử Lý Chi Tiết

```
User Input
    ↓
Frontend gửi tới Backend
    ↓
RAGService nhận yêu cầu
    ↓
1. EmbeddingService: Chuyển câu hỏi thành vector
    ↓
2. FAISS: Tìm 15 chunks tương tự
    ↓
3. DatabaseService: Lấy nội dung chunks
    ↓
4. Reranker: Xếp hạng lại, chọn top 5
    ↓
5. LLMService: Tạo câu trả lời
    ↓
6. RAGService: Kết hợp kết quả
    ↓
Backend trả về JSON
    ↓
Frontend hiển thị
    ↓
User thấy câu trả lời + nguồn
```

**Thời gian**: ~1-2 giây

## 🔧 Các Dịch Vụ Core

| Dịch Vụ | Chức Năng |
|---------|----------|
| **RAGService** | Điều phối toàn bộ quy trình |
| **EmbeddingService** | Chuyển text thành vector |
| **DatabaseService** | Quản lý SQLite database |
| **OllamaService** | Gửi prompt tới Ollama LLM |
| **GeminiService** | Gửi prompt tới Gemini LLM |

## 📁 Cấu Trúc Thư Mục

```
uni_bot/
├── main.py                    # Entry point
├── config/settings.py         # Cấu hình
├── src/
│   ├── api/routes.py         # API endpoints
│   ├── services/             # Business logic
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   ├── database_service.py
│   │   └── ...
│   └── utils/                # Utilities
├── frontend/                 # Next.js app
├── data/
│   ├── pdfs/                # Source PDFs
│   ├── processed/           # Processed chunks
│   └── embeddings/          # FAISS index + DB
└── scripts/                 # Utility scripts
```

## 🚀 Bắt Đầu Nhanh

### Backend
```bash
conda create -n uni_bot python=3.11 -y
conda activate uni_bot
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Ollama
```bash
ollama serve
ollama pull llama3
```

## 🔗 API Endpoints

| Endpoint | Mục Đích |
|----------|---------|
| `POST /api/v1/chat` | Trả lời câu hỏi |
| `POST /api/v1/search` | Tìm kiếm tài liệu |
| `GET /api/v1/health` | Kiểm tra sức khỏe |
| `GET /api/v1/stats` | Thống kê hệ thống |

## 📈 Hiệu Suất

- **Response Time**: 1-2 giây
- **Embedding**: ~100ms
- **Vector Search**: ~10ms
- **Reranking**: ~50ms
- **LLM Generation**: ~500-1000ms

## 🎯 Tại Sao Thiết Kế Này?

✅ **RAG**: Câu trả lời chính xác từ tài liệu
✅ **Vietnamese Embedding**: Tối ưu cho tiếng Việt
✅ **FAISS**: Tìm kiếm nhanh
✅ **Ollama + Gemini**: Linh hoạt, có fallback
✅ **Conversation Memory**: Hiểu context

## 📚 Tài Liệu Chi Tiết

Tôi đã tạo Memory Bank với các file:
- `projectbrief.md` - Tổng quan dự án
- `productContext.md` - Bối cảnh sản phẩm
- `systemPatterns.md` - Kiến trúc & patterns
- `techContext.md` - Công nghệ & setup
- `activeContext.md` - Trạng thái hiện tại
- `progress.md` - Tiến độ phát triển
- `DEEP_DIVE_EXPLANATION.md` - Giải thích chi tiết
- `QUICK_REFERENCE.md` - Tài liệu tham khảo nhanh

## 💡 Ví Dụ Thực Tế

### Người dùng hỏi: "Học phí bao nhiêu?"

```
1. Frontend gửi: "Học phí bao nhiêu?"
2. Embedding: Chuyển thành vector
3. FAISS: Tìm chunks về học phí
4. Reranker: Xếp hạng, chọn top 5
5. LLM: Tạo câu trả lời
6. Response: "Học phí năm 2024 là... Ngoài ra..."
7. Frontend: Hiển thị câu trả lời + nguồn
```

## 🎓 Tiếp Theo

1. **Đọc tài liệu**: Bắt đầu với `projectbrief.md`
2. **Chạy hệ thống**: Setup backend + frontend
3. **Hỏi câu hỏi**: Test chatbot
4. **Khám phá code**: Xem `src/services/rag_service.py`
5. **Hiểu sâu**: Đọc `DEEP_DIVE_EXPLANATION.md`

## ✨ Điểm Mạnh

- ✅ Câu trả lời chính xác (từ tài liệu)
- ✅ Hỗ trợ tiếng Việt tốt
- ✅ Có thể cập nhật tài liệu dễ dàng
- ✅ Có thể truy vết nguồn
- ✅ Không cần fine-tune LLM
- ✅ Linh hoạt (Ollama + Gemini)

## 🔮 Hướng Phát Triển

- Persistent conversation storage
- User authentication
- Admin dashboard
- Analytics
- Production deployment
- Mobile app
- Voice interface

---

**Bây giờ bạn đã hiểu sâu hệ thống! 🎉**

Hãy bắt đầu bằng cách:
1. Đọc `memory-bank/projectbrief.md`
2. Chạy hệ thống
3. Hỏi một câu hỏi
4. Xem logs để hiểu luồng
5. Khám phá code

