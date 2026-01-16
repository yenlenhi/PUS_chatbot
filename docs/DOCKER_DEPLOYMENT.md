# Docker Build & Deployment Guide

## 🎯 Mục đích
Pre-download embedding models vào Docker image để tránh lỗi runtime trên Railway.

## 📦 Files đã tạo/cập nhật

### 1. **Dockerfile** (MỚI)
Multi-stage build với 2 stages:
- **Stage 1 (model-downloader)**: Download models trước
  - `keepitreal/vietnamese-sbert` (primary)
  - `all-MiniLM-L6-v2` (fallback)
- **Stage 2 (runtime)**: Copy models và chạy application

### 2. **scripts/download_models.py** (MỚI)
Script để test việc download models locally trước khi build Docker.

### 3. **.dockerignore** (MỚI)
Loại bỏ files không cần thiết khỏi Docker context.

### 4. **railway.json** (CẬP NHẬT)
Chuyển từ `NIXPACKS` sang `DOCKERFILE` builder.

### 5. **src/services/embedding_service.py** (CẬP NHẬT)
- Cải thiện offline model loading
- Better cache directory handling
- Multiple fallback models
- Detailed logging

## 🚀 Cách test local

### Test 1: Download models script
```bash
python scripts/download_models.py
```

### Test 2: Build Docker image locally
```bash
# Build image
docker build -t uni-bot:test .

# Run container
docker run -p 8080:8080 --env-file .env uni-bot:test

# Test health endpoint
curl http://localhost:8080/health
```

### Test 3: Test embedding service
```bash
# Inside container
docker exec -it <container_id> python -c "
from src.services.embedding_service import EmbeddingService
import os
os.environ['HF_HUB_OFFLINE'] = '1'
svc = EmbeddingService()
emb = svc.create_embedding('Test sentence')
print(f'✅ Embedding shape: {emb.shape}')
"
```

## 📋 Deployment trên Railway

### Bước 1: Commit & Push
```bash
git add Dockerfile .dockerignore railway.json scripts/download_models.py
git add src/services/embedding_service.py
git commit -m "feat: pre-download embedding models in Docker image"
git push
```

### Bước 2: Railway sẽ tự động:
1. Detect Dockerfile
2. Build multi-stage image (download models trong stage 1)
3. Deploy stage 2 với models đã cached

### Bước 3: Verify deployment
- Check Railway logs: Models should load từ cache
- Test chat endpoint: Không có download errors

## ⚙️ Environment Variables trên Railway

Đảm bảo các biến sau được set:
```env
# Model configuration
EMBEDDING_MODEL=keepitreal/vietnamese-sbert
EMBEDDING_DIMENSION=384

# Model cache (optional, Docker đã handle)
TRANSFORMERS_CACHE=/root/.cache/huggingface
HF_HOME=/root/.cache/huggingface

# Offline mode (optional)
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

## 🔍 Troubleshooting

### Lỗi: "Model not found"
- **Nguyên nhân**: Model không được download trong build stage
- **Giải pháp**: Check Railway build logs, verify stage 1 thành công

### Lỗi: "Permission denied"
- **Nguyên nhân**: Cache directory không có quyền write
- **Giải pháp**: Dockerfile đã set permissions, check logs

### Build timeout trên Railway
- **Nguyên nhân**: Download models quá lâu
- **Giải pháp**: Railway Pro plan có build timeout cao hơn

## 📊 Kích thước Image

Ước tính:
- Base image: ~500MB
- keepitreal/vietnamese-sbert: ~300MB
- all-MiniLM-L6-v2: ~90MB
- Application code: ~50MB
- **Total**: ~940MB (acceptable cho Railway)

## ✅ Lợi ích

1. **Không cần download runtime**: Models đã có trong image
2. **Faster startup**: Không đợi download
3. **Offline deployment**: Không phụ thuộc HuggingFace Hub
4. **Predictable performance**: Không bị network issues
5. **Better caching**: Railway cache Docker layers

## 🎓 Best Practices

1. **Multi-stage build**: Giảm kích thước final image
2. **Layer caching**: Requirements trước, code sau
3. **Health checks**: Railway tự động restart nếu unhealthy
4. **Offline mode**: Set `HF_HUB_OFFLINE=1` để force offline
5. **Fallback models**: Luôn có backup model
