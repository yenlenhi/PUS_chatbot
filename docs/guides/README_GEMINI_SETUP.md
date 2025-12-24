# Hướng dẫn cài đặt và sử dụng Gemini PDF Processing

## Tổng quan

Hệ thống đã được nâng cấp để sử dụng **Gemini Vision API** để trích xuất text từ cả PDF thường và PDF scan, cải thiện đáng kể chất lượng OCR cho các tài liệu được scan.

## Cấu trúc thư mục PDF

```
data/
├── pdfs/           # PDF có thể copy được (sử dụng phương pháp truyền thống)
└── new_pdf/        # PDF scan (sử dụng Gemini Vision API)
```

## Cài đặt

### 1. Cài đặt dependencies bổ sung

```bash
pip install -r requirements_gemini.txt
```

Hoặc cài đặt thủ công:
```bash
pip install PyMuPDF>=1.23.0 Pillow>=10.0.0
```

### 2. Cấu hình Gemini API

Thêm vào file `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
```

Để lấy API key:
1. Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Tạo API key mới
3. Copy và paste vào file `.env`

## Sử dụng

### 1. Test hệ thống

```bash
python scripts/test_gemini_pdf.py
```

Script này sẽ kiểm tra:
- Kết nối Gemini API
- Thư mục PDF và files
- Trích xuất text từ PDF thường
- Trích xuất text từ PDF scan với Gemini
- Tạo chunks hoàn chỉnh

### 2. Xử lý PDF với các chế độ khác nhau

#### Chế độ mặc định (sử dụng Gemini cho tất cả):
```bash
python scripts/process_pdfs.py
```

#### Chế độ ưu tiên Gemini (khuyến nghị):
```bash
python scripts/process_pdfs.py --gemini-priority
```
- PDF thường (data/pdfs): Sử dụng phương pháp truyền thống (nhanh hơn)
- PDF scan (data/new_pdf): Sử dụng Gemini Vision API (chất lượng cao hơn)

#### Chế độ không sử dụng Gemini:
```bash
python scripts/process_pdfs.py --no-gemini
```

### 3. Xây dựng embeddings

Sau khi xử lý PDF thành công:
```bash
python scripts/build_embeddings.py
```

### 4. Chạy hệ thống

```bash
python main.py
```

## Tính năng mới

### GeminiPDFService

- **Chuyển đổi PDF thành hình ảnh**: Sử dụng PyMuPDF với độ phân giải cao
- **OCR với Gemini Vision**: Trích xuất text chính xác từ hình ảnh
- **Xử lý batch**: Xử lý nhiều trang với rate limiting
- **Retry logic**: Tự động thử lại khi gặp lỗi
- **Tối ưu hóa**: Nén hình ảnh và quản lý memory

### PDFProcessor nâng cấp

- **Dual processing**: Hỗ trợ cả PDF thường và PDF scan
- **Fallback mechanism**: Tự động chuyển sang phương pháp truyền thống nếu Gemini thất bại
- **Flexible configuration**: Có thể bật/tắt Gemini cho từng file
- **Enhanced logging**: Log chi tiết quá trình xử lý

## Troubleshooting

### 1. Lỗi Gemini API

```
Error: GEMINI_API_KEY is not set
```
**Giải pháp**: Đảm bảo đã set GEMINI_API_KEY trong file `.env`

### 2. Lỗi rate limiting

```
Rate limited, waiting Xs before retry
```
**Giải pháp**: Hệ thống tự động retry, chờ hoàn thành

### 3. Lỗi PyMuPDF

```
ImportError: No module named 'fitz'
```
**Giải pháp**: 
```bash
pip install PyMuPDF
```

### 4. Lỗi memory với PDF lớn

**Giải pháp**: Hệ thống tự động tối ưu hóa hình ảnh và xử lý theo batch

## Performance

### So sánh hiệu suất:

| Phương pháp | PDF thường | PDF scan | Tốc độ | Chất lượng |
|-------------|------------|----------|---------|------------|
| Traditional | ✓ Tốt | ✗ Kém | Nhanh | Trung bình |
| Gemini | ✓ Tốt | ✓ Xuất sắc | Chậm hơn | Cao |
| Hybrid (khuyến nghị) | ✓ Tốt | ✓ Xuất sắc | Tối ưu | Cao |

### Khuyến nghị:

- **Sử dụng `--gemini-priority`** cho hiệu suất và chất lượng tối ưu
- **PDF thường**: Phương pháp truyền thống (nhanh, đủ chất lượng)
- **PDF scan**: Gemini Vision API (chậm hơn nhưng chất lượng cao)

## Monitoring

Theo dõi logs để kiểm tra tiến trình:
```bash
tail -f logs/chatbot.log
```

Các thông tin quan trọng:
- Số lượng PDF được xử lý
- Số trang trích xuất thành công
- Số chunks được tạo
- Lỗi và warnings
