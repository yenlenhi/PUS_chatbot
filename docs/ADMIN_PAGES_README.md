# README: MÔ TẢ TRANG ADMIN

Tài liệu này mô tả chi tiết từng trang quản trị theo ba mục: 
5.3.1 Mục tiêu chức năng, 5.3.2 Bố cục giao diện và thành phần, 5.3.3 Luồng thao tác.

Các trang:
- /admin/dashboard
- /admin/chat-history
- /admin/feedback
- /admin/documents

---

## Trang: /admin/dashboard

### 5.3.1. Mục tiêu chức năng
- Cung cấp cái nhìn tổng quan về hệ thống: số liệu tài liệu, chunks, embeddings, truy vấn gần đây.
- Hiển thị sức khỏe hệ thống (DB/Redis/Watcher/Queue) và cảnh báo khi suy giảm (degraded).
- Tóm tắt xu hướng: tài liệu mới xử lý, top tài liệu được trích dẫn, thời gian phản hồi trung bình.

### 5.3.2. Bố cục giao diện và thành phần
- Header: tiêu đề “Admin Dashboard”, nút làm mới (refresh).
- Khu Widgets (cards):
  - Documents Summary: tổng số tài liệu, tài liệu mới trong 24h.
  - Chunks & Embeddings: tổng số chunks/embeddings, phân phối kích thước chunk.
  - Queries Overview: số lượt truy vấn/ngày, thời gian phản hồi trung bình.
  - Health Status: DB/Redis/Watcher/Queue (badge OK/Warning/Error).
- Charts:
  - Line chart: truy vấn theo thời gian.
  - Bar chart: top tài liệu được tham chiếu.
- Actions nhanh: Rebuild BM25, Restart Watcher, Xem chi tiết Health.

### 5.3.3. Luồng thao tác
1) Admin mở Dashboard.
2) Hệ thống tải dữ liệu thống kê và sức khỏe; hiển thị widgets.
3) Admin kiểm tra cảnh báo; nếu cần, thực hiện “Restart Watcher” hoặc “Rebuild BM25”.
4) Admin xem xu hướng, bấm vào card để chuyển tới trang chi tiết (Documents/Analytics/Health).

---

## Trang: /admin/chat-history

### 5.3.1. Mục tiêu chức năng
- Hiển thị lịch sử phiên chat để giám sát chất lượng câu trả lời và nguồn trích dẫn.
- Hỗ trợ tìm kiếm/lọc theo thời gian, từ khóa, chủ đề; xuất dữ liệu phục vụ báo cáo.

### 5.3.2. Bố cục giao diện và thành phần
- Header: tiêu đề “Chat History”, bộ lọc thời gian (date range), ô tìm kiếm từ khóa.
- Bảng danh sách phiên chat:
  - Cột đề xuất: Conversation ID, Thời gian, Câu hỏi (rút gọn), Trả lời (rút gọn), Số nguồn trích dẫn, Độ tin cậy, Hành động (Xem).
- Modal/Drawer Chi tiết phiên:
  - Hiển thị đầy đủ câu hỏi, câu trả lời, danh sách nguồn trích dẫn (file, trang, trích đoạn).
  - Nút “Xuất CSV/JSON”, “Đánh dấu cần xem lại”.

### 5.3.3. Luồng thao tác
1) Admin vào Chat History, chọn khoảng thời gian và/hoặc nhập từ khóa.
2) Hệ thống lọc danh sách phiên; admin chọn một phiên để xem chi tiết.
3) Trong chi tiết, admin kiểm tra nguồn trích dẫn, độ tin cậy, nội dung trả lời.
4) Admin có thể xuất dữ liệu, hoặc đánh dấu phiên cần xem lại/cải thiện.

---

## Trang: /admin/feedback

### 5.3.1. Mục tiêu chức năng
- Thu thập và quản lý phản hồi người dùng về chất lượng câu trả lời.
- Phân tích mức độ hài lòng (thumbs up/down), góp ý, nhãn chủ đề để cải thiện hệ thống.

### 5.3.2. Bố cục giao diện và thành phần
- Header: “User Feedback”, bộ lọc mức độ hài lòng (All/Up/Down), thời gian.
- Bảng Feedback:
  - Cột đề xuất: Conversation ID, Thời gian, Mức độ (Up/Down), Góp ý, Chủ đề, Hành động (Xem).
- Chi tiết Feedback:
  - Hiển thị câu hỏi, câu trả lời liên quan, các nguồn trích dẫn, ghi chú của người dùng.
  - Nút “Liên kết tới tài liệu/nguồn”: mở nhanh trang Documents/Chunk chi tiết để reprocess.

### 5.3.3. Luồng thao tác
1) Admin mở Feedback và thiết lập bộ lọc (ví dụ: Down trong 7 ngày gần đây).
2) Xem danh sách phản hồi tiêu cực, mở chi tiết để kiểm tra nguyên nhân.
3) Nếu cần, điều hướng tới Documents/Settings để reprocess hoặc điều chỉnh tham số retrieval.
4) Ghi nhận cải thiện vào báo cáo (export CSV/JSON cho QA/đào tạo).

---

## Trang: /admin/documents

### 5.3.1. Mục tiêu chức năng
- Quản lý vòng đời tài liệu: upload → xử lý → sẵn sàng tra cứu → cập nhật/xóa.
- Theo dõi trạng thái xử lý, thống kê chunks, thao tác reprocess, delete/restore.
- Tích hợp Auto‑Ingestion và quản lý index (BM25/pgvector).

### 5.3.2. Bố cục giao diện và thành phần
- Thanh hành động: Upload, công tắc Auto‑Ingestion, Rebuild BM25.
- Bộ lọc: trạng thái (pending/processing/completed/failed), từ khóa, thời gian; phân trang.
- Bảng tài liệu:
  - Cột đề xuất: Filename, Status, Chunks, File Size, Updated At, Actions (Details/Reprocess/Delete/Restore).
- Chi tiết tài liệu:
  - Metadata: tên file, đường dẫn, kích thước, hash, thời gian tạo/cập nhật.
  - Lịch sử xử lý: thời điểm bắt đầu/kết thúc, lỗi (nếu có), cấu hình chunking.
  - Chunks: danh sách có heading/page/word_count/char_count; mở trích đoạn đầy đủ.

### 5.3.3. Luồng thao tác
1) Admin chọn Upload và tải lên tệp PDF.
2) Hệ thống tạo bản ghi `documents` (status=pending) và chuyển sang `processing` khi pipeline chạy.
3) Sau khi hoàn tất, status=completed; hiển thị tổng `chunks`, thời gian xử lý.
4) Admin có thể:
   - Bật Auto‑Ingestion để hệ thống tự phát hiện file mới trong `data/new_pdf/`.
   - Thực hiện Reprocess với thiết lập chunking/embedding mới.
   - Delete (soft) để ẩn khỏi truy xuất hoặc Delete (hard) để xóa khỏi DB; Restore để kích hoạt lại.
5) Khi dữ liệu thay đổi, admin chạy Rebuild BM25 để đảm bảo tìm kiếm sparse cập nhật; pgvector index (ivfflat) dùng cho dense retrieval đã sẵn.

---

**Ghi chú:**
- Các trang đều cần phân quyền (RBAC): admin toàn quyền, editor giới hạn thao tác, viewer chỉ xem.
- Tất cả thao tác phá hủy (hard delete/reindex) nên có dialog xác nhận 2 bước.
- Khuyến khích bổ sung telemetry tối thiểu để theo dõi lỗi và hành vi người dùng quản trị.

**Document Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: University Chatbot Development Team
