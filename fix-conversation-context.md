# Fix Context Loss & Stateless Chatbot

## Goal
Chatbot phải nhớ ngữ cảnh hội thoại — khi user hỏi "Cụ thể hơn đi?" phải trả lời đúng chủ đề câu hỏi trước.

## Root Cause
| Bug | Nguyên nhân | File |
|-----|-------------|------|
| **Context Loss** | `async_rag_service.py` streaming/non-streaming đều KHÔNG gọi `_rewrite_query_with_history()` | `async_rag_service.py` |
| **Stateless** | Frontend KHÔNG gửi `conversation_history` trong request body | `page.tsx` |

## Tasks
- [x] Task 1: FE — gửi `conversation_history` (6 tin nhắn gần nhất) trong streaming request body tại `page.tsx` → Verify: console.log request body thấy history
- [x] Task 2: FE — gửi `conversation_history` trong vision (image) request body tại `page.tsx` → Verify: request body có history
- [x] Task 3: BE — thêm populate `conversation_history` + query rewriting vào `generate_answer_stream_async()` → Verify: server log thấy "Rewritten query"
- [x] Task 4: BE — thêm query rewriting vào `generate_answer_async()` → Verify: server log thấy "Rewritten query"
- [ ] Task 5: Test — hỏi follow-up "Cụ thể hơn đi?" sau 1 câu hỏi → Bot trả lời đúng chủ đề

## Done When
- [ ] Follow-up questions giữ đúng ngữ cảnh xuyên suốt cuộc hội thoại
