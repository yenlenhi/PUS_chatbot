# Fix: Chatbot mất ngữ cảnh hội thoại khi hỏi follow-up

## Goal
Khi user hỏi "Cụ thể hơn đi?" sau câu hỏi trước, chatbot phải hiểu ngữ cảnh và trả lời đúng chủ đề.

## Root Cause Analysis

**2 nguyên nhân chính:**

1. **Frontend không gửi `conversation_history`**
   - File: `frontend/src/app/chat-bot/page.tsx` (line 1030-1034)
   - Streaming request chỉ gửi `{ message, conversation_id, language }` — thiếu `conversation_history`
   - Backend nhận được history rỗng → không thể rewrite query

2. **Async RAG service bỏ qua query rewriting**
   - File: `src/services/async_rag_service.py`
   - Cả 2 path (streaming line 230+ và non-streaming line 62+) đều **KHÔNG** gọi `_rewrite_query_with_history()`
   - Chỉ có sync `rag_service.py` mới gọi (line 1214)

**Luồng hiện tại (BUG):**
```
User: "Thông tin về Văn bằng 2?"  → Backend tìm đúng
User: "Cụ thể hơn đi?"           → Backend tìm "cụ thể hơn" → không liên quan!
```

**Luồng mong muốn (FIX):**
```
User: "Thông tin về Văn bằng 2?"  → Backend tìm đúng
User: "Cụ thể hơn đi?"           → Rewrite thành "Chi tiết hơn về Văn bằng 2 công an" → tìm đúng!
```

## Tasks

- [ ] Task 1: Frontend gửi `conversation_history` kèm mỗi request → Verify: log request body thấy history
- [ ] Task 2: `async_rag_service.py` — thêm query rewriting vào cả 2 path (streaming + non-streaming) → Verify: log thấy rewritten query
- [ ] Task 3: Test thủ công trên website → Verify: hỏi follow-up "Cụ thể hơn đi?" trả lời đúng ngữ cảnh

## Proposed Changes

### Frontend — `page.tsx`

#### [MODIFY] [page.tsx](file:///c:/TruongVanKhai/Project/uni_bot/frontend/src/app/chat-bot/page.tsx)

Tại cả 2 chỗ gọi API (streaming line 1030 và vision line 974):
- Thêm `conversation_history` từ state `messages` (lấy 6 tin nhắn gần nhất, chỉ lấy `role` + `content`)

```diff
 body: JSON.stringify({
   message: currentQuery,
   conversation_id: conversationId,
   language: language,
+  conversation_history: messages
+    .filter(m => m.id !== '1')  // Bỏ welcome message
+    .slice(-6)                  // 6 tin nhắn gần nhất (3 cặp Q&A)
+    .map(m => ({ role: m.role === 'bot' ? 'assistant' : m.role, content: m.content })),
 })
```

---

### Backend — `async_rag_service.py`

#### [MODIFY] [async_rag_service.py](file:///c:/TruongVanKhai/Project/uni_bot/src/services/async_rag_service.py)

**Non-streaming path** (`generate_answer_async`, sau line 113):
```diff
+            # Rewrite query using conversation history for context
+            current_history = self.rag_service.conversations.get(conversation_id, [])
+            if current_history:
+                rewritten_query = await self._run_in_executor(
+                    self.rag_service._rewrite_query_with_history,
+                    normalized_query,
+                    current_history,
+                )
+                if rewritten_query != normalized_query:
+                    log.info(f"[ASYNC] Rewritten query: '{rewritten_query[:80]}'")
+                    normalized_query = rewritten_query
```

**Streaming path** (`generate_answer_stream_async`, sau line 269):
```diff
+            # Rewrite query using conversation history
+            current_history = self.rag_service.conversations.get(conversation_id, [])
+            if current_history:
+                rewritten_query = await self._run_in_executor(
+                    self.rag_service._rewrite_query_with_history,
+                    normalized_query,
+                    current_history,
+                )
+                if rewritten_query != normalized_query:
+                    log.info(f"[ASYNC STREAM] Rewritten: '{normalized_query[:30]}' -> '{rewritten_query[:50]}'")
+                    normalized_query = rewritten_query
```

**Cả 2 path**: Cũng cần populate conversation_history vào in-memory dict nếu có:
- Đã có code kiểm tra `if conversation_history and not self.rag_service.conversations[conversation_id]` — OK cho non-streaming
- Streaming path thiếu — cần thêm

## Verification Plan

### Manual Verification
1. Chạy server local hoặc deploy
2. Mở chatbot, hỏi: "Thông tin về Văn bằng 2 công an?"
3. Sau khi bot trả lời, hỏi tiếp: "Cụ thể hơn đi?"
4. Kiểm tra bot trả lời **đúng chủ đề Văn bằng 2**, không lạc sang topic khác
5. Thử thêm: "Điều kiện tuyển sinh?" → "Còn gì nữa không?" → Bot phải trả lời về tuyển sinh

## Done When
- [ ] Follow-up questions ("Cụ thể hơn đi?", "Còn gì nữa?") đều trả lời đúng ngữ cảnh
