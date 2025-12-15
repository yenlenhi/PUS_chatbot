# CHƯƠNG 5: CHƯƠNG TRÌNH MINH HỌA (DEMO HỆ THỐNG)

Chương này giới thiệu tổng quan các trang và tính năng đã xây dựng của hệ thống UniChatBot, kèm các luồng thao tác mẫu để minh họa cách sử dụng.

## MỤC LỤC

1. [Tổng quan hệ thống](#51-tổng-quan-hệ-thống)
2. [Trang Chatbot người dùng](#52-trang-chatbot-người-dùng)
3. [Bảng điều khiển (Admin Dashboard)](#53-bảng-điều-khiển-admin-dashboard)
4. [Quản lý tài liệu](#54-quản-lý-tài-liệu)
5. [Tra cứu và truy vấn RAG](#55-tra-cứu-và-truy-vấn-rag)
6. [Thống kê và Phân tích](#56-thống-kê-và-phân-tích)
7. [Tích hợp và Cấu hình](#57-tích-hợp-và-cấu-hình)
8. [Luồng thao tác minh họa](#58-luồng-thao-tác-minh-họa)
9. [Hướng dẫn chạy nhanh (Try-it)](#59-hướng-dẫn-chạy-nhanh-try-it)
10. [Ghi chú kỹ thuật và hạn chế](#510-ghi-chú-kỹ-thuật-và-hạn-chế)

---

## 5.1. Tổng quan hệ thống

- Frontend: Next.js 15, React 19, Tailwind CSS, shadcn/ui
- Backend: FastAPI (Python), SQLAlchemy, Redis (cache)
- Database: PostgreSQL 16 với pgvector
- AI/ML: Vietnamese SBERT (384-dim), BM25, RRF fusion, Cross-Encoder reranking, Gemini 2.0 Flash (LLM + OCR)
- Container: Docker Compose (tùy chọn)

Hệ thống cung cấp 2 nhóm giao diện chính:
- Giao diện người dùng (Chat): hỏi đáp, xem câu trả lời và nguồn trích dẫn
- Giao diện quản trị (Admin): quản lý tài liệu, theo dõi xử lý, xem thống kê

---

## 5.2. Trang Chatbot người dùng

### Mục tiêu chức năng
- Nhập câu hỏi tiếng Việt, có hỗ trợ gợi ý và lịch sử.
- Trả lời theo RAG, có trích dẫn nguồn (tên file, trang) và điểm tin cậy.
- Hiển thị các trích đoạn nguồn, cho phép mở rộng/xem chi tiết.
- Trạng thái tải, lỗi thân thiện; đảm bảo khả năng truy cập (a11y).

### Bố cục UI & thành phần
- Thanh tiêu đề: logo, tiêu đề hệ thống, nút chuyển chế độ tối/sáng.
- Ô nhập câu hỏi: placeholder, đếm ký tự, nút gửi, phím Enter để gửi.
- Khu vực trả lời: văn bản định dạng, danh sách nguồn trích dẫn, điểm tin cậy.
- Thanh bên (tùy chọn): gợi ý câu hỏi, lịch sử phiên, bộ lọc chủ đề.

### Luồng thao tác chi tiết
1) Người dùng nhập câu hỏi và nhấn Gửi.
2) Hệ thống hiển thị spinner “Đang truy vấn…”.
3) Nhận câu trả lời, render nội dung, kèm danh sách nguồn (Top‑N). 
4) Người dùng có thể bấm vào nguồn để mở popover/đối thoại hiển thị trích đoạn đầy đủ.
5) Tùy chọn lưu câu hỏi vào lịch sử phiên hiện tại.

### Trạng thái & xử lý lỗi
- Loading: hiển thị skeleton/spinner và vô hiệu nút Gửi.
- Empty query: cảnh báo “Vui lòng nhập câu hỏi”.
- No results: thông báo “Không tìm thấy thông tin phù hợp trong nguồn dữ liệu” và gợi ý từ khóa.
- Server error: hiển thị mã lỗi, cho phép thử lại; tự động gửi telemetry tối thiểu.

### Khả năng truy cập (a11y)
- Focus rõ ràng cho ô nhập, nút; hỗ trợ phím tắt.
- Tương phản màu đáp ứng WCAG AA; vùng thông tin có aria‑labels.

### Hiệu năng & UX
- Debounce gợi ý câu hỏi: 300–500ms.
- Giới hạn độ dài câu hỏi: 500 ký tự; cảnh báo khi vượt.
- Streaming (nếu bật): hiển thị phần trả lời dần, cải thiện cảm nhận tốc độ.

### API hợp đồng
- Endpoint: `POST /api/v1/chat`
- Request body (JSON):
```json
{
	"query": "Điều kiện xét học bổng là gì?",
	"conversation_id": "optional-uuid"
}
```
- Response body (JSON):
```json
{
	"answer": "Theo quy chế...",
	"sources": [
		{
			"filename": "QUY_CHE_DAO_TAO.pdf",
			"pageNumber": 12,
			"content": "Điều kiện xét học bổng..."
		}
	],
	"confidence": 0.92,
	"processing_time": 1.84
}
```
- Mã lỗi: `400` (Invalid query), `500` (Server error), `503` (Service unavailable).

### Ví dụ hiển thị nguồn trích dẫn
```
[Nguồn 1] QUY_CHE_DAO_TAO.pdf — Trang 12
"Điều kiện xét học bổng: GPA ≥ 3.5; DRL ≥ 80; ..."
```

---

## 5.3. Bảng điều khiển (Admin Dashboard)

### Mục tiêu chức năng
- Quản lý vòng đời tài liệu: upload → xử lý → sẵn sàng truy xuất → cập nhật/xóa.
- Theo dõi tiến trình xử lý, lỗi và thống kê cơ bản theo tài liệu.
- Tác vụ hàng loạt: reprocess, xóa, khôi phục, lọc và phân trang.

### Bố cục UI & thành phần
- Thanh hành động: nút Upload, công tắc Auto‑Ingestion, nút Rebuild BM25.
- Bộ lọc: trạng thái (pending/processing/completed/failed), khoảng thời gian, từ khóa.
- Bảng tài liệu: các cột khuyến nghị:
	- `Filename` (tên tệp)
	- `Status` (pending/processing/completed/failed)
	- `Chunks` (tổng số đoạn)
	- `File Size` (dung lượng)
	- `Updated At` (thời gian cập nhật)
	- `Actions` (Details/Reprocess/Delete)
- Phân trang: `page`, `pageSize` (mặc định 50), hiển thị tổng số.

### Quy trình upload & xử lý
1) Chọn file PDF và nhấn Upload.
2) Backend lưu file tạm, tạo bản ghi `documents` (status = pending).
3) Thêm vào hàng đợi xử lý nền; status chuyển sang `processing`.
4) Sau khi hoàn tất: cập nhật `completed`, ghi `total_chunks`, thời gian xử lý.
5) Nếu lỗi: `failed` + `error_message`; cho phép retry.

### Tác vụ tài liệu
- Details: mở trang chi tiết, liệt kê các `chunks`, thống kê kích thước.
- Reprocess: xóa embeddings/chunks cũ, chạy lại pipeline với cấu hình mới.
- Delete:
	- Soft delete: đặt `is_active = false`, giữ dữ liệu để khôi phục.
	- Hard delete: xóa khỏi DB (cảnh báo không thể khôi phục).

### Trạng thái & thông báo
- Hiển thị tiến độ theo phần trăm (ước lượng theo số trang/chunks).
- Toast/alert cho thành công/thất bại, mã lỗi chi tiết.
- Thanh nhật ký (log panel) tùy chọn để giám sát theo thời gian thực.

### Phân quyền (RBAC)
- Vai trò: `admin`, `editor`, `viewer`.
- `admin`: toàn quyền; `editor`: upload/reprocess; `viewer`: chỉ xem.

### API hợp đồng
- Upload: `POST /api/v1/documents/upload`
	- Request: `multipart/form-data` (field `file`)
	- Response: `{ document_id, status: "processing" }`
- Liệt kê: `GET /api/v1/documents?status=&skip=&limit=`
	- Response: `{ documents: [...], total, skip, limit }`
- Chi tiết: `GET /api/v1/documents/{id}`
	- Response: `{ document, chunks: [...], statistics: {...} }`
- Reprocess: `POST /api/v1/documents/{id}/reprocess`
	- Response: `{ success: true, message: "Document reprocessing started" }`
- Xóa: `DELETE /api/v1/documents/{id}?hard_delete=false`
	- Response: `{ success: true, message }`

### Ví dụ trạng thái bảng
```
Filename               | Status     | Chunks | Size  | Updated At
-----------------------+------------+--------+-------+-------------------
QUY_CHE_DAO_TAO.pdf    | completed  | 45     | 2.3MB | 2025-12-09 21:10
TUYEN_SINH_2025.pdf    | processing | 32     | 1.8MB | 2025-12-10 08:42
QUY_DINH_HOC_PHI.pdf   | failed     | 0      | 0.9MB | 2025-12-10 09:05
```

### Phân tích chi tiết các trang con trong Admin

Để quản trị hiệu quả, Admin Dashboard được tổ chức thành nhiều trang chức năng chuyên biệt. Dưới đây là phân tích chi tiết và đề xuất cấu trúc cho từng trang con:

#### 1) Documents (Quản lý tài liệu)
- Mục tiêu: Quản lý vòng đời của tài liệu (upload → xử lý → tra cứu → cập nhật/xóa).
- Chức năng:
	- Upload PDF, xem danh sách, lọc (status/date/keyword), phân trang.
	- Chi tiết tài liệu: tổng quan, metadata, lịch sử xử lý, thống kê chunks.
	- Thao tác: Reprocess, Soft/Hard delete, Mark inactive/active.
- API:
	- `POST /api/v1/documents/upload`
	- `GET /api/v1/documents?status=&skip=&limit=`
	- `GET /api/v1/documents/{id}`
	- `POST /api/v1/documents/{id}/reprocess`
	- `DELETE /api/v1/documents/{id}?hard_delete=false`

#### 2) Processing Queue (Hàng đợi xử lý)
- Mục tiêu: Quan sát và kiểm soát các tác vụ xử lý PDF đang chạy.
- Chức năng:
	- Xem hàng đợi: số lượng nhiệm vụ, trạng thái từng job, ETA ước lượng.
	- Điều khiển: tạm dừng, tiếp tục, hủy job, ưu tiên xử lý tài liệu quan trọng.
	- Retry jobs thất bại; xem log chi tiết theo job.
- API (gợi ý):
	- `GET /api/v1/processing/queue`
	- `POST /api/v1/processing/jobs/{id}/pause|resume|cancel|retry`

#### 3) Embeddings (Quản lý vectors)
- Mục tiêu: Theo dõi số lượng embeddings, chất lượng và index vector.
- Chức năng:
	- Tổng quan: số embeddings, phân phối theo kích thước chunk, thời gian tạo.
	- Kiểm tra lỗi: phát hiện chunks không có embedding, chạy “repair”.
	- Quản lý index: IVFFlat `lists` hiện tại, gợi ý tối ưu theo số lượng rows.
- API (gợi ý):
	- `GET /api/v1/embeddings/stats`
	- `POST /api/v1/embeddings/repair-missing`
	- `POST /api/v1/embeddings/reindex?lists=...`

#### 4) Retrieval Settings (Thiết lập truy xuất)
- Mục tiêu: Điều chỉnh tham số ảnh hưởng tới chất lượng/tốc độ truy xuất.
- Chức năng:
	- Top‑K (retrieval), Top‑N (reranking), trọng số RRF.
	- Bật/tắt BM25, thay đổi tokenizer, ngôn ngữ tsvector (nếu dùng FTS).
	- Threshold confidence, tối đa số nguồn hiển thị.
- API (gợi ý):
	- `GET /api/v1/settings/retrieval`
	- `POST /api/v1/settings/retrieval` (cập nhật cấu hình)

#### 5) Analytics (Thống kê & báo cáo)
- Mục tiêu: Nắm bắt mức độ sử dụng và chất lượng hệ thống.
- Chức năng:
	- Dashboard: số lượt truy vấn/ngày, chủ đề phổ biến, thời gian phản hồi.
	- Chất lượng: Precision@5, tỷ lệ câu trả lời có trích dẫn hợp lệ.
	- Top tài liệu được tham chiếu; heatmap thời gian cao điểm.
- API:
	- `GET /api/v1/analytics/overview`
	- `GET /api/v1/analytics/queries?from=&to=`

#### 6) Users & Roles (Người dùng & phân quyền)
- Mục tiêu: Bảo mật và quản trị quyền hạn.
- Chức năng:
	- Quản lý tài khoản admin/editor/viewer; đặt mật khẩu, khóa/mở khóa.
	- Audit logs: ghi lại thao tác quan trọng (delete, reprocess, reindex).
- API (gợi ý):
	- `GET /api/v1/admin/users`
	- `POST /api/v1/admin/users`
	- `PATCH /api/v1/admin/users/{id}`
	- `GET /api/v1/admin/audit-logs`

#### 7) System Health (Sức khỏe hệ thống)
- Mục tiêu: Theo dõi tình trạng dịch vụ.
- Chức năng:
	- Health checks: DB/Redis/Watcher/Queue size; trạng thái `healthy/degraded`.
	- Thao tác: khởi động lại watcher, làm sạch queue.
- API:
	- `GET /api/v1/health`
	- `POST /api/v1/ingestion/watcher/restart`

#### 8) Logs (Nhật ký)
- Mục tiêu: Quan sát log theo module/thời gian.
- Chức năng:
	- Bộ lọc: cấp độ (INFO/WARN/ERROR), khoảng thời gian, dịch vụ.
	- Tải xuống log; xem chi tiết stack trace lỗi.
- API (gợi ý):
	- `GET /api/v1/logs?level=&from=&to=&service=`

#### 9) Config (Cấu hình hệ thống)
- Mục tiêu: Quản trị tham số vận hành.
- Chức năng:
	- Gemini OCR (bật/tắt), batch size embeddings, chunk sizes/overlap.
	- Đường dẫn watcher, ngưỡng index `lists`, tham số LLM (temperature).
- API:
	- `GET /api/v1/settings`
	- `POST /api/v1/settings` (cập nhật cấu hình)

#### 10) Integrations (Tích hợp)
- Mục tiêu: Kết nối hệ thống bên ngoài.
- Chức năng:
	- Webhook sau khi xử lý tài liệu (notify hệ thống quản lý văn bản).
	- Xuất dữ liệu: CSV/JSON các chunks/embeddings theo tiêu chí.
- API (gợi ý):
	- `POST /api/v1/integrations/webhooks`
	- `GET /api/v1/integrations/export?type=chunks|embeddings&from=&to=`

### Khuyến nghị UX cho Admin
- Nhóm chức năng theo tab rõ ràng; breadcrumbs cho trang chi tiết.
- Bổ sung xác nhận (confirm) trước thao tác destructive (hard delete/reindex).
- Hiển thị tiến trình theo bước (wizard) cho các thao tác phức tạp như reprocess.

### Bản đồ điều hướng (Admin Routes)

Các đường dẫn giao diện quản trị hiện có:

- `http://localhost:3000/admin/dashboard`
	- Tổng quan hệ thống: số lượng tài liệu, chunks, embeddings; 
		xu hướng truy vấn; cảnh báo sức khỏe (DB/Redis/Watcher/Queue).
	- Widgets đề xuất: “Tài liệu mới xử lý”, “Top tài liệu được trích dẫn”, “Thời gian phản hồi trung bình”.

- `http://localhost:3000/admin/chat-history`
	- Lịch sử hội thoại: danh sách phiên chat (ẩn thông tin nhạy cảm nếu cần),
		lọc theo thời gian/chủ đề, xem chi tiết câu hỏi–trả lời–nguồn.
	- Chức năng: tìm kiếm theo từ khóa, xuất CSV/JSON, đánh dấu phiên cần xem lại.

- `http://localhost:3000/admin/feedback`
	- Phản hồi người dùng: đánh giá chất lượng câu trả lời (thumbs up/down), 
		ghi chú góp ý, gắn nhãn chủ đề.
	- Chức năng: lọc theo mức độ hài lòng, tạo báo cáo cải thiện, liên kết tới 
		tài liệu/nguồn bị phản hồi tiêu cực để reprocess.

- `http://localhost:3000/admin/documents`
	- Quản lý tài liệu: upload, danh sách, lọc, chi tiết, reprocess, delete/restore.
	- Tích hợp Auto‑Ingestion: bật/tắt, hiển thị trạng thái watcher.
	- Liên quan: Embeddings/Indexing trạng thái, nút Rebuild BM25.

Gợi ý bổ sung routes:
- `http://localhost:3000/admin/embeddings` — thống kê vectors, reindex.
- `http://localhost:3000/admin/settings/retrieval` — tham số Top‑K/Top‑N, RRF.
- `http://localhost:3000/admin/health` — health checks.

### Danh mục chức năng đầy đủ (Feature Reference)

Dưới đây là danh mục tất cả chức năng của khu vực Admin Dashboard, kèm mô tả ngắn gọn và mục đích sử dụng. Bạn có thể dùng phần này như checklist triển khai và tài liệu bàn giao.

1) Upload tài liệu (Documents → Upload)
- Mô tả: chọn và tải lên tệp PDF để hệ thống xử lý.
- Luồng: upload → tạo bản ghi `documents` → queue xử lý nền.
- Ràng buộc: định dạng `.pdf`, kích thước tối đa theo `MAX_UPLOAD_SIZE`.

2) Danh sách tài liệu (Documents → List)
- Mô tả: liệt kê tất cả tài liệu cùng trạng thái, kích thước, số chunks.
- Tính năng: lọc theo trạng thái/keyword/thời gian, phân trang, sắp xếp.

3) Chi tiết tài liệu (Documents → Details)
- Mô tả: xem metadata, lịch sử xử lý, thống kê chunk size, danh sách chunks.
- Tính năng: mở trích đoạn, xem heading/page, tải metadata.

4) Tự động thu nhận (Auto‑Ingestion)
- Mô tả: bật/tắt watcher theo dõi thư mục `data/new_pdf/`.
- Tính năng: hiển thị trạng thái watcher, danh sách file mới phát hiện.

5) Xử lý lại tài liệu (Reprocess)
- Mô tả: xóa chunks/embeddings cũ, chạy lại pipeline với cấu hình chunking mới.
- Tùy chọn: đặt `CHUNK_SIZE/MIN/MAX/OVERLAP`, bật/tắt Gemini OCR.

6) Xóa/Khôi phục tài liệu (Delete/Restore)
- Mô tả: soft delete (ẩn khỏi truy xuất) hoặc hard delete (xóa khỏi DB).
- Cảnh báo: thao tác phá hủy cần confirm 2 bước; hard delete không thể khôi phục.

7) Hàng đợi xử lý (Processing Queue)
- Mô tả: giám sát jobs đang chạy, trạng thái, tiến độ, ETA.
- Tính năng: pause/resume/cancel/retry job; lọc theo trạng thái.

8) Quản lý embeddings (Embeddings)
- Mô tả: thống kê số lượng vectors, phát hiện missing embeddings.
- Tính năng: chạy repair cho chunks thiếu embedding; cấu hình `ivfflat lists`.

9) Thiết lập truy xuất (Retrieval Settings)
- Mô tả: điều chỉnh Top‑K, Top‑N, bật/tắt BM25, trọng số RRF.
- Tùy chọn: ngưỡng confidence tối thiểu, số nguồn hiển thị tối đa.

10) Xây dựng lại BM25 (Rebuild BM25)
- Mô tả: tái tạo chỉ mục BM25 sau khi cập nhật tài liệu/chunks.
- Ghi chú: thao tác nặng; hiển thị tiến trình và ảnh hưởng đến truy vấn.

11) Thống kê & Báo cáo (Analytics)
- Mô tả: xem số lượt truy vấn, thời gian phản hồi, chủ đề phổ biến.
- Chỉ số: Precision@5, tỷ lệ câu trả lời có trích dẫn hợp lệ, cache hit rate.

12) Lịch sử hội thoại (Chat History)
- Mô tả: xem danh sách phiên chat, nội dung hỏi/đáp, nguồn trích dẫn.
- Tính năng: tìm kiếm, lọc theo thời gian/chủ đề, xuất CSV/JSON.

13) Phản hồi người dùng (Feedback)
- Mô tả: thu thập đánh giá (up/down), ghi chú, nhãn chủ đề.
- Tính năng: lọc mức độ hài lòng, gợi ý cải thiện tài liệu/thiết lập retrieval.

14) Người dùng & Phân quyền (Users & Roles)
- Mô tả: quản lý tài khoản, vai trò (admin/editor/viewer), trạng thái khóa.
- Tính năng: audit logs cho thao tác nhạy cảm; chính sách mật khẩu.

15) Sức khỏe hệ thống (System Health)
- Mô tả: kiểm tra DB/Redis/Watcher/Queue; đánh dấu `healthy/degraded`.
- Tính năng: khởi động lại watcher, làm sạch queue, gửi cảnh báo.

16) Nhật ký hệ thống (Logs)
- Mô tả: xem log theo cấp độ, dịch vụ, khoảng thời gian.
- Tính năng: tải xuống log, xem chi tiết stack trace lỗi.

17) Cấu hình hệ thống (Config)
- Mô tả: chỉnh `USE_GEMINI_OCR`, `EMBEDDING_BATCH_SIZE`, `CHUNK_*`, LLM params.
- Tính năng: cấu hình theo môi trường, kiểm tra hợp lệ trước áp dụng.

18) Tích hợp (Integrations)
- Mô tả: webhooks khi tài liệu xử lý xong, export dữ liệu (chunks/embeddings).
- Tính năng: cấu hình endpoint, token bảo mật, lịch xuất định kỳ.

---

## 5.4. Quản lý tài liệu

### Auto-Ingestion
- Đặt file PDF vào thư mục `data/new_pdf/`
- Watchdog tự động phát hiện và xử lý
- File đã xử lý được chuyển sang `data/processed/`

### Trích xuất và Chunking
- Text Extraction: Gemini Vision → pdfplumber → PyPDF2 (fallback)
- HeadingChunker: tách theo tiêu đề, kích thước min/max/target, overlap

### Embeddings & Indexing
- Tạo embeddings (SBERT 384-d) theo batch (mặc định 32)
- Lưu vào `embeddings` (pgvector), tạo index `ivfflat`
- Rebuild BM25 index

---

## 5.5. Tra cứu và truy vấn RAG

### Pipeline RAG
1. Query Processing: chuẩn hóa, tạo embedding
2. Dense Retrieval: vector search (cosine similarity)
3. Sparse Retrieval: BM25
4. Fusion: RRF hợp nhất hai danh sách
5. Reranking: Cross-Encoder
6. Context Generation: định dạng nguồn
7. LLM Response: Gemini sinh câu trả lời, trích dẫn nguồn

### Tùy chọn
- Top-K retrieval (mặc định 20)
- Top-N reranking (mặc định 5)
- Temperature LLM (mặc định 0.2)

---

## 5.6. Thống kê và Phân tích

### Chỉ số hiển thị
- Tổng số tài liệu, tổng chunks, tổng embeddings
- Thời gian xử lý trung bình mỗi tài liệu
- Cache hit rate (Redis)
- Phân phối số lượt truy vấn theo chủ đề/thời gian

### Health Checks
- `/api/v1/health` — trạng thái DB, Redis, watcher, queue size

---

## 5.7. Tích hợp và Cấu hình

### Cấu hình chính (`config/settings.py`)
- `USE_GEMINI_OCR`: bật/tắt OCR
- `EMBEDDING_BATCH_SIZE`: kích thước batch
- `CHUNK_SIZE`, `MIN_CHUNK_SIZE`, `MAX_CHUNK_SIZE`, `CHUNK_OVERLAP`
- `IVFFLAT_LISTS`: số lists index (theo quy mô dữ liệu)

### Môi trường
- `.env`: `DATABASE_URL`, `REDIS_URL`, `GEMINI_API_KEY`, `ENVIRONMENT`, `LOG_LEVEL`

---

## 5.8. Luồng thao tác minh họa

### Luồng A: Người dùng hỏi đáp
1. Mở trang Chat
2. Nhập câu hỏi: "Điều kiện xét học bổng là gì?"
3. Nhận câu trả lời kèm nguồn: `QUY_CHE_DAO_TAO.pdf, trang 12`
4. Xem danh sách trích đoạn nguồn, bấm mở chi tiết (nếu có)

### Luồng B: Admin cập nhật tài liệu
1. Vào Admin Dashboard → Upload PDF
2. Theo dõi trạng thái `processing`
3. Sau khi `completed`, tài liệu khả dụng cho RAG
4. Nếu cần: Reprocess với thiết lập chunking mới

### Luồng C: Auto-Ingestion
1. Sao chép PDF vào `data/new_pdf/`
2. Hệ thống tự động xử lý → `data/processed/`
3. BM25 index được xây dựng lại

---

## 5.9. Hướng dẫn chạy nhanh (Try-it)

```powershell
# Tùy chọn 1: Chạy backend trực tiếp
cd "C:\TruongVanKhai\Project\uni_bot"
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Tùy chọn 2: Docker Compose (nếu dùng)
cd "C:\TruongVanKhai\Project\uni_bot"
docker-compose up -d

# Frontend
cd "C:\TruongVanKhai\Project\uni_bot\frontend"
pm install
npm run dev
```

Truy cập:
- Backend API: `http://localhost:8000/api/docs`
- Frontend: `http://localhost:3000`

---

## 5.10. Ghi chú kỹ thuật và hạn chế

- Gemini OCR có chi phí/quota; bật khi cần cho bản scan
- IVFFlat là index gần đúng (approximate); tăng `lists` để cải thiện recall
- Cross-Encoder reranking chậm với K lớn; nên giới hạn Top-K hợp lý
- Chunking theo heading tăng chất lượng, nhưng cần thống nhất format tài liệu
- Bảo mật: không lưu API keys trong code, sử dụng `.env`

---

**Tham chiếu liên quan:**
- Cơ sở lý thuyết: `docs/CHAPTER_3_THEORETICAL_FOUNDATION.md`
- Kiến trúc & luồng end-to-end: `docs/CHAPTER_4_6_SYSTEM_ARCHITECTURE_AND_WORKFLOWS.md`
- Quy trình xử lý document: `docs/DOCUMENT_PROCESSING_FLOW.md`

**Document Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: University Chatbot Development Team