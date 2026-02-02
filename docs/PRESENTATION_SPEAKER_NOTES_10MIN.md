# CHÚ THÍCH THUYẾT TRÌNH 10 PHÚT (Slide 1-15)
## PSU CHATBOT - Hệ thống Chatbot Tư vấn Tuyển sinh

**Thời lượng:** 10 phút cho phần lý thuyết (Slide 1-15), sau đó demo hệ thống.

**Chiến lược phân bổ thời gian:**
- Phần 1 (Slide 1-7): Giới thiệu & Vấn đề (4 phút)
- Phần 2 (Slide 8-10): Cơ sở lý thuyết & Kiến trúc (3 phút)
- Phần 3 (Slide 11-15): Thiết kế chi tiết (3 phút)

---

## SLIDE 1: Trang bìa (20 giây)

**Chú thích:**
- "Kính chào Quý Thầy Cô và Ban Giám khảo!"
- "Em là [Tên], cùng nhóm VB2 D5 xin trình bày đề tài **PSU Chatbot** - ứng dụng RAG hỗ trợ tư vấn tuyển sinh cho Trường Đại học An ninh Nhân dân."
- "Thời gian 10 phút lý thuyết, sau đó em sẽ demo hệ thống thực tế."

---

## SLIDE 2: Nội dung chính (15 giây)

**Chú thích:**
- "Bài báo cáo gồm 3 phần:"
  1. Vấn đề thực tế
  2. Cơ sở lý thuyết & Kiến trúc
  3. Chương trình minh họa (demo)

---

## SLIDE 3: Vấn đề thực tế - Overview (10 giây)

**Chú thích:**
- "Phần 1 gồm: Bối cảnh, Hệ quả, Mục tiêu và Giải pháp."

---

## SLIDE 4: Bối cảnh (35 giây)

**Chú thích:**
- **Bối cảnh chung:** "Chuyển đổi số trong giáo dục đang diễn ra mạnh mẽ, nhu cầu tra cứu nhanh và chính xác ngày càng cao."
- **Tại trường:** "Hỗ trợ học vụ chủ yếu thủ công qua điện thoại, email. Nhu cầu hỏi đáp về tuyển sinh rất lớn từ học viên."
- **Hệ quả:** "Cán bộ quá tải, phản hồi chậm, học viên khó tiếp cận thông tin."

---

## SLIDE 5: Hệ quả (SKIP - Đã nói ở Slide 4)

**Chú thích:**
- *Bỏ qua slide này để tiết kiệm thời gian, đã tích hợp vào Slide 4.*

---

## SLIDE 6: Mục tiêu đề tài (50 giây)

**Chú thích:**
- **Mục tiêu chung:** "Xây dựng chatbot AI hỗ trợ đào tạo và tư vấn người học."

- **5 mục tiêu cụ thể (nói nhanh, chọn 3 quan trọng nhất):**
  1. "Số hóa kho tài liệu: quy chế, biểu mẫu, hướng dẫn từ nguồn chính thống."
  2. "Quản trị dữ liệu thông minh: tự động hóa upload, mọi câu trả lời kèm trích dẫn nguồn minh bạch."
  3. "Xây dựng Web tích hợp: Giao diện Chat cho user, Dashboard cho Admin giám sát và thống kê."

- *Bỏ qua mục tiêu 4, 5 để giữ thời gian.*

---

## SLIDE 7: Giải pháp (40 giây)

**Chú thích:**
- "PSU Chatbot - Hệ thống hỗ trợ tra cứu thông minh với 5 điểm nổi bật:"
  1. "Hoạt động 24/7, trả lời tức thì."
  2. "Dựa trên tài liệu chính thống, không bịa đặt."
  3. "Hiển thị nguồn trích dẫn để kiểm chứng."
  4. "Tự động gợi ý biểu mẫu phù hợp."
  5. "Giảm tải 40-50% câu hỏi thường gặp cho cán bộ."

- **Transition:** "Để thực hiện được điều này, hệ thống áp dụng các công nghệ AI tiên tiến."

---

## SLIDE 8: Cơ sở lý thuyết (20 giây)

**Chú thích:**
- "5 công nghệ chính:"
  1. RAG
  2. Vector Embeddings & Semantic Search
  3. BM25 & Hybrid Search
  4. Cross-Encoder Reranking
  5. LLM (Google Gemini 2.0)

---

## SLIDE 9: Bảng công nghệ (1 phút)

**Chú thích:**
- "Bảng tóm tắt công nghệ. Em xin phép trình bày 3 công nghệ quan trọng nhất:"

**1. RAG:**
- "Kỹ thuật kết hợp tìm kiếm tài liệu với AI sinh văn bản."
- "Tìm thông tin → AI soạn câu trả lời chính xác, không bịa đặt."

**2. Hybrid Search (RRF):**
- "Kết hợp Vector Search (tìm theo ý nghĩa) + BM25 (tìm theo từ khóa)."
- "Đảm bảo tìm đúng cả ngữ nghĩa lẫn từ chính xác (mã SV, số văn bản)."

**3. LLM (Gemini 2.0 Flash):**
- "Mô hình ngôn ngữ lớn của Google, đọc ngữ cảnh và soạn câu trả lời tự nhiên."

---

## SLIDE 10: Kiến trúc tổng thể (15 giây)

**Chú thích:**
- "Phần 2: Kiến trúc hệ thống gồm 4 nội dung chính."
- "Em sẽ tập trung vào Kiến trúc 4 tầng và Quy trình RAG."

---

## SLIDE 11: Kiến trúc 4 tầng (1 phút)

**Chú thích:**
- "Hệ thống áp dụng **kiến trúc 4 tầng:** Frontend - Backend - Database - AI/ML."

- **3 Lợi ích chính:**
  1. "**Module hóa:** Đổi LLM không ảnh hưởng giao diện, dễ nâng cấp."
  2. "**Hiệu năng cao:** Phân tải tốt, xử lý hàng nghìn truy vấn đồng thời."
  3. "**Bảo mật:** Dữ liệu nhạy cảm lưu ở Database, truy cập qua Backend có xác thực."

- *Chỉ tay vào sơ đồ khi nói.*

---

## SLIDE 12: Quy trình hệ thống (30 giây)

**Chú thích:**
- "Quy trình tổng quát 4 bước:"
  1. "User gửi câu hỏi qua Web."
  2. "Backend xác thực và điều phối."
  3. "AI tìm thông tin từ Database."
  4. "Trả kết quả kèm trích dẫn trong **1-2 giây**."

---

## SLIDE 13: Quy trình RAG Retrieval (1 phút 15 giây)

**Chú thích:**
- "Đây là **lõi hệ thống** - Quy trình RAG gồm 7 bước:"

**Pipeline (nói nhanh):**
1. **Chuẩn hóa:** "Làm sạch câu hỏi."
2. **Dense Search:** "Tìm theo ngữ nghĩa, lấy Top 30."
3. **Sparse Search (BM25):** "Tìm theo từ khóa, lấy Top 30."
4. **Hybrid Fusion (RRF):** "Kết hợp 2 kết quả trên."
5. **Reranking:** "Cross-Encoder chấm điểm lại, chọn Top 20."
6. **Context Builder:** "Lấy Top 15 tốt nhất."
7. **LLM:** "Gemini sinh câu trả lời kèm trích dẫn."

- **Nhấn mạnh:** "Quy trình này đạt **85% độ chính xác**, cao hơn ChatGPT thông thường (60%)."

---

## SLIDE 14: Bảo mật (1 phút)

**Chú thích:**
- "Bảo mật rất quan trọng với ngành Công an. Hệ thống có **4 lớp bảo vệ:**"

**1. Lớp Xác thực:**
- "JWT + RBAC + Bcrypt → Đảm bảo đúng người, đúng quyền."

**2. Lớp Mạng:**
- "HTTPS/TLS 1.2+ → Mã hóa 100% dữ liệu, chống nghe lén."

**3. Lớp Dữ liệu:**
- "SHA256 Checksum + Input Validation → File không bị thay đổi, dữ liệu luôn sạch."

**4. Chống tấn công:**
- "Rate Limiting (60 req/phút) + Redis Blacklist → Chống DDoS, thu hồi quyền tức thì."

---

## SLIDE 15: Chương trình minh họa (20 giây)

**Chú thích:**
- "Hệ thống đã triển khai tại **www.psuchatbot.com** với 6 chức năng chính."
- "Em xin phép chuyển sang phần **demo thực tế** để Quý Thầy Cô dễ hình dung hơn."

**→ CHUYỂN SANG DEMO**

---

## 🎯 TIPS QUAN TRỌNG CHO 10 PHÚT

### ✅ Kỹ năng nói:
1. **Nói nhanh nhưng rõ:** ~150-160 từ/phút.
2. **Bỏ qua chi tiết không quan trọng:** Tập trung vào 3-4 điểm chính mỗi slide.
3. **Dùng "tay chỉ":** Chỉ vào sơ đồ khi giải thích để tiết kiệm thời gian nói.
4. **Không đọc slides:** Chỉ nói ý chính, slides là gợi nhớ.

### ⏱️ Timeline thực tế:
| Slide | Thời gian | Tích lũy |
|-------|-----------|----------|
| 1 | 20s | 0:20 |
| 2 | 15s | 0:35 |
| 3 | 10s | 0:45 |
| 4 | 35s | 1:20 |
| 5 | SKIP | 1:20 |
| 6 | 50s | 2:10 |
| 7 | 40s | 2:50 |
| 8 | 20s | 3:10 |
| 9 | 60s | 4:10 |
| 10 | 15s | 4:25 |
| 11 | 60s | 5:25 |
| 12 | 30s | 5:55 |
| 13 | 75s | 7:10 |
| 14 | 60s | 8:10 |
| 15 | 20s | 8:30 |
| **Dự phòng** | 90s | **10:00** |

### 🔥 Nếu vượt thời gian:
- **Bỏ Slide 5** (đã tích hợp vào Slide 4)
- **Slide 6:** Chỉ nói 3/5 mục tiêu
- **Slide 9:** Chỉ nói 3/7 công nghệ
- **Slide 13:** Nói vắn tắt pipeline thành 5 bước thay vì 7

### 🎬 Chuyển sang Demo:
- "Quý Thầy Cô đã hiểu kiến trúc tổng thể. Giờ em xin demo hệ thống thực tế."
- Mở trước tab **www.psuchatbot.com** để không mất thời gian.

---

**Chúc bạn thuyết trình thành công! 🎓🔥**
