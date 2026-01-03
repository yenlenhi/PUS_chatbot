# ✅ Hướng dẫn cấu hình Supabase Storage cho Image Persistence

## 🎉 Status: HOÀN THÀNH

### Đã Làm Xong:
- ✅ Database migration: Thêm cột `images` vào bảng `conversations`
- ✅ Backend: Upload images tự động khi user gửi chat
- ✅ Frontend: Hiển thị images trong admin chat history
- ✅ Supabase bucket: `chat-attachments` đã được tạo
- ✅ Credentials: Đã cấu hình trong `.env`

---

## 1. ✅ Tạo Storage Bucket (ĐÃ XONG)

Truy cập Supabase Dashboard → Storage và tạo bucket mới:

```
Bucket Name: chat-attachments
Public: ❌ Private (không public)
File Size Limit: 10 MB
Allowed MIME types: image/jpeg, image/png, image/gif, image/webp
```

## 2. ⚠️ Cấu hình Storage Policies (RLS) - CẦN LÀM

**Quan trọng:** Để images có thể upload được, bạn cần chạy SQL policies.

### Cách 1: Tự động (Khuyến nghị)

Vào Supabase Dashboard → SQL Editor và chạy file:
```
scripts/setup_storage_policies.sql
```

### Cách 2: Thủ công

Vào bucket "chat-attachments" → Policies và thêm từng policy:

### Policy cho Upload (INSERT):
```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'chat-attachments');
```

### Policy cho Read (SELECT):
```sql
CREATE POLICY "Allow authenticated reads"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'chat-attachments');
```

### Policy cho Delete:
```sql
CREATE POLICY "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'chat-attachments');
```

## 3. ✅ Kiểm tra Environment Variables (ĐÃ XONG)

File `.env` đã có đầy đủ các biến:

```env
# Supabase API URL (không phải database URL)
SUPABASE_URL=https://thessjemstjljfbkvzih.supabase.co

# Service Role Key (có quyền bypass RLS)
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Anon Key (cho client-side)
SUPABASE_ANON_KEY=your-anon-key-here
```

**Lưu ý:** SUPABASE_URL phải là API URL (bắt đầu bằng `https://`), không phải database connection string (bắt đầu bằng `postgresql://`).

## 4. Test Upload

Sau khi cấu hình xong, test bằng cách:

1. Gửi tin nhắn có kèm hình ảnh trong chatbot
2. Kiểm tra Supabase Storage → chat-attachments → {conversation_id}/
3. Kiểm tra database: `SELECT images FROM conversations WHERE conversation_id = '...'`
4. Xem chi tiết cuộc hội thoại trong admin panel: http://localhost:3000/admin/chat-history

## 5. Troubleshooting

### Lỗi "Bucket not found"
- Đảm bảo đã tạo bucket tên "chat-attachments"
- Kiểm tra SUPABASE_URL đúng là API URL

### Lỗi "Unauthorized"
- Kiểm tra SUPABASE_SERVICE_KEY đã đúng chưa
- Xác nhận Storage Policies đã được cấu hình

### Images không hiển thị
- Kiểm tra console log xem có lỗi CORS không
- Kiểm tra URL trong database có đúng format không
- Test URL trực tiếp trong browser

## 6. Database Schema

Đã thêm cột `images` vào bảng `conversations`:

```sql
ALTER TABLE conversations ADD COLUMN images TEXT;
```

Format dữ liệu: JSON array of image URLs
```json
["https://supabase.co/storage/v1/object/chat-attachments/conv-id/image1.png", "..."]
```
