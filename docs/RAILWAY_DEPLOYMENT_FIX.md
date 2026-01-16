# 🚂 Railway Deployment - Fix Embedding Model Loading

## 🔴 Vấn đề gặp phải
```
TimeoutError: The read operation timed out
ERROR: failed to build - torch download timeout (670MB CUDA version)
```

## ✅ Giải pháp đã implement

### Option 1: Lightweight Build (KHUYẾN NGHỊ - ĐÃ ACTIVE)
**File**: `Dockerfile.lightweight`
**Cách hoạt động**:
- Build nhanh (~3-5 phút)
- Models download lần đầu khởi động (~2-3 phút)
- Models được cache trong Railway volume
- Lần khởi động sau load từ cache (~10 giây)

**Ưu điểm**:
- ✅ Build rất nhanh, không timeout
- ✅ Sử dụng cache của Railway hiệu quả
- ✅ Tiết kiệm tài nguyên build

**Nhược điểm**:
- ⚠️ First startup chậm hơn (download models)

### Option 2: Pre-download Build (BACKUP)
**File**: `Dockerfile`
**Cách hoạt động**:
- Pre-download models trong build stage
- Dùng torch CPU-only (100MB thay vì 670MB)
- Models baked vào Docker image

**Ưu điểm**:
- ✅ Startup nhanh ngay lần đầu
- ✅ Offline deployment
- ✅ Predictable performance

**Nhược điểm**:
- ⚠️ Build lâu hơn (5-10 phút)
- ⚠️ Image size lớn hơn (~1.2GB)

## 🚀 Deploy ngay (Option 1 - Lightweight)

```bash
# Đã config sẵn trong railway.json
git add .
git commit -m "fix: use lightweight Dockerfile to avoid build timeout"
git push
```

Railway sẽ:
1. ✅ Build nhanh với Dockerfile.lightweight
2. ✅ Deploy thành công
3. ⏳ First startup: Download models (~2-3 phút)
4. ✅ Lần sau: Load từ cache (~10 giây)

## 🔄 Chuyển sang Option 2 (nếu cần)

Sửa `railway.json`:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"  // Thay vì Dockerfile.lightweight
  }
}
```

## 📊 So sánh chi tiết

| Metric | Lightweight | Pre-download |
|--------|-------------|--------------|
| Build time | 3-5 phút ⚡ | 5-10 phút 🐌 |
| Image size | ~800MB | ~1.2GB |
| First startup | 2-3 phút (download) | 30 giây ⚡ |
| Next startup | 10 giây ⚡ | 10 giây ⚡ |
| Railway cache | Sử dụng tốt ✅ | Không cần cache |
| Build reliability | Cao ✅ | Trung bình ⚠️ |

## 🔧 Environment Variables cần thiết trên Railway

```env
# Model configuration
EMBEDDING_MODEL=keepitreal/vietnamese-sbert
EMBEDDING_DIMENSION=384

# Model cache paths (auto-handled)
TRANSFORMERS_CACHE=/root/.cache/huggingface
HF_HOME=/root/.cache/huggingface
```

## 📝 Logs mong đợi

### First Startup (Lightweight):
```
🤖 Loading embedding model: keepitreal/vietnamese-sbert
📍 Using device: cpu
📁 Cache directory: /root/.cache/huggingface
📥 Downloading model from HuggingFace... (~2 minutes)
✅ Embedding model loaded successfully
   📊 Embedding dimension: 384
```

### Subsequent Startups:
```
🤖 Loading embedding model: keepitreal/vietnamese-sbert
📍 Using device: cpu
📁 Cache directory: /root/.cache/huggingface
✅ Embedding model loaded successfully (from cache)
   📊 Embedding dimension: 384
```

## 🎯 Recommendation

**Dùng Dockerfile.lightweight** (đã active):
- ✅ Build không bao giờ timeout
- ✅ Railway caching works perfectly
- ✅ Cost-effective
- ⚠️ First startup hơi chậm nhưng chấp nhận được

## 🆘 Troubleshooting

### Lỗi: Still timeout with lightweight
```bash
# Increase timeout in requirements install
# Already done in Dockerfile.lightweight:
PIP_DEFAULT_TIMEOUT=300
```

### Lỗi: Model not found after restart
```bash
# Check Railway volume persistence
# Models should persist in /root/.cache/huggingface
```

### Lỗi: Out of memory during model load
```bash
# Use smaller model in .env:
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```
