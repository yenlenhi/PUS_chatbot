# Báo cáo tiến độ chatbot PSU

**Mốc chốt số liệu:** 13/04/2026  
**Khoảng vận hành chính:** 30 ngày gần nhất (31`/03/2026` đến `13/04/2026`)  
**Nguồn chính:** PostgreSQL production (`user_sessions`, `conversations`, `feedback`, `access_logs`)  
**Nguồn đối chiếu:** endpoint admin/public production trên Railway

## 1. Tóm tắt điều hành

-   Chatbot đang vận hành ổn định trên production, với **1.636 người dùng theo session web hoạt động** và **1.634 conversation duy nhất** trong 30 ngày gần nhất.
-   Trong cùng kỳ, hệ thống đã xử lý **4.061 tin nhắn**, tương đương trung bình **140,03 tin nhắn/ngày**.
-   Về phản hồi người dùng, chatbot ghi nhận **168 feedback trong 30 ngày**, trong đó **95 tích cực**, **7 tiêu cực**, **66 trung tính**. Tỷ lệ tích cực đạt **56,55%**.
-   Nội dung được hỏi nhiều nhất tập trung rõ vào chủ đề tuyển sinh: chỉ tiêu, phương thức tuyển sinh, hồ sơ sơ tuyển, điều kiện sơ tuyển và các mốc thời gian nhập học.

## 2. Số liệu chính

### 2.1. Tình trạng public hiện tại

-   **0** người online tại thời điểm kiểm tra.
-   **287** page views toàn thời gian.
-   **204** session truy cập được ghi nhận trong `access_logs`.

### 2.2. Vận hành 30 ngày gần nhất

-   **1.636** người dùng theo session web hoạt động.
-   **1.634** conversation duy nhất.
-   **4.061** tin nhắn.
-   Trung bình **56,4** người dùng/ngày.
-   Trung bình **140,03** tin nhắn/ngày.

### 2.3. Quy mô tích lũy toàn thời gian

-   **2.072** session web.
-   **2.130** conversation duy nhất.
-   **4.810** tin nhắn.
-   **4.780** tổng lượt ghé/lượt hỏi cộng dồn trong `user_sessions`.
-   **1.105** session quay lại (`total_visits > 1`).

## 3. Phản hồi người dùng

### 3.1. Thống kê phản hồi

-   **30 ngày gần nhất:** 168 feedback gồm 95 tích cực, 7 tiêu cực, 66 trung tính.
-   **Tỷ lệ 30 ngày:** tích cực **56,55%**, tiêu cực **4,17%**.
-   **Toàn thời gian:** 183 feedback gồm 109 tích cực, 8 tiêu cực, 66 trung tính.

### 3.2. Ví dụ phản hồi trích cho báo cáo

-   Phản hồi tích cực tiêu biểu: “Chatbot nhanh, trả lời ổn, 9 điểm”, “nice”, “Ok”.
-   Phản hồi tiêu cực tiêu biểu: “lan man”, “Chưa tốt”, “Chưa giải quyết được trọng tâm yêu cầu của câu hỏi”, “cần phát triển thêm data , nguồn data còn hạn chế , hỏi những câu hỏi liên quan tới trư...”.

### 3.3. Các phản hồi tiêu cực gần đây

-   `2026-04-06` | tôi ko đạo . Ba,bà nội hai em có đạo ông nội ko đạo mẹ ko đạo nhà ngoại ko đạo ông ngoại cựu chiến binh lý lịch được k? | phản hồi: “lan man”
-   `2026-04-03` | Tôi muốn biết hồ sơ cần chuẩn bị cho phương thức này | phản hồi: “Chưa tốt”
-   `2026-04-03` | Các yêu cầu của phương thức 1 | phản hồi: “Chưa giải quyết được trọng tâm yêu cầu của câu hỏi”
-   `2026-04-02` | tiền thân đại học an ninh nhân dân | phản hồi: “cần phát triển thêm data , nguồn data còn hạn chế , hỏi những câu hỏi liên quan tới trường còn chưa trả lời đc nhiều lắm , thay vì để trố...”
-   `2026-04-02` | sao toàn đưa mã trường không z mã ngành đâu bro | phản hồi: “khả năng retrieval dữ liệu chưa rõ khi hỏi giữa mã ngành và lẫn sang mã trường”

## 4. Nội dung người dùng quan tâm nhiều nhất trong 30 ngày

1.  Chỉ tiêu tuyển sinh vào Trường Đại học An Ninh Nhân Dân?: **454** lượt
2.  Các phương thức tuyển sinh?: **201** lượt
3.  Hồ sơ sơ tuyển cần chuẩn bị những gì?: **105** lượt
4.  Điều kiện sơ tuyển vào Trường Đại học An Ninh Nhân Dân là gì?: **92** lượt
5.  Tôi muốn biết mốc thời gian đăng ký và xác nhận nhập học: **70** lượt

## 5. Quy tắc trình bày và loại trừ

-   Báo cáo này **tách riêng** `người dùng theo session web` và `conversation duy nhất`, không gộp chung thành một chỉ số “người dùng”.
-   **Không dùng trong báo cáo chính** các metric sau từ dashboard analytics:
    -   `daily likes/dislikes` trong `analytics/chat`
    -   `avg_messages_per_conversation`
    -   `avg_conversation_duration_seconds`
    -   `funnel percentage`
    -   `return_frequency percentage`
    -   `topic percentage`
-   Lý do loại trừ:
    -   một phần metric đang hardcode hoặc suy diễn;
    -   một phần có logic tính tỷ lệ chưa chính xác nên dễ gây hiểu sai khi trình bày chính thức.

## 6. Kiểm tra chéo với production endpoint

Chỉ số

DB

Endpoint

Kết quả

Page views toàn thời gian

287

287

Khớp

Online hiện tại

0

0

Khớp

Conversation duy nhất toàn thời gian

2.130

2.130

Khớp

Tin nhắn toàn thời gian

4.810

4.810

Khớp

Feedback 30 ngày

168

168

Khớp

Feedback toàn thời gian

183

183

Khớp

## 7. Kết luận ngắn cho slide/báo cáo miệng

-   Trong 30 ngày gần nhất, chatbot PSU ghi nhận **1.636 người dùng theo session**, tạo ra **1.634 cuộc hội thoại** và **4.061 tin nhắn**.
-   Chất lượng phản hồi hiện ở mức khả quan với **56,55% feedback tích cực**, nhưng vẫn còn một số phản ánh tập trung vào việc trả lời lan man, chưa đúng trọng tâm hoặc dữ liệu còn thiếu.
-   Nhóm nhu cầu nổi bật nhất hiện nay là **tư vấn tuyển sinh**, đặc biệt về chỉ tiêu, phương thức, hồ sơ và mốc thời gian.

## 8. Ghi chú tái tạo báo cáo

-   Script sinh báo cáo: [scripts/generate_psu_progress_report.py](C:%5CTruongVanKhai%5CProject%5Cuni_bot%5Cscripts%5Cgenerate_psu_progress_report.py)
-   File này là snapshot đã chốt ngày **13/04/2026**.