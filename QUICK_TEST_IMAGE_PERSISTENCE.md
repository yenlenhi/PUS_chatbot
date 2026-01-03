# 🚀 Quick Test Guide - Image Persistence

## Trước khi test:

### ⚠️ QUAN TRỌNG: Chạy Storage Policies

Vào Supabase Dashboard → SQL Editor và paste nội dung từ file:
```
scripts/setup_storage_policies.sql
```

Hoặc copy-paste trực tiếp:

```sql
-- Policy cho Upload (INSERT)
CREATE POLICY IF NOT EXISTS "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'chat-attachments');

-- Policy cho Read (SELECT)
CREATE POLICY IF NOT EXISTS "Allow authenticated reads"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'chat-attachments');

-- Policy cho Delete
CREATE POLICY IF NOT EXISTS "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'chat-attachments');

-- Policy cho Service Role (bypass RLS)
CREATE POLICY IF NOT EXISTS "Service role full access"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'chat-attachments');
```

---

## Test Workflow:

### 1. Kiểm tra servers đang chạy:
```bash
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### 2. Test upload image:
1. Mở chatbot: http://localhost:3000
2. Upload 1 hình ảnh bất kỳ
3. Gửi tin nhắn kèm hình

### 3. Verify upload thành công:

#### A. Kiểm tra Supabase Storage:
- Vào Supabase Dashboard → Storage → chat-attachments
- Sẽ thấy folder theo conversation_id
- Bên trong có file image được upload

#### B. Kiểm tra Database:
```sql
SELECT 
    conversation_id, 
    user_message,
    images,
    created_at
FROM conversations 
WHERE images IS NOT NULL 
ORDER BY created_at DESC 
LIMIT 5;
```

Kết quả sẽ có format:
```json
["https://thessjemstjljfbkvzih.supabase.co/storage/v1/object/chat-attachments/xxx/xxx.png"]
```

#### C. Kiểm tra Admin Panel:
1. Vào http://localhost:3000/admin/chat-history
2. Click "Xem chi tiết" của conversation vừa tạo
3. Sẽ thấy hình ảnh hiển thị trong user message bubble (nền xanh)

---

## Troubleshooting:

### ❌ Lỗi "Unauthorized" khi upload
**Nguyên nhân:** Chưa chạy Storage Policies
**Giải pháp:** Chạy SQL policies ở bước 1

### ❌ Images không hiển thị trong admin panel
**Kiểm tra:**
1. Console log có lỗi 403/404 không?
2. URL trong database có đúng format không?
3. Storage Policies đã chạy chưa?

### ❌ Bucket not found
**Giải pháp:** Chạy lại script tạo bucket:
```bash
python scripts/create_supabase_bucket.py
```

---

## Expected Result:

✅ **Upload thành công:**
- Backend log: "📸 Uploaded X images to Supabase Storage"
- Supabase Storage: Có file trong chat-attachments/{conversation_id}/
- Database: Cột images có array of URLs
- Admin Panel: Hình ảnh hiển thị trong chat history modal

---

## 📊 Architecture Flow:

```
User Upload Image (Frontend)
    ↓
POST /api/query với images[]
    ↓
RAG Service (rag_service.py)
    ↓
upload_chat_images() → Supabase Storage
    ↓
save_conversation(images=urls) → PostgreSQL
    ↓
get_conversation_detail() → Frontend
    ↓
Display in Admin Panel ✅
```
