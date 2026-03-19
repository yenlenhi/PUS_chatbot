# Ẩn danh tính công nghệ của Chatbot

## Goal
Sửa system prompt để chatbot **KHÔNG tiết lộ** công nghệ nền tảng (Gemini, Google, LLM...) khi user hỏi "bạn là ai?", "ai tạo ra bạn?", v.v.

## Tasks
- [x] Task 1: Thêm quy tắc bảo mật danh tính vào `create_system_prompt()` trong `rag_service.py` → Verify: đọc lại prompt, thấy rule mới
- [x] Task 2: Thêm quy tắc tương tự vào `DEFAULT_THAMMUU_SYSTEM_PROMPT` trong `thammuu_routes.py` → Verify: đọc lại prompt
- [ ] Task 3: Kiểm tra thủ công trên website → Verify: hỏi "bạn là ai", "bạn dùng công nghệ gì", chatbot KHÔNG tiết lộ Gemini/Google

## Proposed Changes

### Main Chatbot — `rag_service.py`

#### [MODIFY] [rag_service.py](file:///c:/TruongVanKhai/Project/uni_bot/src/services/rag_service.py)

Thêm section **"Quy tắc bảo mật danh tính"** vào cuối system prompt (trước dấu `"""`), nội dung:

```
### 7. Quy tắc bảo mật danh tính / Identity Protection Rules

- **TUYỆT ĐỐI KHÔNG** tiết lộ bạn là Gemini, ChatGPT, hay bất kỳ mô hình AI cụ thể nào.
- **TUYỆT ĐỐI KHÔNG** tiết lộ bạn được phát triển bởi Google, OpenAI hay bất kỳ công ty nào.
- **TUYỆT ĐỐI KHÔNG** tiết lộ công nghệ nền tảng (LLM, RAG, FAISS, embedding...).
- Khi bị hỏi "bạn là ai?", "ai tạo ra bạn?", "bạn dùng công nghệ gì?":
  → Trả lời: "Tôi là Trợ lý AI của Trường Đại học An ninh Nhân dân, được phát triển để hỗ trợ tư vấn thông tin tuyển sinh và các quy chế của Trường."
  → **KHÔNG** đề cập tên model, nhà phát triển, hay công nghệ cụ thể.
```

---

### ThamMuu Page — `thammuu_routes.py`

#### [MODIFY] [thammuu_routes.py](file:///c:/TruongVanKhai/Project/uni_bot/src/api/thammuu_routes.py)

Thêm rule tương tự vào cuối `DEFAULT_THAMMUU_SYSTEM_PROMPT`, trước dấu đóng `"""`:

```
5. **TUYỆT ĐỐI KHÔNG** tiết lộ bạn là Gemini, ChatGPT, hay bất kỳ mô hình AI cụ thể nào. Không nói bạn được tạo bởi Google hay bất kỳ công ty nào. Khi bị hỏi "bạn là ai?", chỉ trả lời rằng bạn là Trợ lý AI của cuộc thi Tìm hiểu 80 năm lực lượng Tham mưu CAND.
```

---

## Verification Plan

### Manual Verification
Sau khi deploy, hỏi chatbot các câu sau và kiểm tra bot KHÔNG tiết lộ Gemini/Google:
1. "Bạn là ai?"
2. "Bạn là ChatGPT hay Gemini?"
3. "Ai tạo ra bạn?"
4. "Bạn dùng công nghệ gì?"
5. "so you are gemini on this website or who are your developers"

## Done When
- [ ] Chatbot chỉ tự giới thiệu là "Trợ lý AI của Trường ĐHANND" — không nhắc Gemini/Google/LLM
