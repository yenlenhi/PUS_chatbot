# Phương Án Ưu Tiên Tài Liệu Tuyển Sinh 2026

## Mục tiêu

Đảm bảo chatbot trả lời theo nguyên tắc:

1. Nếu người dùng hỏi rõ `2026`, chỉ ưu tiên tài liệu tuyển sinh `2026`.
2. Nếu người dùng hỏi về `năm nay`, `mới nhất`, hoặc không nêu năm nhưng ngữ cảnh là tuyển sinh hiện tại, mặc định ưu tiên chu kỳ tuyển sinh hiện hành (`2026` theo ngày hệ thống).
3. Tài liệu cũ hơn như `2025`, `2024` chỉ dùng để đối chiếu và phải nêu rõ năm.

## Thứ tự nguồn chính thống nên ưu tiên crawl / ingest

### Tầng 1: Website chính thức của Trường

- `https://dhannd.bocongan.gov.vn/Thong-tin-tuyen-sinh/truong-dai-hoc-an-ninh-nhan-dan-thong-bao-chi-tieu-tuyen-sinh-tuyen-moi-dao-tao-trinh-do-dai-hoc-nam-2026-a-4132`
  - Nội dung nêu rõ căn cứ `Quyết định số 523/QĐ-BCA-X01 ngày 30/01/2026` và `Công văn số 673/X02-P2 ngày 12/02/2026`.
  - Đây phải là nguồn ưu tiên số 1 cho các câu hỏi về chỉ tiêu tuyển sinh 2026 của Trường Đại học An ninh nhân dân.

### Tầng 2: Bộ Công an

- `https://bocongan.gov.vn/bai-viet/trien-khai-cong-tac-tuyen-sinh-cand-nam-2026-dap-ung-yeu-cau-xay-dung-luc-luong-cand-trong-tinh-hinh-moi-1770632323`
  - Bài ngày `09/02/2026`.
  - Dùng để lấy bối cảnh chính thức toàn ngành CAND năm 2026.
  - Phù hợp cho các câu hỏi về tiến độ công bố, định hướng tuyển sinh, nguyên tắc triển khai.

### Tầng 3: Văn bản chỉ đạo / chính sách cấp Bộ, Chính phủ

- `https://bocongan.gov.vn/chinh-sach-phap-luat/bai-viet/sua-doi-bo-sung-mot-so-dieu-quy-dinh-ve-tuyen-sinh-trong-cong-an-nhan-dan-1763109496`
  - Dùng khi cần căn cứ quy phạm hoặc sửa đổi quy định tuyển sinh trong CAND.
- Các trang thuộc `chinhphu.vn` hoặc `xaydungchinhsach.chinhphu.vn`
  - Chỉ dùng làm nguồn bổ trợ khi Trường hoặc Bộ chưa đăng đủ tài liệu triển khai chi tiết.

## Quy tắc ingest dữ liệu

### 1. Tách riêng tài liệu tuyển sinh theo năm

- Mỗi tài liệu cần có ít nhất các metadata:
  - `document_year`
  - `source_url`
  - `source_authority`
  - `document_type`
- `document_year` phải được trích từ:
  - tên file
  - URL nguồn
  - tiêu đề tài liệu

### 2. Chỉ ingest tài liệu chính thức

- Ưu tiên ingest:
  - thông báo tuyển sinh
  - hướng dẫn tuyển sinh
  - chỉ tiêu tuyển sinh
  - ngưỡng đảm bảo chất lượng đầu vào
  - kế hoạch tuyển sinh
- Hạn chế hoặc hạ điểm:
  - tài liệu dự thảo
  - tài liệu không rõ nguồn
  - tài liệu chỉ là bản scan không xác định được năm / cơ quan ban hành

### 3. Duy trì registry URL nguồn

- `data/pdf_urls.json` nên được dùng như bảng ánh xạ:
  - `filename -> official_url`
  - từ đó suy ra:
    - domain chính thống
    - mức độ ưu tiên nguồn
    - năm tài liệu

## Quy tắc retrieval / ranking

### Nếu query có năm rõ ràng

- Ví dụ: `điểm chuẩn 2025`, `chỉ tiêu 2026`
- Chỉ tăng điểm cho tài liệu đúng năm.
- Tài liệu khác năm bị trừ điểm.

### Nếu query không có năm nhưng là câu hỏi tuyển sinh

- Ví dụ:
  - `chỉ tiêu tuyển sinh`
  - `phương thức xét tuyển`
  - `hồ sơ tuyển sinh`
  - `điểm chuẩn mới nhất`
- Mặc định coi đây là câu hỏi cho chu kỳ hiện tại.
- Theo ngày hệ thống hiện tại, chu kỳ mặc định là `2026`.

### Nếu có nhiều nguồn cùng năm

- Xếp hạng:
  1. Website chính thức của Trường
  2. Bộ Công an
  3. Chính phủ / cổng chính sách
  4. Nguồn còn lại

## Quy tắc trả lời

- Nếu context có cả `2026` và `2025`:
  - dùng `2026` làm căn cứ chính
  - chỉ nhắc `2025` khi người dùng yêu cầu so sánh hoặc khi cần giải thích thay đổi
- Nếu chưa có đủ tài liệu `2026`:
  - nói rõ phần nào đã có căn cứ 2026
  - phần nào mới chỉ có căn cứ 2025 hoặc quy định khung
  - không suy diễn các mốc chưa công bố

## Việc đã nối vào code

- Bổ sung utility `src/utils/admission_document_priority.py`
  - suy ra `document_year`
  - suy ra `source_url`
  - chấm điểm ưu tiên theo `năm + nguồn + loại tài liệu`
- Nối lớp ưu tiên này vào `RAGService._final_ranking()`
- Đưa metadata nguồn / năm vào `create_context()` để LLM nhìn thấy rõ tài liệu nào là 2026

## Checklist vận hành

1. Bổ sung đầy đủ URL tài liệu 2026 vào `data/pdf_urls.json`.
2. Upload / ingest các PDF tuyển sinh 2026 ngay khi Trường công bố file chính thức.
3. Rebuild BM25 và embeddings sau mỗi đợt cập nhật.
4. Chạy bộ test ưu tiên năm để chắc chắn `2026` luôn đứng trên `2025` khi query là tuyển sinh hiện tại.
