# Báo cáo tiến độ chatbot PSU

**Mốc chốt số liệu:** 07/04/2026  
**Khoảng vận hành chính:** 7 ngày gần nhất (31`/03/2026` đến `07/04/2026`)  
**Nguồn chính:** PostgreSQL production (`user_sessions`, `conversations`, `feedback`, `access_logs`)  
**Nguồn đối chiếu:** endpoint admin/public production trên Railway

## 1. Tóm tắt điều hành

-   Chatbot đang vận hành ổn định trên production, với **1.412 người dùng theo session web hoạt động** và **1.410 conversation duy nhất** trong 30 ngày gần nhất.
-   Trong cùng kỳ, hệ thống đã xử lý **3.502 tin nhắn**, tương đương trung bình **125,07 tin nhắn/ngày**.
-   Về phản hồi người dùng, chatbot ghi nhận **115 feedback trong 30 ngày**, trong đó **68 tích cực**, **6 tiêu cực**, **41 trung tính**. Tỷ lệ tích cực đạt **59,13%**.
-   Nội dung được hỏi nhiều nhất tập trung rõ vào chủ đề tuyển sinh: chỉ tiêu, phương thức tuyển sinh, hồ sơ sơ tuyển, điều kiện sơ tuyển và các mốc thời gian nhập học.

## 2. Số liệu chính

### 2.1. Tình trạng public hiện tại

-   **0** người online tại thời điểm kiểm tra.
-   **284** page views toàn thời gian.
-   **202** session truy cập được ghi nhận trong `access_logs`.

### 2.2. Vận hành 30 ngày gần nhất

-   **1.412** người dùng theo session web hoạt động.
-   **1.410** conversation duy nhất.
-   **3.502** tin nhắn.
-   Trung bình **52,3** người dùng/ngày.
-   Trung bình **125,07** tin nhắn/ngày.

### 2.3. Quy mô tích lũy toàn thời gian

-   **1.839** session web.
-   **1.897** conversation duy nhất.
-   **4.222** tin nhắn.
-   **4.192** tổng lượt ghé/lượt hỏi cộng dồn trong `user_sessions`.
-   **968** session quay lại (`total_visits > 1`).

## 3. Phản hồi người dùng

### 3.1. Thống kê phản hồi

-   **30 ngày gần nhất:** 115 feedback gồm 68 tích cực, 6 tiêu cực, 41 trung tính.
-   **Tỷ lệ 30 ngày:** tích cực **59,13%**, tiêu cực **5,22%**.
-   **Toàn thời gian:** 130 feedback gồm 82 tích cực, 7 tiêu cực, 41 trung tính.

### 3.2. Ví dụ phản hồi trích cho báo cáo

-   Phản hồi tích cực tiêu biểu: “Chatbot nhanh, trả lời ổn, 9 điểm”, “nice”, “Ok”.
-   Phản hồi tiêu cực tiêu biểu: “lan man”, “Chưa tốt”, “Chưa giải quyết được trọng tâm yêu cầu của câu hỏi”, “Dữ liệu còn hạn chế, nhiều câu hỏi liên quan trực tiếp tới trường vẫn chưa được trả lời...”.

### 3.3. Các phản hồi tiêu cực gần đây

-   `2026-04-06` | tôi ko đạo . Ba,bà nội hai em có đạo ông nội ko đạo mẹ ko đạo nhà ngoại ko đạo ông ngoại cựu chiến binh lý lịch được k? | phản hồi: “lan man”
-   `2026-04-03` | Tôi muốn biết hồ sơ cần chuẩn bị cho phương thức này | phản hồi: “Chưa tốt”
-   `2026-04-03` | Các yêu cầu của phương thức 1 | phản hồi: “Chưa giải quyết được trọng tâm yêu cầu của câu hỏi”
-   `2026-04-02` | tiền thân đại học an ninh nhân dân | phản hồi: “Dữ liệu còn hạn chế, nhiều câu hỏi liên quan trực tiếp tới trường vẫn chưa được trả lời đủ cụ thể”

## 4. Nội dung người dùng quan tâm nhiều nhất trong 7 ngày

1.  Chỉ tiêu tuyển sinh vào Trường Đại học An Ninh Nhân Dân?: **400** lượt
2.  Các phương thức tuyển sinh?: **171** lượt
3.  Hồ sơ sơ tuyển cần chuẩn bị những gì?: **98** lượt
4.  Điều kiện sơ tuyển vào Trường Đại học An Ninh Nhân Dân là gì?: **79** lượt
5.  Tôi muốn biết mốc thời gian đăng ký và xác nhận nhập học: **64** lượt

## 5. Kết luận ngắn cho slide/báo cáo miệng

-   Trong 30 ngày gần nhất, chatbot PSU ghi nhận **1.412 người dùng theo session**, tạo ra **1.410 cuộc hội thoại** và **3.502 tin nhắn**.
-   Chất lượng phản hồi hiện ở mức khả quan với **59,13% feedback tích cực**, nhưng vẫn còn một số phản ánh tập trung vào việc trả lời lan man, chưa đúng trọng tâm hoặc dữ liệu còn thiếu.
-   Nhóm nhu cầu nổi bật nhất hiện nay là **tư vấn tuyển sinh**, đặc biệt về chỉ tiêu, phương thức, hồ sơ và mốc thời gian.

## 6. Ghi chú tái tạo báo cáo

-   File này là snapshot đã chốt ngày **07/04/2026**.