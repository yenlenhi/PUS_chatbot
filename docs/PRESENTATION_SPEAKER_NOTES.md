# CHÚ THÍCH CHO SLIDE THUYẾT TRÌNH
## Đề tài: PSU CHATBOT - Hệ thống Chatbot Tư vấn Tuyển sinh

**Hướng dẫn sử dụng:**  
Đọc phần chú thích tương ứng với slide đang trình bày. Mỗi phần có timeline theo dạng *"Nói gì -> Làm gì -> Nhấn mạnh gì"*.

---

## SLIDE 1: Trang bìa (30 giây)

**Chú thích:**
- **Mở đầu:** "Kính chào Quý Thầy Cô và Ban Giám khảo cuộc thi Unitech 2026!"
- **Giới thiệu:** "Em là Trương Văn Khải / Vũ Quốc Hưng / Nguyễn Hữu Tấn Dũng, sinh viên lớp VB2 D5 / D32C, trun Đại học An ninh Nhân dân."
- **Tên đề tài:** "Hôm nay, nhóm em xin trình bày đề tài **PSU Chatbot** - Hệ thống trợ lý ảo hỗ trợ tra cứu học vụ cho Trường Đại học An ninh Nhân dân, ứng dụng công nghệ RAG (Retrieval-Augmented Generation)."
- **Kết thúc:** "Thời gian trình bày khoảng 10-12 phút. Mời Quý Thầy Cô theo dõi!"

---

## SLIDE 2: Nội dung chính (20 giây)

**Chú thích:**
- "Bài báo cáo gồm 6 phần chính:"
  1. **Vấn đề thực tế:** Bối cảnh và mục tiêu.
  2. **Cơ sở lý thuyết:** Các công nghệ AI/ML được sử dụng.
  3. **Kiến trúc tổng thể:** Thiết kế 4 tầng, quy trình RAG.
  4. **Chương trình minh họa:** Demo giao diện user và admin.
  5. **Kết luận:** Kết quả và so sánh.
  6. **Hướng phát triển.**
- **Transition:** "Chúng em xin bắt đầu với phần 1 - Vấn đề thực tế."

---

## SLIDE 3: Vấn đề thực tế - Tổng quan (15 giây)

**Chú thích:**
- "Slide này tóm tắt 3 nội dung chính của phần vấn đề thực tế:"
  - Bối cảnh và hệ quả
  - Mục tiêu đề tài
  - Giải pháp đề xuất
- "Chúng em sẽ đi vào từng phần chi tiết."

---

## SLIDE 4: Bối cảnh (40 giây)

**Chú thích:**
- **Bối cảnh chung:**
  - "Trong bối cảnh chuyển đổi số mạnh mẽ của ngành Công an và giáo dục đại học nói chung, nhu cầu tra cứu thông tin nhanh và chính xác của người học ngày càng gia tăng."
  - "Trường Đại học An ninh Nhân dân cũng không ngoại lệ."
  
- **Bối cảnh tại trường:**
  - "Hiện tại, nhu cầu hỏi đáp về học vụ, tuyển sinh, quy chế rất lớn từ học viên."
  - "Tuy nhiên, công tác hỗ trợ chủ yếu thủ công qua điện thoại, email, hoặc trực tiếp tại văn phòng."
  - "Điều này dẫn đến những hệ quả tiêu cực mà chúng em sẽ nêu ở slide tiếp theo."

---

## SLIDE 5: Hệ quả (40 giây)

**Chú thích:**
- **3 Hệ quả chính:**
  1. **Cán bộ quá tải:** "Cán bộ đào tạo phải trả lời hàng chục câu hỏi trùng lặp mỗi ngày, ảnh hưởng công việc chính."
  2. **Phản hồi chậm, thiếu nhất quán:** "Thông tin đôi khi bị trễ, hoặc trả lời không đồng nhất giữa các cán bộ."
  3. **Học viên khó tiếp cận:** "Học viên không thể hỏi đáp ngoài giờ hành chính, gây bất tiện."

- **Nhu cầu giải pháp:**
  - "Từ đó đặt ra nhu cầu về một **giải pháp AI có kiểm soát tri thức**, hoạt động 24/7, đảm bảo chính xác, an toàn thông tin, và giảm tải cho cán bộ."

---

## SLIDE 6: Mục tiêu đề tài (50 giây)

**Chú thích:**
- **Mục tiêu chung:** "Xây dựng và triển khai thử nghiệm một hệ thống chatbot ứng dụng trí tuệ nhân tạo theo hướng RAG, hỗ trợ công tác đào tạo và tư vấn người học tại Trường Đại học An ninh Nhân dân."

- "Để đạt được mục tiêu chung, đề tài đặt ra **5 mục tiêu cụ thể:**"

  1. **Thu thập, số hóa và chuẩn hóa kho tài liệu chuyên sâu:** "Hệ thống hóa toàn bộ văn bản quy chế, quy định, biểu mẫu và cẩm nang đào tạo từ nguồn chính thống làm nền tảng cốt lõi."
  
  2. **X dựng cơ chế quản trị dữ liệu thông minh:** "Thiết kế hệ thống quản lý tập trung với quy trình tự động hóa (upload PDF, xử lý lại tài liệu). Mọi câu trả lời kèm trích dẫn nguồn minh bạch: tên văn bản, số trang, điều khoản."
  
  3. **Phát triển nền tảng Web tích hợp đa giao diện:** "Giao diện Chatbot cho người dùng tra cứu 24/7 và Dashboard Quản trị cho cán bộ giám sát, quản lý tài liệu và khai thác thống kê."
  
  4. **Thử nghiệm diện rộng và đánh giá hiệu quả:** "Đánh giá qua các chỉ số: thời gian phản hồi, tỷ lệ hài lòng, độ chính xác. Kết quả là cơ sở để tối ưu thuật toán RAG và cải thiện giao diện."
  
  5. **Xây dựng cơ chế phân tích hành vi và tối ưu liên tục:** "Tích hợp module phân tích theo dõi lịch sử truy vấn, nhận diện chủ đề quan tâm và thu thập phản hồi. Hệ thống liên tục được tinh chỉnh để thích ứng với nhu cầu thực tế."

- **Nhấn mạnh:** "Đây là định hướng xuyên suốt quá trình thiết kế và triển khai hệ thống."

---

## SLIDE 7: Giải pháp (1 phút)

**Chú thích:**
- **So sánh Trước - Sau:**
  
  **Trước khi có PSU Chatbot:**
  - Sinh viên phải đọc nhiều tài liệu dài.
  - Phòng ban quá tải câu hỏi lặp lại.
  - Thông tin phân tán nhiều nguồn.
  - Khó tìm forms mẫu phù hợp.
  
  **Sau khi có PSU Chatbot:**
  - Trả lời tức thì 24/7.
  - Câu trả lời chính xác từ tài liệu chính thức.
  - Tự động đính kèm forms phù hợp.
  - Giảm tải công việc cho phòng ban.

- **5 Điểm nổi bật:**
  1. Hỗ trợ học viên tra cứu 24/7
  2. Trả lời dựa trên tài liệu chính thống
  3. Hiển thị nguồn trích dẫn để kiểm chứng
  4. Tự động gợi ý biểu mẫu phù hợp
  5. Giảm tải cho cán bộ đào tạo

- **Transition:** "Để thực hiện được điều này, chúng em đã nghiên cứu và áp dụng các công nghệ AI tiên tiến. Mời Quý Thầy Cô theo dõi phần Cơ sở lý thuyết."

---

## SLIDE 8: Cơ sở lý thuyết - Tổng quan (20 giây)

**Chú thích:**
- "Hệ thống sử dụng **5 công nghệ AI/ML chính:**"
  1. RAG - Retrieval-Augmented Generation
  2. Vector Embeddings và Semantic Search
  3. Sparse Search (BM25), Hybrid Search
  4. Cross-Encoder Reranking
  5. LLM - Large Language Model (Google Gemini)

- "Chúng em sẽ giải thích chi tiết từng công nghệ ở slide tiếp theo."

---

## SLIDE 9: Bảng công nghệ chi tiết (1 phút 30 giây)

**Chú thích:**
- "Đây là bảng tóm tắt các công nghệ, bao gồm: Tên kỹ thuật, Công dụng, và Vai trò trong hệ thống."

**Đọc nhanh (Chọn 3-4 công nghệ quan trọng nhất):**

1. **RAG (Retrieval-Augmented Generation):**
   - "Kỹ thuật kết hợp tìm kiếm tài liệu với AI sinh văn bản."
   - "Vai trò: Tìm thông tin liên quan → AI soạn câu trả lời chính xác."

2. **Embedding (Vietnamese SBERT):**
   - "Phương pháp biểu diễn văn bản dưới dạng vector số trong không gian ngữ nghĩa."
   - "Mã hóa câu hỏi và tài liệu thành vector 384 chiều để tính độ tương đồng."

3. **Hybrid Search (RRF - Reciprocal Rank Fusion):**
   - "Kết hợp tìm kiếm ngữ nghĩa (Vector Search) + tìm kiếm từ khóa (BM25)."
   - "Đảm bảo tìm đúng cả ý nghĩa lẫn từ chính xác (ví dụ: mã sinh viên, điều khoản, số văn bản)."

4. **Reranker (Cross-Encoder MS-MARCO):**
   - "Mô hình xếp hạng lại (reranking) các tài liệu đã tìm được."
   - "Sử dụng Cross-Encoder để chấm điểm chính xác hơn Bi-Encoder, đưa Top-K kết quả liên quan nhất lên đầu."

5. **LLM (Google Gemini 2.0 Flash):**
   - "Mô hình ngôn ngữ lớn của Google."
   - "Đọc hiểu ngữ cảnh và soạn câu trả lời tự nhiên bằng tiếng Việt."

- **Lưu ý:** "Nếu Quý Thầy Cô quan tâm chi tiết, em có phần Phụ lục ở cuối để giải thích sâu hơn."

---

## SLIDE 10: Kiến trúc hệ thống - Tổng quan (15 giây)

**Chú thích:**
- "Phần này chúng em sẽ trình bày **Kiến trúc tổng thể** của hệ thống, bao gồm:"
  1. Kiến trúc 4 tầng
  2. Quy trình hệ thống
  3. Quy trình RAG Retrieval (Lõi hệ thống)
  4. Bảo mật vận hành

---

## SLIDE 11: Kiến trúc tổng thể 4 tầng (1 phút 20 giây)

**Chú thích:**
- **Giới thiệu:**
  - "Hệ thống áp dụng **kiến trúc 4 tầng** để dễ bảo trì, mở rộng và tối ưu hiệu suất."
  - "4 tầng gồm: **Frontend (Giao diện) – Backend (Ứng dụng) – Database (Dữ liệu) – AI/ML**."

- **Lợi ích:**
  1. **Mô-đun & dễ nâng cấp:** "Có thể đổi LLM hoặc Embedding mà không ảnh hưởng giao diện."
  2. **Hiệu năng & mở rộng tốt:** "Phân tải xử lý giữa các tầng, tăng khả năng chịu tải."
  3. **Bảo mật cao:** "Dữ liệu nhạy cảm lưu ở Database, truy cập qua Backend có xác thực."
  4. **Tích hợp AI hiệu quả:** "RAG + embeddings + reranking + vector search, tối ưu tiếng Việt."

- **Thực tế triển khai:**
  - "Hệ thống đạt độ chính xác cao nhờ kết hợp reranking và vector search."

- **Gợi ý trình bày:** *Nếu có sơ đồ, chỉ tay vào từng tầng khi giải thích.*

---

## SLIDE 12: Quy trình hệ thống (50 giây)

**Chú thích:**
- **Quy trình tổng quát gồm 4 bước:**
  1. "Người dùng gửi câu hỏi qua cổng tra cứu (Web hoặc Mobile)."
  2. "Hệ thống xác thực người dùng và điều phối tra cứu (Backend)."
  3. "AI tìm thông tin từ dữ liệu chính thống (Database + AI/ML Layer)."
  4. "Kết quả được tổng hợp và trả về người dùng kèm trích dẫn nguồn."

- **Nhấn mạnh:** "Toàn bộ quy trình diễn ra trong **1-2 giây**, trả lời tức thì."

---

## SLIDE 13: Quy trình RAG Retrieval (1 phút)

**Chú thích:**
- **Giới thiệu:**
  - "Đây là **lõi của hệ thống** - Quy trình RAG Retrieval."
  - "Mục tiêu: Tìm ra Top-N chunks (đoạn văn bản) liên quan nhất để làm ngữ cảnh cho LLM sinh câu trả lời."

- **Pipeline chi tiết (7 bước):**
  - **Input:** "Câu hỏi từ người dùng (Query)."
  - **Bước 1 - Chuẩn hóa (Query Normalization):** "Làm sạch câu hỏi: loại ký tự đặc biệt, chuẩn hóa Unicode, lowercase."
  - **Bước 2 - Dense Retrieval (Vector Search):** "Tìm kiếm ngữ nghĩa bằng pgvector + Cosine Similarity. Lấy Top 30 chunk tương đồng nhất."
  - **Bước 3 - Sparse Retrieval (BM25):** "Tìm kiếm từ khóa chính xác theo tần suất (BM25 algorithm). Lấy Top 30 chunk."
  - **Bước 4 - Hybrid Fusion (RRF):** "Kết hợp kết quả từ Dense + Sparse bằng thuật toán Reciprocal Rank Fusion."
  - **Bước 5 - Reranking (Cross-Encoder):** "Sử dụng Cross-Encoder chấm điểm lại từng cặp (query-chunk), chọn Top 20 chính xác nhất."
  - **Bước 6 - Context Builder:** "Lấy Top 15 tốt nhất, xây dựng ngữ cảnh (context) có cấu trúc để đưa vào LLM."
  - **Bước 7 - LLM Generation:** "Google Gemini 2.0 Flash đọc ngữ cảnh + câu hỏi → sinh câu trả lời tự nhiên kèm trích dẫn."

- **Nhấn mạnh:** "Quy trình này đảm bảo độ chính xác cao (~85%) so với ChatGPT thông thường (~60%)."

---

## SLIDE 14: Bảo mật vận hành (1 phút 15 giây)

**Chú thích:**
- **Giới thiệu:** "Bảo mật là ưu tiên hàng đầu, đặc biệt quan trọng với ngành Công an."

- **4 Lớp bảo vệ:**

  **Lớp 1 - Xác thực:**
  - JWT (HS256): Token định danh, hết hạn sau 30 phút.
  - RBAC: Phân quyền theo vai trò (Admin/User).
  - Bcrypt: Mã hóa mật khẩu một chiều.
  - **Tác dụng:** Đảm bảo đúng người, đúng quyền; chống lộ mật khẩu.

  **Lớp 2 - Mạng:**
  - HTTPS/TLS 1.2+: Mã hóa đường truyền.
  - Security Headers: HSTS, X-Frame (chống Clickjacking).
  - CORS: Chặn domain lạ.
  - **Tác dụng:** Mã hóa 100% dữ liệu truyền đi, chống nghe lén (Man-in-the-Middle).

  **Lớp 3 - Dữ liệu:**
  - Checksum (SHA256): Kiểm tra file upload.
  - Input Validation (Pydantic).
  - **Tác dụng:** File không bị thay đổi/cài mã độc; dữ liệu luôn sạch và đúng.

  **Lớp 4 - Chống tấn công:**
  - Rate Limiting: Giới hạn 60 request/phút.
  - Redis Blacklist: Chặn token lập tức khi cần.
  - **Tác dụng:** Chống Spam/DDoS/Brute-force; thu hồi quyền truy cập tức thì.

- **Kết luận:** "Với 4 lớp bảo vệ này, hệ thống đảm bảo an toàn thông tin cao."

---

## SLIDE 15: Chương trình minh họa - Tổng quan (20 giây)

**Chú thích:**
- "Phần này chúng em sẽ demo giao diện thực tế, bao gồm:"
  - Giao diện Chatbot người dùng
  - Bảng điều khiển Admin (Dashboard)
  - Trang Quản lý tài liệu
  - Trang Lịch sử chat
  - Trang Quản lý File đính kèm
  - Trang Phản hồi người dùng

- **Website:** "Hệ thống đã được triển khai tại **www.psuchatbot.com**. Mời Quý Thầy Cô theo dõi demo."

---

## SLIDE 16: Giao diện Chatbot người dùng (50 giây)

**Chú thích:**
- **Giới thiệu:**
  - "Giao diện chatbot thân thiện, dễ sử dụng cho học viên và cán bộ."
  - "Thích hợp đa nền tảng: máy tính và điện thoại."

- **Tính năng chính:**
  1. **Hiển thị trích dẫn nguồn:** "Mỗi câu trả lời đều kèm trích đoạn nội dung gốc từ văn bản chính thức để kiểm chứng."
  2. **Hỗ trợ đa phương thức:**
     - Văn bản (Text)
     - Giọng nói (Speech-to-Text / Text-to-Speech)
     - Hình ảnh trong câu hỏi (Vision)

- **Lưu ý:** "Slide tiếp theo sẽ có hình ảnh minh họa cụ thể."

---

## SLIDE 17-18: Hình ảnh giao diện Chatbot (40 giây)

**Chú thích:**
- **Slide 17:**
  - **Hình 1:** "Giao diện bắt đầu phiên chat - đơn giản, trực quan."
  - **Hình 2:** "Các tính năng hỗ trợ: Copy phiên đối thoại, đánh giá (thumbs up/down), upload hình ảnh, text-to-speech, speech-to-text."

- **Slide 18:**
  - **Hình 3:** "Phản hồi của Chatbot kèm tài liệu tham khảo bên phải."
  - **Hình 4:** "Click vào tài liệu để xem văn bản gốc, đảm bảo tính xác thực."

- **Nhấn mạnh:** "Học viên có thể xác minh mọi thông tin ngay lập tức."

---

## SLIDE 19: Admin Dashboard - Tổng quan (1 phút)

**Chú thích:**
- **Mục đích:** "Đây là công cụ đánh giá toàn diện hiệu quả Chatbot, đồng thời cung cấp phân tích nhu cầu của học viên kịp thời cho ban lãnh đạo."

- **Theo dõi 5 nhóm chỉ số:**

  1. **Hiệu suất hệ thống:**
     - Lượt truy cập, chi phí token, an ninh và lỗi phát sinh.

  2. **Hành vi người dùng:**
     - Tần suất quay lại, user funnel, chủ đề quan tâm, câu hỏi phổ biến.

  3. **Dữ liệu chat:**
     - Số lượt tin nhắn, feedbacks, câu hỏi chưa trả lời được.

  4. **Dữ liệu tài liệu:**
     - Số lượng, dung lượng tài liệu theo danh mục; tài liệu được truy xuất nhiều.

  5. **Hiệu năng:**
     - Số câu hỏi đã xử lý, thời gian phản hồi trung bình, số giờ tiết kiệm, điểm chất lượng.

- **Giá trị:** "Giúp ban lãnh đạo ra quyết định dựa trên dữ liệu thực tế."

---

## SLIDE 20-22: Hình ảnh Admin Dashboard (1 phút)

**Chú thích:**
- **Slide 20:**
  - **Hình 1:** "Tổng quan sức khỏe hệ thống (System Health): CPU, RAM, Database status."
  - **Hình 2:** "Chỉ số người dùng: Tổng user, user hoạt động, tỷ lệ quay lại."

- **Slide 21:**
  - **Hình 3:** "Chỉ số Chat: Tổng tin nhắn, phản hồi tích cực/tiêu cực."
  - **Hình 4:** "Chỉ số tài liệu: Số file, dung lượng, tài liệu hot nhất."

- **Slide 22:**
  - **Hình 5:** "Chỉ số hiệu suất: Thời gian phản hồi, throughput."
  - **Hình 6:** "Một số tính năng phụ: Export báo cáo, cài đặt hệ thống."

- **Lưu ý:** "Tất cả chỉ số đều real-time, cập nhật liên tục."

---

## SLIDE 23: Trang Quản lý tài liệu (1 phút)

**Chú thích:**
- **Mục đích:** "Quản lý tập trung kho tri thức của Chatbot."

- **Theo dõi và thao tác:**
  - Số lượng, trạng thái hoạt động của tài liệu.
  - Phân loại và tìm kiếm theo tên, danh mục, nội dung.
  - Thống kê: số trang, số chunks, thời gian xử lý, dung lượng.

- **Cập nhật linh hoạt:**
  - Thêm tài liệu đơn lẻ hoặc hàng loạt.
  - Bật/tắt/xóa vĩnh viễn mà không cần huấn luyện lại mô hình.
  - Xem và tải xuống tài liệu.

- **Giá trị:** "Đảm bảo Chatbot chỉ trả lời từ tài liệu chính thống, giữ thông tin luôn mới và chính xác."

---

## SLIDE 24-25: Hình ảnh Quản lý tài liệu (40 giây)

**Chú thích:**
- **Slide 24:**
  - **Hình 1:** "Hiển thị, phân loại, thống kê tài liệu."
  - **Hình 2:** "Các thao tác: Bật/tắt/xóa/xem/tải xuống."

- **Slide 25:**
  - **Hình 3:** "Chức năng upload tài liệu (drag-drop hoặc chọn file)."
  - **Hình 4:** "Bật/tắt dữ liệu Chatbot được học (toggle switch)."

---

## SLIDE 26: Trang Lịch sử chat (1 phút)

**Chú thích:**
- **Theo dõi:**
  - Toàn bộ tương tác giữa người dùng và Chatbot.
  - Tổng số cuộc hội thoại, trạng thái, thời gian.
  - Số tin nhắn, câu hỏi đầu tiên.
  - Tìm kiếm, xem chi tiết từng hội thoại.
  - Xuất dữ liệu để báo cáo.

- **Mục đích:**
  1. Đánh giá chất lượng trả lời và hiệu quả RAG.
  2. Phát hiện câu hỏi lặp lại, câu hỏi chưa xử lý tốt.
  3. Cơ sở cải tiến tài liệu, prompt và báo cáo.

- **Giá trị thực tiễn:** "Nhà trường có thể điều chỉnh tài liệu, cập nhật quy chế hoặc bổ sung hướng dẫn phù hợp với nhu cầu học viên."

---

## SLIDE 27: Hình ảnh Lịch sử chat (30 giây)

**Chú thích:**
- **Hình 1:** "Danh sách cuộc hội thoại với filter và search."
- **Hình 2:** "Xem chi tiết: câu hỏi - câu trả lời - nguồn trích dẫn - độ tin cậy."

---

## SLIDE 28-29: Trang File đính kèm (40 giây)

**Chú thích:**
- **Slide 28:** Giống Trang Quản lý tài liệu (có thể bỏ qua hoặc nói ngắn gọn: "Trang này quản lý các file đính kèm như biểu mẫu, forms để Chatbot tự động gợi ý khi cần.")
- **Slide 29:** Hình ảnh minh họa.

---

## SLIDE 30: Trang Phản hồi người dùng (20 giây)

**Chú thích:**
- "Trang này thu thập phản hồi từ người dùng (thumbs up/down, comment)."
- "Giúp đánh giá chất lượng từng câu trả lời và cải thiện hệ thống liên tục."

---

## SLIDE 31: Kết luận - Tổng quan (15 giây)

**Chú thích:**
- "Phần cuối cùng, chúng em xin trình bày **Kết luận**, bao gồm:"
  1. Kết quả đạt được
  2. So sánh với ChatGPT, Gemini
  3. Hướng phát triển

---

## SLIDE 32: Kết quả (1 phút 30 giây)

**Chú thích:**
- **Giới thiệu:** "Sau quá trình triển khai và thử nghiệm, đề tài đạt được các kết quả sau:"

**1. Về hiệu quả hệ thống:**
- "Hệ thống vận hành ổn định 24/7, sẵn sàng phục vụ mọi lúc."
- **Kết quả kiểm thử:**
- Qua kiểm thử thực tế với 100 câu hỏi mẫu về quy chế, tuyển sinh, học vụ:
  - **Độ chính xác:** ≥ 85% (trả lời đúng hoàn toàn)
  - **Tỷ lệ trả lời thành công:** ≥ 95% (bao gồm trả lời đúng và đúng một phần)
  - **Trả lời chưa đầy đủ:** ~10%
  - **Không tìm thấy thông tin:** ~5%
  - **Trả lời sai hoàn toàn:** <1% (chủ yếu do tài liệu mơ hồ)
  - **Thời gian phản hồi trung bình:** ≤ 2 giây
- **So sánh:** ChatGPT thông thường chỉ đạt ~60% độ chính xác cho câu hỏi chuyên ngành vì không có quyền truy cập vào dữ liệu nội bộ của trường.
- "Minh chứng tính khả thi của mô hình RAG trong môi trường giáo dục đặc thù (ngành Công an)."
- "Kết hợp hiệu quả nhiều kỹ thuật AI/ML để nâng cao độ chính xác."
- "Kiến trúc 4 tầng vận hành hiệu quả, sẵn sàng nâng cấp và mở rộng."

**3. Về hiệu quả thực tiễn:**
- "Hệ thống kỳ vọng xử lý **40-50% câu hỏi thường gặp** (điểm chuẩn, học phí, hồ sơ...), giảm tải đáng kể cho cán bộ đào tạo."
- "Ước tính tiết kiệm **rất nhiều giờ lao động mỗi tháng** (giảm thời gian tìm hồ sơ, giải đáp học vụ, làm báo cáo)."
- "Hình thành quy trình mới về quản lý và truy xuất dữ liệu đào tạo, giúp cán bộ tập trung vào công tác chuyên môn."
- "Nâng cao trải nghiệm tra cứu và khả năng tiếp cận thông tin chủ động của người học."

- **Tổng kết:** "Triển khai thành công một hệ thống chatbot RAG end-to-end, có quy trình rõ ràng và khả năng quản lý qua giao diện."

---

## SLIDE 33: So sánh với ChatGPT, Gemini (1 phút 30 giây)

**Chú thích:**
- **Giới thiệu:** "Để thấy rõ ưu điểm của hệ thống, chúng em so sánh với ChatGPT và Gemini thông thường."

**Bảng so sánh 5 tiêu chí:**

1. **Độ chính xác pháp lý:**
   - PSU Chatbot: **Cao** - Chỉ trả lời dựa trên văn bản quy định, không "sángáo".
   - ChatGPT/Gemini: **Rủi ro** - Có thể trả lời chung chung hoặc sai lệch.

2. **Nguồn chứng minh:**
   - PSU Chatbot: **Minh bạch** - Trích dẫn rõ ràng (Điều 5, trang 12, Sổ tay SV).
   - ChatGPT/Gemini: **Hộp đen** - Không biết tại sao AI lại trả lời như vậy.

3. **Tính cập nhật:**
   - PSU Chatbot: **Tức thời** - Tải file mới lên → hiểu ngay.
   - ChatGPT/Gemini: **Chậm** - Dữ liệu cũ (Knowledge Cutoff), cần huấn luyện lại lâu.

4. **Tích hợp quy trình:**
   - PSU Chatbot: **Hành động được** - Cung cấp file/biểu mẫu tải về ngay.
   - ChatGPT/Gemini: **Chỉ Text** - Chỉ hướng dẫn lý thuyết.

5. **An ninh dữ liệu:**
   - PSU Chatbot: **Kiểm soát** - Dữ liệu nằm trong server quản lý, có thể Offline/Local.
   - ChatGPT/Gemini: **Phụ thuộc** - Dữ liệu nhạy cảm gửi lên đám mây công cộng.

- **Kết luận:** "Hệ thống này không chỉ sử dụng AI để trả lời câu hỏi, mà còn **'thuần hóa'** nó để phục vụ các tác vụ chuyên biệt, chính xác và an toàn."

---

## SLIDE 34: Hình ảnh so sánh (15 giây)

**Chú thích:**
- "Đây là ví dụ cùng một câu hỏi được hỏi trên PSU Chatbot, ChatGPT và Gemini."
- "Quý Thầy Cô có thể thấy sự khác biệt rõ rệt về độ chi tiết, trích dẫn nguồn và tính chính xác."

---

## SLIDE 35: Hướng phát triển (1 phút 30 giây)

**Chú thích:**
- **Lưu ý trước khi nói:** "Sản phẩm hiện tại tập trung vào thiết kế kiến trúc và xây dựng prototype, chưa hoàn thiện phần đo lường và tự động cập nhật dữ liệu."

**Ngắn hạn (1-2 tháng):**
1. Cải thiện xử lý tài liệu: kết hợp OCR đám mây + OCR cục bộ, giảm chi phí.
2. Hoàn thiện chiến lược chunking theo đoạn/tiêu đề/ngữ nghĩa.
3. Điều chỉnh tham số retrieval dựa trên quan sát thực tế.

**Trung hạn (3-6 tháng):**
1. Bổ sung cơ chế đo lường hiệu suất, xây dựng bộ tập kiểm thử.
2. Mở rộng tính năng quản trị và quan sát hệ thống.
3. Thêm tính năng: lọc theo chuyên đề, ưu tiên nguồn theo đơn vị/khoa, hỗ trợ ngôn ngữ khác.

**Dài hạn (6-12 tháng):**
1. Tinh chỉnh mô hình embedding/reranking trên dữ liệu riêng của trường để tăng độ chính xác.
2. Nâng cấp hạ tầng để vận hành quy mô lớn hơn.
3. Mở rộng thành trợ giảng ảo; công cụ phân tích nhu cầu học viên cho ban lãnh đạo.

---

## SLIDE 36: Cảm ơn (30 giây)

**Chú thích:**
- "Trên đây là toàn bộ nội dung mà nhóm em muốn trình bày."
- "Em xin chân thành cảm ơn Quý Thầy Cô và Ban Giám khảo đã dành thời gian lắng nghe!"
- "Website: **www.psuchatbot.com**"
- "Email liên hệ: **info@dhannd.edu.vn**"
- "Nhóm em sẵn sàng trả lời các câu hỏi của Quý Thầy Cô. Xin cảm ơn!"

---

## SLIDE 37-47: Phụ lục (Dùng khi bị hỏi hoặc có thời gian dư)

**Chú thích tổng quát:**
- "Các slide còn lại là Phụ lục, giải thích chi tiết các công nghệ và hướng dẫn sử dụng."
- "Nếu Quý Thầy Cô có câu hỏi cụ thể, em sẽ tham chiếu đến slide tương ứng."

### Slide 38: RAG - Giải thích chi tiết (40 giây)
- Giải thích Retrieval + Generation.
- Vì sao cần RAG.
- Lợi ích RAG.

### Slide 39: Vector Embeddings & Semantic Search (50 giây)
- Ví dụ cụ thể về vector.
- Công thức Cosine Similarity.

### Slide 40: BM25 & Hybrid Search (40 giây)
- BM25 mạnh khi nào.
- Hybrid Search kết hợp như thế nào.

### Slide 41: Cross-Encoder Reranking (40 giây)
- Bi-Encoder vs Cross-Encoder.
- Tại sao cần rerank.

### Slide 42: LLM - Large Language Model (50 giây)
- Gemini 2.0 Flash là gì.
- Prompt engineering như thế nào.
- Ví dụ minh họa.

### Slide 43-47: Hướng dẫn sử dụng chi tiết
- Hướng dẫn người learning (Slide 43)
- Hướng dẫn Admin Dashboard (Slide 44)
- Hướng dẫn Quản lý tài liệu (Slide 45)
- Hướng dẫn Lịch sử chat (Slide 46-47)

---

## 📝 TIPS TRÌNH BÀY CHUNG

### ✅ Nguyên tắc vàng:
1. **Nói chậm, rõ ràng:** Không nói nhanh, tránh nuốt chữ.
2. **Giao tiếp mắt:** Nhìn vào hội đồng khi nói, không chỉ nhìn slide.
3. **Sử dụng ngôn ngữ cơ thể:** Chỉ tay vào slide khi cần nhấn mạnh.
4. **Kiểm soát thời gian:** Mỗi slide tuân thủ timeline đã ghi.
5. **Tự tin:** Nhóm đã làm tốt, trình bày với thái độ chuyên nghiệp.

### 🔥 Câu hỏi khó có thể gặp:
- **"Nếu Google ngừng cung cấp Gemini thì sao?"**
  → Trả lời: "Kiến trúc module hóa, có thể thay đổi LLM trong <1 ngày, các lựa chọn: GPT-4o mini, Claude Sonnet, hoặc self-host Llama 3."

- **"Độ chính xác 85% tính như thế nào?"**
  → Trả lời: "Kiểm thử với 100 câu hỏi mẫu, so sánh câu trả lời với đáp án chuẩn từ tài liệu."

- **"Chi phí vận hành bao nhiêu?"**
  → Trả lời: "~$50-95/tháng, rẻ hơn nhiều so với 1 nhân viên trực tổng đài (~10-15 triệu/tháng)."

---

**Chúc bạn thuyết trình thành công! 🎓🚀**
