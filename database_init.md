# Database Initialization Guide - Hướng dẫn Khởi tạo Database

## 📋 Tổng quan

Hướng dẫn này sẽ chỉ bạn cách khởi tạo, reset và quản lý database cho hệ thống RAG chatbot với enhanced chunking strategy.

## 🗂️ Cấu trúc Database

### Database Schema
Database sử dụng SQLite với 2 bảng chính:

#### 1. Bảng `chunks` (Lưu trữ các đoạn văn bản)
```sql
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,                    -- Nội dung chunk
    source_file TEXT NOT NULL,               -- File PDF nguồn
    page_number INTEGER,                     -- Số trang (nếu có)
    chunk_index INTEGER NOT NULL,           -- Thứ tự chunk trong document
    
    -- Enhanced metadata fields (mới)
    heading_text TEXT,                       -- Text của heading
    heading_level INTEGER,                   -- Cấp độ heading (1, 2, 3...)
    heading_number TEXT,                     -- Số heading (vd: "7.3.1")
    parent_heading TEXT,                     -- Heading cha (vd: "7.3" cho "7.3.1")
    is_sub_chunk BOOLEAN DEFAULT FALSE,     -- Có phải sub-chunk không
    sub_chunk_index INTEGER,                -- Thứ tự trong sub-chunks
    total_sub_chunks INTEGER,               -- Tổng số sub-chunks
    chunk_type TEXT DEFAULT 'content',      -- Loại chunk: intro/heading/content
    word_count INTEGER,                     -- Số từ
    char_count INTEGER,                     -- Số ký tự
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Bảng `embeddings` (Lưu trữ vector embeddings)
```sql
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,              -- Liên kết với chunks.id
    embedding BLOB NOT NULL,                -- Vector embedding (768 dimensions)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks (id)
);
```

### Files được tạo
- **Database**: `data/embeddings/chatbot.db`
- **FAISS Index**: `data/embeddings/faiss_index.index`
- **FAISS Metadata**: `data/embeddings/faiss_index.metadata`
- **Chunks JSON**: `data/processed/heading_chunks.json`
- **Analysis**: `data/processed/chunk_analysis_production.json`

## 🚀 Cách khởi tạo Database

### Phương pháp 1: Khởi tạo từ đầu (Khuyến nghị)

```bash
# Kích hoạt conda environment
conda activate uni_bot

# Reset và rebuild hoàn toàn
python scripts/reset_and_rebuild.py
```

**Quá trình thực hiện:**
1. **Backup** dữ liệu hiện tại (nếu có)
2. **Xóa** database, FAISS index, chunks files cũ
3. **Tạo** database mới với enhanced schema
4. **Xử lý** tất cả PDF files với enhanced chunking
5. **Tạo** embeddings cho tất cả chunks
6. **Xây dựng** FAISS index mới
7. **Phân tích** và lưu kết quả

### Phương pháp 2: Reset đơn giản

```bash
# Chỉ xóa database và FAISS index
python scripts/reset_database.py

# Sau đó rebuild
python scripts/process_pdfs_with_headings.py
```

### Phương pháp 3: Migration từ schema cũ

```bash
# Nếu đã có database cũ, migrate schema
python scripts/migrate_database_schema.py

# Sau đó deploy chunking mới
python scripts/deploy_new_chunking.py
```

## 🔧 Scripts và chức năng

### 1. `reset_and_rebuild.py` - Reset và rebuild hoàn toàn
**Chức năng:**
- Backup dữ liệu hiện tại
- Xóa toàn bộ database, FAISS index, files
- Tạo lại từ đầu với enhanced chunking
- Tự động phân tích kết quả

**Khi nào sử dụng:**
- Lần đầu setup
- Muốn làm sạch hoàn toàn
- Thay đổi chunking strategy
- Có vấn đề với dữ liệu

### 2. `migrate_database_schema.py` - Migration schema
**Chức năng:**
- Thêm các cột metadata mới vào bảng chunks
- Cập nhật metadata cho chunks hiện có
- Backup trước khi migration

**Khi nào sử dụng:**
- Đã có database cũ
- Muốn giữ lại dữ liệu hiện có
- Upgrade schema

### 3. `deploy_new_chunking.py` - Deploy chunking mới
**Chức năng:**
- Backup dữ liệu
- Xóa chunks và embeddings cũ
- Xử lý lại PDFs với enhanced chunking
- Tạo embeddings và FAISS index mới

**Khi nào sử dụng:**
- Sau khi migrate schema
- Muốn áp dụng chunking mới
- Database schema đã sẵn sàng

### 4. `analyze_chunks.py` - Phân tích chất lượng
**Chức năng:**
- Phân tích kích thước chunks
- Thống kê phân bố
- Đưa ra khuyến nghị
- Tìm chunks có vấn đề

**Khi nào sử dụng:**
- Sau khi tạo chunks
- Kiểm tra chất lượng
- Tối ưu hóa parameters

### 5. `test_new_chunking.py` - Test chunking strategy
**Chức năng:**
- Test chunking mới trên PDFs
- So sánh với chunking cũ
- Lưu kết quả test
- Đánh giá hiệu suất

**Khi nào sử dụng:**
- Trước khi deploy
- Test thay đổi parameters
- So sánh strategies

## 📊 Enhanced Chunking Strategy

### Nguyên tắc chunking mới:
1. **Bảo toàn hoàn toàn nội dung** - Không bỏ sót bất kỳ thông tin nào
2. **Chia theo heading hierarchy** - Tôn trọng cấu trúc tài liệu
3. **Merge chunks nhỏ thông minh** - Tránh mất ngữ cảnh
4. **Metadata phong phú** - Hỗ trợ retrieval chính xác

### Parameters tối ưu:
- `min_chunk_size`: 100 characters
- `max_chunk_size`: 2500 characters  
- `target_chunk_size`: 1000 characters

### Loại chunks:
- **intro**: Phần giới thiệu trước heading đầu tiên
- **heading**: Chunks chứa heading và nội dung
- **content**: Chunks nội dung thông thường

## 🔍 Kiểm tra và xác minh

### Kiểm tra database
```bash
# Xem thông tin chunks
python -c "
from src.services.database_service import DatabaseService
db = DatabaseService()
print(f'Total chunks: {db.get_chunk_count()}')
"

# Phân tích chất lượng
python scripts/analyze_chunks.py
```

### Kiểm tra FAISS index
```bash
# Test FAISS index
python -c "
from src.services.faiss_service import FAISSService
faiss = FAISSService()
if faiss.load_index():
    print(f'FAISS index loaded: {faiss.index.ntotal} vectors')
else:
    print('Failed to load FAISS index')
"
```

### Kiểm tra files
```bash
# Kiểm tra files được tạo
ls -la data/embeddings/
ls -la data/processed/
```

## 🚨 Xử lý sự cố

### Lỗi "table chunks has no column named heading_text"
**Nguyên nhân:** Database schema cũ chưa có metadata columns
**Giải pháp:**
```bash
python scripts/migrate_database_schema.py
```

### Lỗi "No PDF files found"
**Nguyên nhân:** Không có file PDF trong thư mục `data/pdfs/`
**Giải pháp:**
- Copy file PDF vào `data/pdfs/`
- Kiểm tra đường dẫn trong `config/settings.py`

### Lỗi "Failed to load FAISS index"
**Nguyên nhân:** FAISS index bị lỗi hoặc chưa tạo
**Giải pháp:**
```bash
python scripts/reset_and_rebuild.py
```

### Lỗi embedding model
**Nguyên nhân:** Model chưa download hoặc lỗi mạng
**Giải pháp:**
- Kiểm tra kết nối internet
- Thử lại sau vài phút
- Thay đổi model trong `config/settings.py`

## 📁 Backup và Recovery

### Tự động backup
Tất cả scripts đều tự động tạo backup trước khi thay đổi:
- `data/processed/backup/database_backup_YYYYMMDD_HHMMSS.db`
- `data/processed/backup/chunks_backup_YYYYMMDD_HHMMSS.json`
- `data/embeddings/backup/database_pre_migration_YYYYMMDD_HHMMSS.db`

### Khôi phục từ backup
```bash
# Khôi phục database
cp data/processed/backup/database_backup_YYYYMMDD_HHMMSS.db data/embeddings/chatbot.db

# Khôi phục chunks
cp data/processed/backup/chunks_backup_YYYYMMDD_HHMMSS.json data/processed/heading_chunks.json
```

## 🎯 Best Practices

### 1. Luôn backup trước khi thay đổi
```bash
# Tạo backup thủ công
cp data/embeddings/chatbot.db data/embeddings/chatbot_backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. Kiểm tra kết quả sau mỗi lần rebuild
```bash
python scripts/analyze_chunks.py
```

### 3. Test trước khi deploy production
```bash
python scripts/test_new_chunking.py
```

### 4. Monitor chất lượng chunks
- Kiểm tra tỷ lệ chunks trong khoảng tối ưu (500-3000 chars)
- Đảm bảo ít chunks quá nhỏ (<100 chars) hoặc quá lớn (>3000 chars)
- Xem xét metadata completeness

### 5. Cập nhật khi có PDF mới
```bash
# Thêm PDF mới vào data/pdfs/ rồi chạy
python scripts/reset_and_rebuild.py
```

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra logs trong `logs/chatbot.log`
2. Chạy `python scripts/analyze_chunks.py` để kiểm tra dữ liệu
3. Thử reset hoàn toàn: `python scripts/reset_and_rebuild.py`
4. Kiểm tra conda environment: `conda activate uni_bot`
