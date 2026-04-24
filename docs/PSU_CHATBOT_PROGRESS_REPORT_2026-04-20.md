# Báo cáo tiến độ chatbot PSU

**Mốc chốt số liệu:** 20/04/2026  
**Khoảng vận hành chính:** 30 ngày gần nhất (22/03/2026 đến 20/04/2026)  
**Nguồn chính:** Admin API production (`/api/v1/feedback/*`, `/api/v1/admin/chat-history/*`, `/api/v1/analytics/*`)  
**Nguồn đối chiếu:** Endpoint export feedback (`/api/v1/feedback/export?days=30`)

## 1. Tóm tắt điều hành

- Chatbot ghi nhận **246 feedback trong 30 ngày**, với **58,94% tích cực**.
- Tổng cộng toàn thời gian hiện có **261 feedback**, trong đó **159 tích cực** và **13 tiêu cực**.
- Hệ thống conversation hiện có **2.448 conversation** và **5.590 tin nhắn** toàn thời gian.
- Lưu lượng web hiện tại: **1 online**, **288 page views** toàn thời gian.

## 2. Số liệu chính

### 2.1. Tình trạng public hiện tại

- **1** người online tại thời điểm kiểm tra.
- **288** page views toàn thời gian.
- **10** lượt xem trong tháng hiện tại.

### 2.2. Vận hành hội thoại

- **2.448** conversation toàn thời gian.
- **5.590** tin nhắn toàn thời gian.
- **3** conversation phát sinh hôm nay.
- **1** conversation đang active.

## 3. Phản hồi người dùng

### 3.1. Thống kê phản hồi

- **30 ngày gần nhất:** 246 feedback gồm 145 tích cực, 12 tiêu cực, 89 trung tính.
- **Tỷ lệ 30 ngày:** tích cực **58,94%**, tiêu cực **4,88%**.
- **Toàn thời gian:** 261 feedback gồm 159 tích cực, 13 tiêu cực, 89 trung tính.

### 3.2. Nhịp feedback theo ngày

- Số ngày có dữ liệu feedback trong kỳ: **21** ngày.
- Trung bình feedback/ngày trong kỳ: **11,71**.

### 3.3. Các phản hồi tiêu cực gần đây

- `2026-04-19` | Tôi muốn biết điều kiện áp dụng của từng phương thức xét tuyển | phản hồi: "Không xem được file pdf trong phần tài liệu tham khảo"
- `2026-04-16` | Phương thức 2 cần những chứng chỉ ngoại ngữ nào? | phản hồi: "không xem được file"
- `2026-04-14` | Tôi học ngành thú y, có được nộp hồ sơ tuyển sinh văn bằng 2 vào T02 không? | phản hồi: "abc"
- `2026-04-14` | Điều kiện thi văn bằng 2 | phản hồi: "."
- `2026-04-14` | Điều kiện sơ tuyển vào Trường Đại học An Ninh Nhân Dân là gì? | phản hồi: "Cần cải thiện"

## 4. Kiểm tra chéo với endpoint export feedback

- Tổng feedback kỳ báo cáo (`feedback/stats`) và (`feedback/export`) đều là **246**.
- Tỷ lệ tích cực kỳ báo cáo từ endpoint thống kê là **58,94%**.
- Chỉ số chất lượng trung bình phản hồi (`avg_response_quality`) là **0,77**.

## 5. Khuyến nghị tự động từ hệ thống

- 💡 Low feedback rate. Consider adding more prominent feedback prompts.
- 📝 Consider reviewing/improving chunks: [6586, 6567, 6594]
- 🎯 Sufficient data for fine-tuning. Consider training custom embeddings.

## 6. Ghi chú tái tạo báo cáo

- Script export: [scripts/export_admin_feedback_report.py](scripts/export_admin_feedback_report.py)
- Đây là snapshot được export tự động ngày **20/04/2026** từ trang admin feedback/API production.
