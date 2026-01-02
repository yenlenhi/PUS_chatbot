# 🚀 Hướng Dẫn Migration từ Docker PostgreSQL sang Supabase

## 📋 Tổng Quan

Hướng dẫn này sẽ giúp bạn chuyển toàn bộ database từ Docker Desktop PostgreSQL sang Supabase (managed PostgreSQL service).

## ✅ Lợi Ích Khi Chuyển Sang Supabase

- ✨ **Không cần Docker Desktop**: Giảm tải tài nguyên máy local
- 🌐 **Cloud-based**: Truy cập từ mọi nơi
- 🔒 **Backup tự động**: Dữ liệu được backup định kỳ
- 📈 **Scalable**: Dễ dàng scale khi cần
- 🆓 **Free tier**: 500MB database + 1GB file storage miễn phí
- 🚀 **Tích hợp sẵn**: pgvector extension, REST API, Realtime subscriptions

## 📝 Các Bước Migration

### **Bước 1: Setup Supabase Project** ⚙️

1. Truy cập [supabase.com](https://supabase.com)
2. Đăng ký/Đăng nhập
3. Click **New Project**
4. Điền thông tin:
   - **Project Name**: `uni-bot`
   - **Database Password**: Tạo password mạnh và **LƯU LẠI**
   - **Region**: `Southeast Asia (Singapore)` (gần Việt Nam nhất)
   - **Pricing Plan**: **Free** (đủ cho development)
5. Click **Create new project**
6. ⏳ Chờ 2-3 phút để Supabase khởi tạo database

### **Bước 2: Lấy Connection String** 🔗

1. Trong Supabase Dashboard → **Settings** (⚙️ bên trái)
2. Click **Database**
3. Scroll xuống **Connection string**
4. Chọn tab **URI**
5. Copy connection string (dạng):
   ```
   postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
6. **Lưu lại connection string này!**

### **Bước 3: Run Migration SQL Script** 📊

**Option A: Qua Supabase SQL Editor (Recommended)**

1. Trong Supabase Dashboard → **SQL Editor** (⚡ bên trái)
2. Click **New query**
3. Copy toàn bộ nội dung file `scripts/migrate_to_supabase.sql`
4. Paste vào editor
5. Click **Run** (hoặc `Ctrl+Enter`)
6. ✅ Kiểm tra output: Phải thấy "Tables created successfully!"

**Option B: Qua Command Line**

```powershell
# Install psql if not installed
# Download from: https://www.postgresql.org/download/windows/

# Run migration script
psql "YOUR_SUPABASE_CONNECTION_STRING" -f scripts/migrate_to_supabase.sql
```

### **Bước 4: Export Data từ Docker PostgreSQL** 📤

1. **Đảm bảo Docker Desktop đang chạy**
2. **Đảm bảo PostgreSQL container đang running**:
   ```powershell
   docker ps
   # Phải thấy uni_bot_postgres container
   ```

3. **Run export script**:
   ```powershell
   python scripts/export_docker_data.py
   ```

4. **Kiểm tra output**:
   - Folder `data/migration_export/` được tạo
   - Các file JSON:
     - `chunks.json` - Tất cả documents chunks
     - `embeddings.json` - Vector embeddings
     - `conversations.json` - Chat history
     - `bm25_index.json` - BM25 search index
     - `export_summary.json` - Tổng kết export

### **Bước 5: Import Data vào Supabase** 📥

1. **Replace YOUR_SUPABASE_URL** bằng connection string từ Bước 2:
   ```powershell
   python scripts/import_to_supabase.py --url "postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
   ```

2. **Chờ import hoàn tất** (có thể mất vài phút nếu data nhiều)

3. **Verify import thành công**:
   - Trong Supabase Dashboard → **Table Editor**
   - Kiểm tra các bảng: `chunks`, `embeddings`, `conversations`, `bm25_index`
   - So sánh số lượng records với `export_summary.json`

### **Bước 6: Cập Nhật Environment Variables** 🔐

**Update file `.env`**:

```env
# ============================================
# Supabase PostgreSQL Configuration (NEW)
# ============================================
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Legacy Docker config (keep for backup)
# POSTGRES_USER=uni_bot_user
# POSTGRES_PASSWORD=uni_bot_password
# POSTGRES_DB=uni_bot_db
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
```

**⚠️ QUAN TRỌNG**: 
- Replace `[YOUR-PROJECT-REF]` và `[YOUR-PASSWORD]` bằng thông tin thực
- **KHÔNG commit file `.env` lên git** (đã có trong `.gitignore`)

### **Bước 7: Update Railway Environment Variables** 🚂

Nếu bạn deploy trên Railway:

1. Vào Railway Dashboard → Your project
2. Click vào service → **Variables**
3. Update/Add:
   ```
   DATABASE_URL=postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
4. Click **Deploy** để apply changes

### **Bước 8: Test Connection** ✅

**Test local**:
```powershell
python test_postgres_connection.py
```

Expected output:
```
✅ PostgreSQL connection successful
✅ pgvector extension is installed
📊 Database Statistics:
  - Chunks: XXX
  - Embeddings: XXX
  - Conversations: XXX
```

**Test trên Railway**:
```powershell
# Check Railway logs
railway logs
```

### **Bước 9: Update Frontend Environment** 🎨

**Update `frontend/.env.local`**:

Không cần thay đổi gì vì frontend chỉ connect tới backend API, không trực tiếp connect tới database.

### **Bước 10: Restart Services** 🔄

**Local development**:
```powershell
# Stop old Docker containers (optional - keep for backup)
docker-compose down

# Start backend with new Supabase connection
uvicorn main:app --reload
```

**Railway**:
- Railway sẽ tự động restart sau khi update environment variables

## 🎯 Verification Checklist

- [ ] Supabase project created
- [ ] Connection string obtained
- [ ] Migration SQL script executed successfully
- [ ] Data exported from Docker PostgreSQL
- [ ] Data imported to Supabase
- [ ] Environment variables updated
- [ ] Connection test passed
- [ ] Backend API working
- [ ] Frontend can communicate with backend
- [ ] Chat functionality working
- [ ] Document upload working

## 🔧 Troubleshooting

### ❌ Error: "role postgres does not exist"

**Solution**: Use correct connection string từ Supabase Dashboard

### ❌ Error: "extension vector does not exist"

**Solution**: 
```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### ❌ Error: "connection refused"

**Solution**: 
1. Check internet connection
2. Verify Supabase project is running (Dashboard → Settings)
3. Check connection string format

### ❌ Error: "authentication failed"

**Solution**: 
1. Verify password in connection string
2. Reset database password in Supabase Dashboard → Settings → Database → Reset password

### ❌ Import fails with "duplicate key"

**Solution**: 
```sql
-- Clear existing data in Supabase (if this is fresh migration)
-- Run in Supabase SQL Editor
TRUNCATE TABLE bm25_index CASCADE;
TRUNCATE TABLE embeddings CASCADE;
TRUNCATE TABLE conversations CASCADE;
TRUNCATE TABLE chunks CASCADE;

-- Reset sequences
SELECT setval('chunks_id_seq', 1, false);
SELECT setval('embeddings_id_seq', 1, false);
SELECT setval('conversations_id_seq', 1, false);
SELECT setval('bm25_index_id_seq', 1, false);
```

Then run import script again.

## 📊 Supabase Dashboard Features

Sau khi migration, bạn có thể sử dụng:

1. **Table Editor** - Xem và edit data trực tiếp
2. **SQL Editor** - Run custom queries
3. **Database** - View connections, extensions, roles
4. **API Docs** - Auto-generated REST API
5. **Logs** - Query logs và errors
6. **Backups** - Daily backups (Pro plan)

## 💰 Supabase Pricing

**Free Tier** (đủ cho development):
- 500 MB database space
- 1 GB file storage
- 2 GB bandwidth
- 50 MB file uploads
- 500,000 read operations
- 100,000 write operations

**Pro Tier** ($25/month):
- 8 GB database space
- 100 GB file storage
- 250 GB bandwidth
- 5 GB file uploads
- Daily backups
- Priority support

## 🔐 Security Best Practices

1. **KHÔNG share connection string công khai**
2. **Sử dụng environment variables** cho sensitive data
3. **Enable Row Level Security (RLS)** nếu có user authentication
4. **Rotate passwords định kỳ** (mỗi 3-6 tháng)
5. **Monitor database logs** để phát hiện unauthorized access

## 📚 Resources

- [Supabase Documentation](https://supabase.com/docs)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)

## ✅ Cleanup (Optional)

Sau khi verify migration thành công và hệ thống chạy ổn định:

1. **Stop Docker containers**:
   ```powershell
   docker-compose down
   ```

2. **Remove Docker volumes** (⚠️ XÓA DỮ LIỆU VĨNH VIỄN):
   ```powershell
   docker volume rm uni_bot_postgres_data
   ```

3. **Backup export files**:
   - Keep `data/migration_export/` folder as backup
   - Hoặc compress và lưu trữ:
     ```powershell
     Compress-Archive -Path data/migration_export -DestinationPath backup_docker_data.zip
     ```

## 🎉 Done!

Bạn đã migration thành công từ Docker PostgreSQL sang Supabase! 🚀

Database của bạn giờ đã:
- ☁️ Chạy trên cloud
- 🔒 Được backup tự động
- 📈 Có thể scale dễ dàng
- 🌐 Truy cập từ mọi nơi
- 🆓 Miễn phí (Free tier)
