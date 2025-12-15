# Hướng dẫn sử dụng tính năng File Attachments

## Tổng quan

Tính năng File Attachments cho phép chatbot đính kèm các file (forms, templates, documents) trong câu trả lời để hỗ trợ người dùng tốt hơn.

**Ví dụ:**
- User: "Cho tôi xin form đơn xin nghỉ học có phép quá 5 ngày"
- Bot: "Nghỉ có phép quá 5 ngày cần sự xác nhận của hiệu trưởng. Bạn hãy điền vào form này: [📄 FORM_XIN_NGHI_HOC.doc]"

## Cấu trúc Database

### Bảng `document_attachments`
Lưu trữ thông tin về các file đính kèm:
- `id`: ID tự động tăng
- `file_name`: Tên file
- `file_type`: Loại file (doc, docx, xlsx, pdf)
- `file_path`: Đường dẫn lưu file
- `file_size`: Kích thước file (bytes)
- `description`: Mô tả file
- `keywords`: Mảng keywords để search
- `is_active`: Trạng thái active/inactive

### Bảng `chunk_attachments`
Liên kết attachments với chunks (many-to-many):
- `chunk_id`: ID của chunk
- `attachment_id`: ID của attachment
- `relevance_score`: Điểm liên quan (0-1)

## API Endpoints

### 1. Upload Attachment
```bash
POST /api/v1/attachments/upload
Content-Type: multipart/form-data

Parameters:
- file: File (required) - .doc, .docx, .xlsx, .xls, .pdf (max 10MB)
- description: string (optional) - Mô tả file
- keywords: string (optional) - Keywords phân cách bằng dấu phẩy
- chunk_ids: string (optional) - Chunk IDs phân cách bằng dấu phẩy

Response:
{
  "id": 1,
  "file_name": "FORM_XIN_NGHI_HOC.doc",
  "file_type": "doc",
  "file_size": 45056,
  "description": "Form xin nghỉ học có phép quá 5 ngày",
  "keywords": ["form", "nghỉ học", "đơn xin nghỉ"],
  "download_url": "/api/v1/attachments/download/1"
}
```

### 2. Download Attachment
```bash
GET /api/v1/attachments/download/{attachment_id}

Response: File binary data
```

### 3. List Attachments
```bash
GET /api/v1/attachments?keywords=form,nghỉ học&file_name=FORM

Response:
[
  {
    "id": 1,
    "file_name": "FORM_XIN_NGHI_HOC.doc",
    ...
  }
]
```

### 4. Delete Attachment (Soft Delete)
```bash
DELETE /api/v1/attachments/{attachment_id}

Response:
{
  "success": true,
  "message": "Attachment deleted successfully"
}
```

### 5. Link Attachment to Chunks
```bash
POST /api/v1/attachments/{attachment_id}/link-chunks
Content-Type: application/json

Body:
{
  "chunk_ids": [1, 5, 10],
  "relevance_score": 1.0
}
```

## Sử dụng qua Admin Interface

### Bước 1: Truy cập Admin Dashboard
1. Đăng nhập vào admin: `http://localhost:3000/admin`
2. Chọn menu "File đính kèm" từ sidebar

### Bước 2: Upload File mới
1. Click nút "Upload File Mới"
2. Chọn file (.doc, .docx, .xlsx, .xls, .pdf)
3. Điền thông tin:
   - **Mô tả**: Mô tả ngắn về file (tùy chọn)
   - **Keywords**: Từ khóa để tìm kiếm, phân cách bằng dấu phẩy
     - Ví dụ: `form, đơn, nghỉ học, xin phép`
   - **Chunk IDs**: Link với chunks cụ thể (tùy chọn)
     - Ví dụ: `1, 5, 10` - chatbot sẽ đính kèm file này khi trả lời từ các chunks này
4. Click "Upload"

### Bước 3: Quản lý Files
- **Tìm kiếm**: Dùng thanh search để tìm file theo tên hoặc mô tả
- **Tải về**: Click nút "Tải về" để download file
- **Xóa**: Click icon thùng rác để xóa file (soft delete)

## Cách hoạt động

### 1. Backend Flow
```
User Query → RAG Retrieval → Retrieved Chunks
    ↓
Check chunks for linked attachments
    ↓
Include attachments in response
```

### 2. Attachment Service
```python
# In rag_service.py
chunk_ids = [chunk["id"] for chunk in relevant_chunks]
attachments = self.attachment_service.get_attachments_by_chunk_ids(chunk_ids)
```

### 3. Response Format
```json
{
  "answer": "...",
  "sources": [...],
  "attachments": [
    {
      "file_name": "FORM_XIN_NGHI_HOC.doc",
      "file_type": "doc",
      "download_url": "/api/v1/attachments/download/1",
      "description": "Form xin nghỉ học có phép",
      "file_size": 45056
    }
  ],
  "confidence": 0.95
}
```

### 4. Frontend Display
File attachments hiển thị dưới câu trả lời với:
- Icon file và tên file
- Mô tả (nếu có)
- Kích thước file
- Nút download

## Linking Strategies

### Strategy 1: Link theo Keywords
Upload file với keywords phù hợp, chatbot tự động tìm:
```
Keywords: ["form", "nghỉ học", "đơn xin nghỉ", "xin phép"]
→ Khi user hỏi về "xin nghỉ học" → attachment được retrieve
```

### Strategy 2: Link trực tiếp với Chunks
Link file với specific chunks:
```
Chunk 123: "Quy định về nghỉ học có phép..."
Attachment ID 1 → linked to Chunk 123
→ Khi chunk 123 được retrieve → attachment được include
```

### Strategy 3: Kết hợp cả hai
- Set keywords để search
- Link với key chunks để đảm bảo xuất hiện

## Best Practices

### 1. Đặt tên file
- Dùng chữ IN HOA
- Không dấu
- Dùng underscore (_) để cách từ
- Ví dụ: `FORM_XIN_NGHI_HOC.doc`, `MAU_DON_XIN_HOC_BONG.docx`

### 2. Keywords
- Dùng từ khóa phổ biến mà user hay tìm
- Bao gồm cả từ viết tắt và đầy đủ
- Ví dụ: `["form", "mẫu đơn", "đơn xin nghỉ", "nghỉ phép", "xin phép nghỉ"]`

### 3. Description
- Viết mô tả ngắn gọn, rõ ràng
- Giúp admin và user hiểu rõ mục đích file
- Ví dụ: "Form xin nghỉ học có phép quá 5 ngày, cần chữ ký hiệu trưởng"

### 4. Chunk Linking
- Link với chunks quan trọng nhất
- Không cần link tất cả chunks liên quan
- Ví dụ: Chỉ link với chunk chính nói về quy định nghỉ học

## Troubleshooting

### Attachment không hiển thị
1. Kiểm tra file đã được link với chunks chưa
2. Kiểm tra keywords có phù hợp với query không
3. Kiểm tra `is_active = TRUE` trong database

### File không download được
1. Kiểm tra file còn tồn tại trong `data/forms/`
2. Kiểm tra permission của thư mục
3. Kiểm tra đường dẫn `file_path` trong database

### Upload failed
1. Kiểm tra file size < 10MB
2. Kiểm tra file type (doc, docx, xlsx, xls, pdf)
3. Kiểm tra quyền ghi vào `data/forms/`

## Examples

### Example 1: Form xin nghỉ học
```python
# Upload via API
curl -X POST "http://localhost:8000/api/v1/attachments/upload" \
  -F "file=@FORM_XIN_NGHI_HOC.doc" \
  -F "description=Form xin nghỉ học có phép quá 5 ngày" \
  -F "keywords=form,nghỉ học,đơn xin nghỉ,xin phép" \
  -F "chunk_ids=123,124,125"
```

### Example 2: Mẫu đơn xin học bổng
```python
# Upload via Admin UI
File: MAU_DON_XIN_HOC_BONG.docx
Description: Mẫu đơn xin học bổng khuyến khích học tập
Keywords: học bổng, đơn xin, mẫu đơn, khuyến khích học tập
Chunk IDs: 200, 201, 202
```

### Example 3: Lịch học kỳ
```python
File: LICH_HOC_KY_2024_2025.xlsx
Description: Lịch học kỳ 1 năm học 2024-2025
Keywords: lịch học, thời khóa biểu, học kỳ
Chunk IDs: (leave empty - will match by keywords)
```

## Technical Notes

### Database Indexes
- `idx_attachments_filename`: Fast filename search
- `idx_attachments_keywords`: GIN index for keyword array search
- `idx_chunk_attachments_chunk`: Fast chunk → attachment lookup
- `idx_chunk_attachments_attachment`: Fast attachment → chunk lookup

### File Storage
- Files stored in: `data/forms/`
- Max file size: 10MB
- Allowed types: doc, docx, xlsx, xls, pdf

### API Rate Limits
- No rate limits currently
- Consider adding if needed in production

## Future Enhancements

1. **Cloud Storage Integration**
   - AWS S3, Google Cloud Storage
   - CDN for faster downloads

2. **Version Control**
   - Track file versions
   - Update history

3. **Preview Generation**
   - Generate thumbnails for documents
   - PDF preview in browser

4. **Analytics**
   - Track download counts
   - Popular attachments

5. **Advanced Linking**
   - Auto-link based on content similarity
   - ML-based relevance scoring
