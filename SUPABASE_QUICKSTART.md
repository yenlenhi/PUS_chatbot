# 🚀 Quick Start - Supabase Migration

Nhanh chóng migration database sang Supabase trong 10 phút!

## ⚡ Quick Steps

### 1️⃣ Tạo Supabase Project (3 phút)
- Vào [supabase.com](https://supabase.com) → New Project
- Region: **Singapore**
- Lưu lại **database password**

### 2️⃣ Setup Schema (1 phút)
```sql
-- Copy & paste vào Supabase SQL Editor
-- File: scripts/migrate_to_supabase.sql
CREATE EXTENSION IF NOT EXISTS vector;
-- (rest of SQL script...)
```

### 3️⃣ Export Data từ Docker (2 phút)
```powershell
# Đảm bảo Docker đang chạy
docker ps

# Export
python scripts/export_docker_data.py
```

### 4️⃣ Import vào Supabase (2 phút)
```powershell
python scripts/import_to_supabase.py --url "YOUR_SUPABASE_URL"
```

### 5️⃣ Update .env (1 phút)
```env
DATABASE_URL=postgresql://postgres.[REF]:[PASSWORD]@...supabase.com:6543/postgres
```

### 6️⃣ Test (1 phút)
```powershell
python test_supabase_connection.py
```

## ✅ Done!

Xem chi tiết: [SUPABASE_MIGRATION_GUIDE.md](SUPABASE_MIGRATION_GUIDE.md)

## 🆘 Quick Troubleshooting

### Connection failed?
1. Check Supabase Dashboard → Settings → Database
2. Verify password trong connection string
3. Test internet connection

### Tables missing?
Run migration SQL trong Supabase SQL Editor

### Import fails?
```sql
-- Clear và retry
TRUNCATE TABLE bm25_index, embeddings, conversations, chunks CASCADE;
```

## 📞 Need Help?

1. Check [SUPABASE_MIGRATION_GUIDE.md](SUPABASE_MIGRATION_GUIDE.md)
2. View Supabase logs: Dashboard → Logs
3. Check Railway logs: `railway logs`
