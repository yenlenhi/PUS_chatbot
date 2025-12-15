# CHƯƠNG 2: TỔNG QUAN VỀ ĐƠN VỊ VÀ YÊU CẦU HỆ THỐNG

## MỤC LỤC

1. [Giới thiệu về đơn vị](#21-giới-thiệu-về-đơn-vị)
2. [Bối cảnh và bài toán thực tế](#22-bối-cảnh-và-bài-toán-thực-tế)
3. [Mục tiêu dự án](#23-mục-tiêu-dự-án)
4. [Phạm vi và đối tượng phục vụ](#24-phạm-vi-và-đối-tượng-phục-vụ)
5. [Yêu cầu chức năng](#25-yêu-cầu-chức-năng)
6. [Yêu cầu phi chức năng](#26-yêu-cầu-phi-chức-năng)
7. [Các bên liên quan (Stakeholders)](#27-các-bên-liên-quan-stakeholders)
8. [Luồng sử dụng điển hình](#28-luồng-sử-dụng-điển-hình)
9. [Tiêu chí đánh giá thành công](#29-tiêu-chí-đánh-giá-thành-công)
10. [Rủi ro và phương án giảm thiểu](#210-rủi-ro-và-phương-án-giảm-thiểu)

---

## 2.1. Giới thiệu về đơn vị

- Đơn vị: Trường Đại học (khoa/viện/ban) triển khai chatbot hỗ trợ thông tin.
- Lĩnh vực: Quản lý đào tạo, tuyển sinh, học bổng, dịch vụ sinh viên.
- Thách thức hiện tại:
  - Khối lượng câu hỏi lớn, lặp lại theo mùa (tuyển sinh, đăng ký lớp, xét học bổng).
  - Tài liệu nhiều, phân tán, thay đổi theo thời gian (quy chế, thông báo, biểu mẫu).
  - Nhân sự hỗ trợ bị quá tải, khó đáp ứng 24/7.

## 2.2. Bối cảnh và bài toán thực tế

- Người dùng (thí sinh/sinh viên/phụ huynh) cần truy cập nhanh thông tin chính xác.
- Câu hỏi có tính đa dạng, nhiều cách diễn đạt, tiếng Việt không chuẩn hóa.
- Tài liệu nguồn là PDF/Word/Thông báo web; có bản scan, có layout phức tạp.
- Hệ thống cần cung cấp câu trả lời đáng tin cậy kèm trích dẫn nguồn.

## 2.3. Mục tiêu dự án

- Xây dựng hệ thống chatbot RAG trả lời chính xác dựa trên tài liệu của trường.
- Hỗ trợ tra cứu 24/7, giảm tải cho bộ phận tư vấn.
- Cập nhật động khi có tài liệu mới, hạn chế "bịa đặt" (hallucination).
- Tích hợp giao diện thân thiện (web dashboard + chat UI).

## 2.4. Phạm vi và đối tượng phục vụ

- Đối tượng:
  - Thí sinh: thông tin tuyển sinh, phương thức xét tuyển.
  - Sinh viên: quy chế đào tạo, đăng ký tín chỉ, học bổng, học phí.
  - Phụ huynh: quy định học phí, hỗ trợ sinh viên.
  - Cán bộ quản lý: cập nhật tài liệu, thống kê truy vấn.
- Phạm vi dữ liệu:
  - PDF quy chế, thông báo, biểu mẫu, cẩm nang.
  - Link trang web thông tin chính thức (nếu mở rộng).
  - Chỉ dữ liệu nội bộ chính thống, loại trừ nguồn không kiểm chứng.

## 2.5. Yêu cầu chức năng

- Chatbot trả lời câu hỏi tiếng Việt, có trích dẫn nguồn (file, trang).
- Quản lý tài liệu:
  - Upload PDF qua dashboard
  - Auto-ingestion qua thư mục theo dõi `data/new_pdf/`
  - Xem trạng thái xử lý (pending/processing/completed/failed)
  - Reprocess với chiến lược chunking mới
  - Xóa/khôi phục tài liệu (soft/hard delete)
- Tìm kiếm:
  - Hybrid retrieval (Vector + BM25)
  - Reranking bằng Cross-Encoder
  - Lọc theo loại tài liệu, thời gian
- Thống kê/Phân tích:
  - Số lượt truy vấn, chủ đề phổ biến
  - Hiệu năng xử lý, thời gian phản hồi
  - Tỉ lệ câu trả lời có trích dẫn
- Quản trị:
  - Quản lý người dùng (role-based)
  - Cấu hình tham số (batch size, index lists, Gemini OCR)

## 2.6. Yêu cầu phi chức năng

- Hiệu năng:
  - Thời gian phản hồi chat: < 2 giây với dữ liệu vừa phải
  - Tốc độ xử lý PDF: 30 giây–5 phút tùy độ lớn
- Độ chính xác:
  - Precision@5 ≥ 0.8 (top 5 đoạn liên quan)
  - Giảm hallucination (bắt buộc trích dẫn nguồn)
- Khả năng mở rộng:
  - Lưu trữ 10k–100k chunks, index hiệu quả
  - Tăng/giảm `ivfflat lists` theo quy mô
- Bảo mật:
  - Phân quyền, kiểm soát truy cập admin
  - Bảo vệ API key (Gemini)
  - Sao lưu database định kỳ
- Tính sẵn sàng:
  - Hoạt động 24/7, khả năng khôi phục nhanh
  - Health checks cho DB/Redis/Watcher

## 2.7. Các bên liên quan (Stakeholders)

- Ban giám hiệu/Ban đào tạo: định hướng, phê duyệt dữ liệu.
- Bộ phận tuyển sinh/Công tác sinh viên: cung cấp tài liệu, phản hồi chất lượng.
- Bộ phận CNTT: vận hành hệ thống, bảo mật, hạ tầng.
- Người dùng cuối: thí sinh, sinh viên, phụ huynh.

## 2.8. Luồng sử dụng điển hình

- Luồng 1: Tra cứu nhanh
  1. Người dùng mở Chat UI, nhập câu hỏi
  2. Hệ thống thực hiện Hybrid Retrieval + Reranking
  3. LLM sinh câu trả lời, kèm trích dẫn nguồn
  4. Người dùng xem nguồn tham chiếu

- Luồng 2: Cập nhật tài liệu
  1. Admin upload PDF hoặc sao chép vào thư mục theo dõi
  2. Hệ thống tự động trích xuất text → chunking → embeddings → lưu DB
  3. Xây dựng lại BM25 index
  4. Tài liệu sẵn sàng cho truy xuất

## 2.9. Tiêu chí đánh giá thành công

- Chất lượng câu trả lời:
  - Tỉ lệ câu trả lời đúng với trích dẫn hợp lệ ≥ 85%
  - Giảm yêu cầu hỗ trợ trực tiếp ≥ 50%
- Trải nghiệm người dùng:
  - Thời gian phản hồi trung bình < 2 giây
  - Giao diện dễ dùng, rõ ràng
- Vận hành:
  - Tự động ingest tài liệu mới trong < 5 phút
  - Tỉ lệ lỗi xử lý tài liệu < 5%

## 2.10. Rủi ro và phương án giảm thiểu

- Rủi ro dữ liệu:
  - Tài liệu lỗi/scan kém → dùng Gemini OCR, kiểm tra chất lượng text
  - Tài liệu thay đổi → cơ chế reprocess và versioning
- Rủi ro hạ tầng:
  - DB quá tải → tối ưu index, phân bổ tài nguyên
  - Quota API (Gemini) → fallback pdfplumber/PyPDF2, giám sát quota
- Rủi ro bảo mật:
  - Lộ API key → lưu trong `.env`, hạn chế quyền truy cập
  - Phân quyền sai → RBAC, audit logs

---

**Tham chiếu liên quan:**
- Kiến trúc & luồng end-to-end: `docs/CHAPTER_4_6_SYSTEM_ARCHITECTURE_AND_WORKFLOWS.md`
- Cơ sở lý thuyết: `docs/CHAPTER_3_THEORETICAL_FOUNDATION.md`
- Quy trình xử lý document: `docs/DOCUMENT_PROCESSING_FLOW.md`

**Document Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: University Chatbot Development Team