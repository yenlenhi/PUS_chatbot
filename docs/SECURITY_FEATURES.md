# Các Tính Năng Bảo Mật Của Hệ Thống

Hệ thống University Chatbot được xây dựng với nguyên tắc "Security First", tích hợp đa lớp bảo mật từ tầng mạng, ứng dụng đến dữ liệu. Tài liệu này mô tả chi tiết các cơ chế bảo mật đang được áp dụng.

## 1. Xác Thực và Phân Quyền (Authentication & Authorization)

### 1.1 JWT Authentication
Hệ thống sử dụng **JSON Web Tokens (JWT)** để quản lý phiên làm việc của người dùng, đảm bảo tính stateless và khả năng mở rộng.
- **Tiêu chuẩn**: Sử dụng thuật toán `HS256`.
- **Flow**: Người dùng đăng nhập -> Nhận Access Token -> Token được gửi trong header `Authorization: Bearer <token>` của mỗi request.
- **Thời hạn**: Token có thời hạn ngắn (mặc định 30 phút), yêu cầu đăng nhập lại khi hết hạn để giảm thiểu rủi ro khi token bị lộ.

### 1.2 Password Security
Mật khẩu người dùng KHÔNG BAO GIỜ được lưu dưới dạng văn bản thuần (plain text).
- **Hashing**: Sử dụng **Bcrypt** với cost factor 12 (rounds=12).
- **Salt**: Mỗi mật khẩu được tự động tạo salt riêng biệt, chống lại các cuộc tấn công Rainbow Table.

### 1.3 Phân Quyền (RBAC)
Hệ thống hỗ trợ phân quyền dựa trên scopes (phạm vi truy cập).
- **User Scope**: Người dùng thông thường, có quyền chat và xem lịch sử.
- **Admin Scope**: Quản trị viên, có quyền quản lý tài liệu, người dùng và xem thống kê hệ thống.
- Middleware `get_current_user` tự động kiểm tra quyền truy cập trước khi xử lý request.

## 2. Bảo Mật Mạng (Network Security)

### 2.1 HTTPS Enforcement
- **Mã hóa**: Tất cả dữ liệu truyền tải đều được mã hóa qua TLS 1.2+.
- **Redirect**: Middleware `HTTPSRedirectMiddleware` tự động chuyển hướng mọi truy cập HTTP sang HTTPS.

### 2.2 Security Headers
Middleware `SecurityHeadersMiddleware` tự động thêm các HTTP headers bảo mật vào mọi phản hồi:
- `Strict-Transport-Security` (HSTS): Buộc trình duyệt chỉ kết nối qua HTTPS trong tương lai.
- `X-Content-Type-Options: nosniff`: Ngăn trình duyệt đoán sai lại MIME type (MIME sniffing).
- `X-Frame-Options: DENY`: Chống tấn công Clickjacking bằng cách cấm nhúng trang web vào iframe.
- `Content-Security-Policy` (CSP): Kiểm soát các nguồn tài nguyên hợp lệ, giảm thiểu nguy cơ XSS.

### 2.3 CORS (Cross-Origin Resource Sharing)
Chính sách CORS được cấu hình chặt chẽ thông qua biến môi trường `ALLOWED_ORIGINS`.
- **Production**: Chỉ cho phép các domain tin cậy (ví dụ: frontend domain) gọi API.
- **Development**: Có thể cấu hình mở rộng để thuận tiện cho việc phát triển.

## 3. Toàn Vẹn Dữ Liệu (Data Integrity)

### Checksum Verification
Để đảm bảo file tải lên không bị thay đổi hoặc lỗi trong quá trình truyền tải, hệ thống tích hợp `ChecksumMiddleware`.
- **Cơ chế**: Client tính toán checksum (SHA256 hoặc MD5) của file và gửi kèm header `X-Checksum`.
- **Xác thực**: Server tính toán lại checksum của dữ liệu nhận được và so sánh. Nếu không khớp, request bị từ chối ngay lập tức.
- **Áp dụng**: Bắt buộc đối với các endpoint upload tài liệu quan trọng (`/api/admin/upload`).

## 4. Cơ Chế Bảo Vệ (Protection Patterns)

### 4.1 Rate Limiting (Chống DDoS/Brute Force)
Hệ thống sử dụng `RateLimitMiddleware` kết hợp với **Redis** (hoặc in-memory fallback) để giới hạn số lượng request.
- **Chiến lược**: Sliding window hoặc Fixed window.
- **Giới hạn cụ thể** (Cấu hình mặc định):
  - Đăng nhập: `5 requests/phút` (Chống đoán mật khẩu).
  - Đăng ký: `3 requests/phút` (Chống spam user rác).
  - Chat API: `60 requests/phút`.
  - Admin API: `30 requests/phút`.
  - Mặc định: `120 requests/phút`.
- **Xử lý**: Trả về mã lỗi `429 Too Many Requests` kèm thời gian `Retry-After`.

### 4.2 Input Validation
- Sử dụng **Pydantic** để định nghĩa schemas (kiểu dữ liệu) cho mọi request body và query parameters.
- Dữ liệu không đúng định dạng (sai kiểu, thiếu trường bắt buộc, giá trị không hợp lệ) sẽ bị từ chối tự động với mã lỗi `422 Unprocessable Entity` trước khi đi vào logic xử lý.

## 5. Deployment Security

- **Environment Variables**: Tất cả thông tin nhạy cảm (DB URL, API Keys, Secret Keys) đều được đọc từ biến môi trường, không hard-code trong mã nguồn.
- **Health Checks**: Endpoint `/health` cung cấp trạng thái hệ thống mà không lộ thông tin nhạy cảm.
- **Docker Security**: Container được cấu hình tối giản, chạy với user không có quyền root (khi cấu hình production nâng cao).

---
*Tài liệu này được cập nhật lần cuối theo phiên bản mã nguồn hiện tại.*
