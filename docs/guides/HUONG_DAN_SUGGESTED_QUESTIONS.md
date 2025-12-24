# Hướng Dẫn Sử Dụng Suggested Questions (Câu Hỏi Đề Xuất)

## 🎯 Tổng Quan

Hệ thống **Suggested Questions** tự động đề xuất các câu hỏi phổ biến dựa trên **chủ đề đang trending** (xu hướng) trong 24 giờ qua. Câu hỏi được cập nhật mỗi giờ để phản ánh chính xác nhu cầu người dùng hiện tại.

## 🚀 Khởi Động Hệ Thống

### 1. Khởi động Backend (Python)

```bash
cd c:\TruongVanKhai\Project\uni_bot

# Kích hoạt môi trường conda
conda activate uni_bot

# Chạy server
python main.py
```

Server sẽ chạy tại: `http://localhost:8000`

### 2. Khởi động Frontend (Next.js)

```bash
cd frontend

# Cài đặt dependencies (nếu chưa)
npm install

# Chạy development server
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

## 📡 Sử Dụng API

### Endpoint: GET /api/analytics/suggested-questions

#### Parameters

| Tham số | Kiểu | Mặc định | Mô tả |
|---------|------|----------|-------|
| `limit` | integer | 5 | Số lượng câu hỏi trả về (1-10) |
| `force_refresh` | boolean | false | Bắt buộc làm mới cache |

#### Ví dụ Request

```bash
# Lấy 5 câu hỏi (mặc định)
curl http://localhost:8000/api/analytics/suggested-questions

# Lấy 3 câu hỏi
curl http://localhost:8000/api/analytics/suggested-questions?limit=3

# Làm mới cache (bypass cache)
curl http://localhost:8000/api/analytics/suggested-questions?force_refresh=true
```

#### Response Format

```json
{
  "success": true,
  "questions": [
    {
      "question": "Điều kiện tuyển sinh năm 2025 như thế nào?",
      "count": 156,
      "last_asked": "2025-12-07 10:30:00"
    },
    {
      "question": "Học phí của trường là bao nhiêu?",
      "count": 142,
      "last_asked": "2025-12-07 09:15:00"
    }
  ],
  "count": 5,
  "cached": true,
  "cache_age_seconds": 1800
}
```

#### Response Fields

| Field | Kiểu | Mô tả |
|-------|------|-------|
| `success` | boolean | Trạng thái request |
| `questions` | array | Danh sách câu hỏi đề xuất |
| `questions[].question` | string | Nội dung câu hỏi |
| `questions[].count` | integer | Số lần được hỏi |
| `questions[].last_asked` | string | Thời gian hỏi gần nhất |
| `count` | integer | Tổng số câu hỏi |
| `cached` | boolean | Dữ liệu từ cache hay không |
| `cache_age_seconds` | integer | Tuổi của cache (giây) |

## 🖥️ Sử Dụng Trên Frontend

### Tự động (Tích hợp sẵn)

Khi truy cập `http://localhost:3000/chat-bot`, các câu hỏi đề xuất sẽ:

1. **Tự động load** khi trang được mở
2. **Hiển thị loading skeleton** trong khi đang tải
3. **Render các nút câu hỏi** khi load xong
4. **Click vào câu hỏi** → tự động điền vào ô input

### Tùy chỉnh trong Code

```typescript
// Trong component React
const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);

useEffect(() => {
  const fetchSuggestions = async () => {
    const response = await fetch('/api/analytics/suggested-questions?limit=5');
    const data = await response.json();
    
    if (data.success) {
      const questions = data.questions.map(q => q.question);
      setSuggestedQuestions(questions);
    }
  };
  
  fetchSuggestions();
}, []);
```

## 🧪 Testing

### Test Script Tự động

```bash
# Chạy test script
python test_suggested_questions.py
```

Script sẽ test:
- ✅ Basic request (limit=5)
- ✅ Different limit (limit=3)
- ✅ Force refresh (force_refresh=true)
- ✅ Cache behavior (second request)

### Test Thủ công

#### 1. Test Backend

```bash
# Test endpoint với curl
curl http://localhost:8000/api/analytics/suggested-questions?limit=5

# Kiểm tra cache
curl http://localhost:8000/api/analytics/suggested-questions
# → cached: true

# Force refresh
curl http://localhost:8000/api/analytics/suggested-questions?force_refresh=true
# → cached: false, cache_age_seconds: 0
```

#### 2. Test Frontend

1. Mở `http://localhost:3000/chat-bot`
2. Chờ loading skeleton (5 thanh xám nhấp nháy)
3. Kiểm tra 5 câu hỏi hiển thị
4. Click một câu hỏi → kiểm tra ô input
5. Mở DevTools → Console → xem API call logs
6. Refresh trang → loading nhanh hơn (cache)

#### 3. Test Python Code

```python
from src.services.analytics_service import AnalyticsService

# Khởi tạo service
svc = AnalyticsService()

# Test trending topics
topics = svc.get_trending_topics(hours_lookback=24)
print(f"Có {len(topics)} trending topics:")
for topic in topics[:5]:
    print(f"  - {topic['topic']}: {topic['trending_score']} points")

# Test suggested questions
questions = svc.get_suggested_questions(limit=5)
print(f"\nCó {len(questions)} suggested questions:")
for q in questions:
    print(f"  - {q.question} ({q.count} lần)")
```

## 📊 Giám Sát & Logs

### Log Messages Quan Trọng

#### Backend Logs

```
📈 Analyzed 15 trending topics
✅ Generated 5 suggested questions from trending topics: ['tuyen_sinh', 'hoc_phi', 'ktx']
📦 Returning cached suggested questions
🔄 Fetching fresh suggested questions (cache miss or expired)
⚠️ Only found 3 questions, adding fallback
⚠️ No trending topics found, using fallback questions
```

### Monitoring Checklist

- [ ] API response time < 500ms (cached)
- [ ] API response time < 2s (uncached)
- [ ] Cache hit rate > 80%
- [ ] Questions updated every hour
- [ ] No 500 errors in logs
- [ ] Frontend shows loading state
- [ ] Questions clickable and functional

## 🔧 Troubleshooting

### Vấn đề: API trả về câu hỏi fallback (mẫu)

**Nguyên nhân:**
- Chưa có dữ liệu trong bảng `topic_classifications`
- Không có conversations trong 7 ngày qua

**Giải pháp:**
1. Kiểm tra bảng `topic_classifications`:
```sql
SELECT COUNT(*) FROM topic_classifications;
SELECT topic, COUNT(*) FROM topic_classifications 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY topic;
```

2. Kiểm tra tracking có hoạt động:
```python
# Trong code tracking
analytics_service.classify_and_log_topic(
    conversation_id=conv_id,
    query=user_query
)
```

### Vấn đề: Frontend không load suggestions

**Nguyên nhân:**
- Backend chưa chạy
- CORS issue
- API endpoint sai

**Giải pháp:**
1. Kiểm tra backend: `http://localhost:8000/docs`
2. Kiểm tra console browser (F12)
3. Test API với curl:
```bash
curl http://localhost:8000/api/analytics/suggested-questions
```

### Vấn đề: Cache không hoạt động

**Nguyên nhân:**
- Server restart → cache bị xóa (in-memory)
- Force refresh được bật

**Giải pháp:**
1. Kiểm tra response field `cached`:
```bash
curl http://localhost:8000/api/analytics/suggested-questions | jq '.cached'
```

2. Kiểm tra cache age:
```bash
curl http://localhost:8000/api/analytics/suggested-questions | jq '.cache_age_seconds'
```

3. Nếu cần cache persistent → chuyển sang Redis:
```python
# Trong routes.py, thay thế _suggested_questions_cache
# bằng Redis client
```

### Vấn đề: Questions không liên quan

**Nguyên nhân:**
- Topic classification không chính xác
- Thiếu dữ liệu trong timeframe

**Giải pháp:**
1. Kiểm tra topic classification accuracy:
```sql
SELECT 
    topic,
    AVG(confidence) as avg_confidence,
    COUNT(*) as count
FROM topic_classifications
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY topic
ORDER BY count DESC;
```

2. Điều chỉnh timeframe trong code:
```python
# Trong analytics_service.py
def get_trending_topics(self, hours_lookback: int = 48):  # Tăng từ 24 lên 48
    ...
```

## ⚙️ Cấu Hình

### Backend Configuration

**File: `src/services/analytics_service.py`**

```python
# Timeframe phân tích trending
hours_lookback = 24  # 24 giờ

# Số câu hỏi tối đa
limit = 5

# Độ dài câu hỏi tối thiểu (filter spam)
min_question_length = 10
```

**File: `src/api/routes.py`**

```python
# Cache TTL (Time To Live)
_suggested_questions_cache = {
    "ttl": 3600  # 1 giờ = 3600 giây
}

# Số câu hỏi cache tối đa
limit=10  # Trong endpoint function
```

### Frontend Configuration

**File: `frontend/src/app/chat-bot/page.tsx`**

```typescript
// Số câu hỏi fetch từ API
const response = await fetch('/api/analytics/suggested-questions?limit=5');

// Fallback questions (khi API lỗi)
const fallbackQuestions = [
  "Điều kiện tuyển sinh...",
  "Quy chế đào tạo...",
  // ...
];
```

## 📈 Best Practices

### 1. Cache Management

- **Mặc định:** Sử dụng cache (hiệu suất cao)
- **Admin refresh:** Dùng `force_refresh=true` để test
- **Production:** Cache 1 giờ là tối ưu
- **High traffic:** Tăng TTL lên 2-3 giờ

### 2. Error Handling

- **Luôn có fallback:** Frontend không bao giờ empty
- **Log errors:** Theo dõi API failures
- **Graceful degradation:** Fallback → Sample questions

### 3. Data Quality

- **Topic tracking:** Đảm bảo classify đúng
- **Regular cleanup:** Xóa dữ liệu cũ >90 ngày
- **Monitor confidence:** AVG confidence > 0.5

### 4. Performance

- **Index database:** `topic`, `created_at` columns
- **Limit queries:** Không query quá nhiều rows
- **Cache results:** 1 giờ TTL cho balance

## 📚 Tài Liệu Liên Quan

- **Implementation Details:** `SUGGESTED_QUESTIONS_IMPLEMENTATION.md`
- **API Documentation:** `http://localhost:8000/docs`
- **Database Schema:** `database_init.md`
- **Testing Guide:** `test_suggested_questions.py`

## 🆘 Hỗ Trợ

Nếu gặp vấn đề:

1. Kiểm tra logs: `logs/app.log`
2. Test endpoint: `curl http://localhost:8000/api/analytics/suggested-questions`
3. Kiểm tra database: Xem queries trong logs
4. Force refresh: Thử `force_refresh=true`
5. Restart services: Backend + Frontend

---

**Phiên bản:** 1.0  
**Ngày cập nhật:** 7/12/2025  
**Tác giả:** PSU ChatBot Team
