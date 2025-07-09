# University Chatbot - Hệ thống Chatbot Tuyển sinh

Hệ thống chatbot tư vấn tuyển sinh cho Trường Đại học An ninh Nhân dân sử dụng công nghệ RAG (Retrieval-Augmented Generation).

## Tính năng

- **Trả lời câu hỏi tự động**: Sử dụng AI để trả lời các câu hỏi về tuyển sinh
- **Tìm kiếm thông tin**: Tìm kiếm trong tài liệu tuyển sinh
- **Hỗ trợ tiếng Việt**: Được tối ưu hóa cho tiếng Việt
- **API RESTful**: Cung cấp API để tích hợp với các ứng dụng khác

## Công nghệ sử dụng

- **FastAPI**: Web framework cho API backend
- **LangChain**: Framework cho RAG pipeline
- **FAISS**: Vector database cho similarity search
- **Sentence Transformers**: Vietnamese SBERT cho embedding
- **Ollama**: Local LLM server
- **SQLite**: Database lưu trữ chunks và metadata

## Cài đặt

### 1. Tạo conda environment

```bash
conda create -n uni_bot python=3.11 -y
conda activate uni_bot
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình environment

Sao chép file `.env.example` thành `.env` và cấu hình các thông số:

```bash
cp .env.example .env
```

### 4. Cài đặt và chạy Ollama

Tải và cài đặt Ollama từ: https://ollama.ai

Chạy Ollama server:
```bash
ollama serve
```

Pull model (chọn một trong hai):
```bash
# Option 1: Qwen2.5 1M context
ollama pull myaniu/qwen2.5-1m

# Option 2: DeepSeek R1
ollama pull deepseek-r1
```

## Sử dụng

### 1. Xử lý dữ liệu PDF

```bash
python scripts/process_pdfs.py
```

### 2. Xây dựng embeddings và FAISS index

```bash
python scripts/build_embeddings.py
```

### 3. Test RAG system (tùy chọn)

```bash
python scripts/test_rag.py
```

### 4. Chạy API server

```bash
python scripts/run_server.py
```

Hoặc:

```bash
python main.py
```

API sẽ chạy tại: http://localhost:8000

## API Endpoints

### Chat
```
POST /api/v1/chat
```

Request body:
```json
{
  "question": "Điều kiện tuyển sinh vào trường là gì?",
  "conversation_id": "optional-conversation-id"
}
```

Response:
```json
{
  "answer": "Để được tuyển sinh vào trường...",
  "sources": ["tuyen_sinh_2025.pdf (Trang 5)"],
  "confidence": 0.85,
  "conversation_id": "uuid-string"
}
```

### Search
```
POST /api/v1/search
```

Request body:
```json
{
  "query": "học phí",
  "top_k": 5
}
```

### Health Check
```
GET /api/v1/health
```

### Statistics
```
GET /api/v1/stats
```

## Cấu trúc thư mục

```
uni_bot/
├── data/
│   ├── pdfs/              # File PDF nguồn
│   ├── processed/         # Chunks đã xử lý
│   └── embeddings/        # FAISS index và SQLite DB
├── src/
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── api/               # FastAPI routes
├── scripts/               # Scripts tiện ích
├── config/                # Cấu hình
├── tests/                 # Unit tests
├── main.py               # FastAPI application
└── requirements.txt      # Dependencies
```

## Development

### Chạy tests

```bash
pytest tests/
```

### Code formatting

```bash
black src/ scripts/ main.py
flake8 src/ scripts/ main.py
```

## Troubleshooting

### 1. Lỗi import sentence-transformers

Cập nhật dependencies:
```bash
pip install --upgrade sentence-transformers==2.7.0 huggingface-hub==0.20.3
```

### 2. Ollama không kết nối được

Kiểm tra Ollama service:
```bash
ollama list
curl http://localhost:11434/api/tags
```

### 3. FAISS index không tìm thấy

Chạy lại script build embeddings:
```bash
python scripts/build_embeddings.py
```

### 4. Không có dữ liệu PDF

Đảm bảo có file PDF trong thư mục `data/pdfs/` và chạy:
```bash
python scripts/process_pdfs.py
```

## Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## License

MIT License
