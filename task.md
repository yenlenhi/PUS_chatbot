## PHASE 1: THIẾT LẬP MÔI TRƯỜNG VÀ XỬ LÝ DỮ LIỆU

### Task 1: Thiết lập môi trường phát triển
- Tạo virtual environment Python
- Cài đặt các thư viện cần thiết: FastAPI, LangChain, FAISS, sentence-transformers, sqlite3, PyPDF2/pdfplumber, ollama
- Thiết lập cấu trúc thư mục dự án

### Task 2: Xử lý và trích xuất dữ liệu PDF
- Viết module đọc và trích xuất text từ 2 file PDF trong `data/pdfs/`
- Làm sạch và chuẩn hóa dữ liệu text (loại bỏ ký tự đặc biệt, format không mong muốn)
- Phân đoạn văn bản thành các chunk có kích thước phù hợp (300-500 tokens)
- Lưu trữ các chunk đã xử lý

## PHASE 2: XÂY DỰNG HỆ THỐNG EMBEDDING VÀ VECTOR DATABASE

### Task 3: Tạo embedding với Vietnamese SBERT
- Tải và cấu hình mô hình Vietnamese SBERT
- Tạo embedding cho tất cả các chunk văn bản
- Tối ưu hóa quá trình tạo embedding (batch processing)

### Task 4: Thiết lập SQLite database và FAISS index
- Thiết kế schema SQLite để lưu trữ:
  - Metadata của chunks (id, source_file, page_number, content)
  - Embedding vectors
- Tạo FAISS index từ các embedding vectors
- Viết các function CRUD cho database

### Task 5: Xây dựng hệ thống tìm kiếm similarity
- Implement similarity search với FAISS
- Tạo function truy vấn top-k documents liên quan
- Tối ưu hóa threshold và số lượng kết quả trả về

## PHASE 3: XÂY DỰNG HỆ THỐNG RAG

### Task 6: Thiết lập Ollama
- Cài đặt và cấu hình Ollama
- Pull và test một trong 2 model (myaniu/qwen2.5-1m hoặc deepseek-r1)
- Tạo connection và test API calls

### Task 7: Xây dựng RAG pipeline với LangChain
- Tạo custom retriever sử dụng FAISS index
- Thiết kế prompt template phù hợp với ngữ cảnh tư vấn tuyển sinh
- Implement RAG chain kết hợp retriever + LLM
- Xử lý context window và token limits

### Task 8: Tối ưu hóa prompt engineering
- Thiết kế system prompt cho domain tư vấn tuyển sinh
- Tạo few-shot examples
- Implement context compression nếu cần
- Test và fine-tune prompt templates

## PHASE 4: XÂY DỰNG API BACKEND

### Task 9: Xây dựng FastAPI endpoints
- Endpoint `/chat`: nhận câu hỏi và trả về câu trả lời
- Endpoint `/health`: kiểm tra trạng thái hệ thống
- Endpoint `/search`: tìm kiếm documents liên quan (optional)
- Implement request/response models với Pydantic

### Task 10: Xử lý lỗi và logging
- Implement error handling cho từng component
- Thiết lập logging system
- Validate input và sanitize output
- Rate limiting và security measures

## PHASE 5: TESTING VÀ OPTIMIZATION

### Task 11: Unit testing và integration testing
- Test từng component riêng biệt
- Test end-to-end workflow
- Tạo test dataset với các câu hỏi mẫu
- Performance testing

### Task 12: Tối ưu hóa hiệu suất
- Optimize database queries
- Implement caching cho frequent queries
- Optimize FAISS index parameters
- Monitor memory usage và response time

## CẤU TRÚC THỦ MỤC ĐỀ XUẤT:
```
chatbot-tuyensinh/
├── data/
│   ├── pdfs/          # PDF files nguồn
│   ├── processed/     # Processed chunks
│   └── embeddings/    # FAISS index và SQLite DB
├── src/
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   ├── utils/         # Utility functions
│   └── api/           # FastAPI routes
├── tests/
├── config/
└── requirements.txt
```