# 🐘 PostgreSQL + pgvector Setup Guide

Hướng dẫn chi tiết để setup PostgreSQL với pgvector extension cho Uni Bot.

## 📋 Yêu Cầu Tiên Quyết

- Docker & Docker Compose đã cài đặt
- Git Bash (cho Windows)
- Python 3.11+
- Conda environment `uni_bot` đã được tạo

## 🚀 Bước 1: Chuẩn Bị Môi Trường

### 1.1 Cập nhật `.env` file

Copy từ `.env.example` và cập nhật các giá trị:

```bash
cp .env.example .env
```

Chỉnh sửa `.env` với các giá trị của bạn:

```env
# PostgreSQL
POSTGRES_USER=uni_bot_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=uni_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://uni_bot_user:your_secure_password@localhost:5432/uni_bot_db

# pgAdmin (optional)
PGADMIN_EMAIL=your_email@example.com
PGADMIN_PASSWORD=your_pgadmin_password
```

### 1.2 Cập nhật `.env` file chính

Cập nhật file `.env` hiện tại với PostgreSQL connection:

```env
# Thêm vào .env
DATABASE_URL=postgresql://uni_bot_user:your_secure_password@localhost:5432/uni_bot_db
```

## 🐳 Bước 2: Khởi Động Docker Containers

### 2.1 Khởi động PostgreSQL + pgvector

Sử dụng Git Bash:

```bash
# Từ thư mục gốc của dự án
docker-compose up -d
```

Kiểm tra status:

```bash
docker-compose ps
```

Bạn sẽ thấy:
- `uni_bot_postgres` - PostgreSQL container (HEALTHY)
- `uni_bot_pgadmin` - pgAdmin container (optional)

### 2.2 Xác Minh PostgreSQL Đang Chạy

```bash
# Kiểm tra logs
docker-compose logs postgres

# Kết nối tới database
docker exec -it uni_bot_postgres psql -U uni_bot_user -d uni_bot_db
```

Nếu thành công, bạn sẽ thấy prompt `uni_bot_db=#`

### 2.3 Kiểm Tra pgvector Extension

Trong PostgreSQL prompt:

```sql
-- Kiểm tra pgvector đã được cài đặt
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Kiểm tra các bảng đã được tạo
\dt

-- Thoát
\q
```

## 🔧 Bước 3: Cập Nhật Python Dependencies

### 3.1 Cài đặt các package mới

Kích hoạt conda environment:

```bash
conda activate uni_bot
```

Cập nhật requirements.txt:

```bash
pip install -r requirements.txt
```

Các package mới sẽ được cài đặt:
- `sqlalchemy` - ORM
- `psycopg2-binary` - PostgreSQL driver
- `sqlmodel` - SQL + Pydantic models
- `pgvector` - pgvector support

### 3.2 Xác Minh Cài Đặt

```bash
powershell python -c "import sqlalchemy; import psycopg2; import pgvector; print('All packages installed successfully!')"
```

## 📊 Bước 4: Kiểm Tra Kết Nối Database

### 4.1 Test Connection Script

Tạo file `test_postgres_connection.py`:

```python
import os
from sqlalchemy import create_engine, text

# Lấy connection string từ .env
db_url = os.getenv("DATABASE_URL", "postgresql://uni_bot_user:uni_bot_password@localhost:5432/uni_bot_db")

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("✅ PostgreSQL Connection Successful!")
        print(f"Version: {result.fetchone()[0]}")
        
        # Kiểm tra pgvector
        result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
        if result.fetchone():
            print("✅ pgvector Extension Installed!")
        else:
            print("❌ pgvector Extension NOT Found!")
            
except Exception as e:
    print(f"❌ Connection Failed: {e}")
```

Chạy test:

```bash
powershell python test_postgres_connection.py
```

## 🎯 Bước 5: Xem Dữ Liệu (Optional)

### 5.1 Sử dụng pgAdmin

Mở browser: `http://localhost:5050`

Đăng nhập:
- Email: `admin@example.com` (hoặc giá trị PGADMIN_EMAIL)
- Password: `admin` (hoặc giá trị PGADMIN_PASSWORD)

Thêm server:
- Host: `postgres`
- Port: `5432`
- Username: `uni_bot_user`
- Password: `uni_bot_password`

### 5.2 Sử dụng Command Line

```bash
# Kết nối tới database
docker exec -it uni_bot_postgres psql -U uni_bot_user -d uni_bot_db

# Xem các bảng
\dt

# Xem schema của chunks table
\d chunks

# Xem số lượng chunks
SELECT COUNT(*) FROM chunks;

# Thoát
\q
```

## 🛑 Bước 6: Dừng Containers (Khi Cần)

```bash
# Dừng containers nhưng giữ data
docker-compose stop

# Dừng và xóa containers (data vẫn được lưu)
docker-compose down

# Dừng, xóa containers và xóa volumes (XÓA TẤT CẢ DỮ LIỆU)
docker-compose down -v
```

## 🔄 Bước 7: Tiếp Theo

Sau khi PostgreSQL + pgvector đã setup thành công:

1. ✅ Cập nhật `config/settings.py` với PostgreSQL connection
2. ✅ Tạo PostgreSQL Database Service
3. ✅ Tạo Hybrid Retrieval Service
4. ✅ Tạo Ingestion Service
5. ✅ Cập nhật RAG Service

## 🆘 Troubleshooting

### PostgreSQL không khởi động

```bash
# Xem logs
docker-compose logs postgres

# Xóa container và volume, khởi động lại
docker-compose down -v
docker-compose up -d
```

### Kết nối bị từ chối

- Kiểm tra `.env` file có đúng credentials không
- Kiểm tra PostgreSQL container đang chạy: `docker-compose ps`
- Kiểm tra port 5432 không bị chiếm dụng

### pgvector extension không tìm thấy

```bash
# Kết nối tới database
docker exec -it uni_bot_postgres psql -U uni_bot_user -d uni_bot_db

# Cài đặt extension
CREATE EXTENSION IF NOT EXISTS vector;

# Kiểm tra
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## 📚 Tài Liệu Tham Khảo

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

