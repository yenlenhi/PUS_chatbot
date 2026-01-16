# Hướng Dẫn Streaming Response

## Tổng Quan

Hệ thống đã được nâng cấp để hỗ trợ **streaming response**, giúp giảm thời gian phản hồi từ ~25 giây xuống chỉ vài giây. User sẽ thấy câu trả lời hiển thị từng phần ngay lập tức thay vì phải đợi toàn bộ response hoàn tất.

## Cải Tiến

### Trước khi có Streaming
- ⏱️ **Thời gian đợi**: ~25 giây
- 😴 **Trải nghiệm**: User phải đợi lâu mới thấy câu trả lời
- 📊 **Flow**: Retrieve → Generate → Return (all at once)

### Sau khi có Streaming
- ⚡ **Thời gian phản hồi đầu tiên**: ~2-3 giây
- 😊 **Trải nghiệm**: User thấy text ngay lập tức
- 📊 **Flow**: Retrieve → Stream chunks → User sees text in real-time

## API Endpoints

### 1. Regular Endpoint (Non-streaming)
```
POST /api/v1/chat
```

**Sử dụng khi:**
- Query có kèm hình ảnh (vision queries)
- Cần response đầy đủ một lần
- Testing/debugging

**Response format:**
```json
{
  "answer": "Full answer text...",
  "sources": ["doc1.pdf", "doc2.pdf"],
  "confidence": 0.85,
  "conversation_id": "uuid-here"
}
```

### 2. Streaming Endpoint (Recommended)
```
POST /api/v1/chat/stream
```

**Sử dụng khi:**
- Query text thông thường (không có hình ảnh)
- Muốn UX tốt hơn với real-time response
- Production use

**Response format (Server-Sent Events):**
```javascript
// Event 1: Metadata
data: {"type": "metadata", "conversation_id": "uuid-here", "status": "processing"}

// Event 2: Status updates
data: {"type": "status", "message": "Đang tìm kiếm tài liệu liên quan..."}

// Event 3: Sources
data: {"type": "sources", "sources": ["doc1.pdf"], "confidence": 0.85}

// Event 4: Status update
data: {"type": "status", "message": "Đang tạo câu trả lời..."}

// Event 5-N: Answer chunks (streaming)
data: {"type": "answer_chunk", "content": "Chào bạn,\n\n"}
data: {"type": "answer_chunk", "content": "Dựa trên các tài liệu..."}
data: {"type": "answer_chunk", "content": "được cung cấp, tôi có thể..."}

// Final event: Complete metadata
data: {"type": "complete", "attachments": [...], "chart_data": [...]}

// Done signal
data: {"type": "done"}
```

## Cách Sử Dụng

### Frontend Implementation (React/Next.js)

```typescript
async function sendStreamingMessage(message: string, conversationId?: string) {
  const response = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      language: 'vi'
    })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  
  let fullAnswer = '';
  let sources = [];
  let attachments = [];
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        
        switch (data.type) {
          case 'metadata':
            console.log('Conversation ID:', data.conversation_id);
            break;
            
          case 'status':
            // Show status message to user
            showStatus(data.message);
            break;
            
          case 'sources':
            sources = data.sources;
            // Update UI with sources
            break;
            
          case 'answer_chunk':
            fullAnswer += data.content;
            // Update UI with new text chunk
            appendToAnswer(data.content);
            break;
            
          case 'complete':
            attachments = data.attachments;
            // Show attachments, charts, etc.
            break;
            
          case 'done':
            console.log('Streaming completed');
            break;
            
          case 'error':
            console.error('Error:', data.message);
            break;
        }
      }
    }
  }
}
```

### Vanilla JavaScript Implementation

```javascript
const evtSource = new EventSource('/api/v1/chat/stream?' + new URLSearchParams({
  message: 'Điều kiện xét tuyển là gì?',
  language: 'vi'
}));

let fullAnswer = '';

evtSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'answer_chunk') {
    fullAnswer += data.content;
    document.getElementById('answer').textContent = fullAnswer;
  } else if (data.type === 'done') {
    evtSource.close();
    console.log('Completed');
  }
});

evtSource.addEventListener('error', (error) => {
  console.error('EventSource error:', error);
  evtSource.close();
});
```

### Python Client Example

```python
import requests
import json

def stream_chat(message: str):
    response = requests.post(
        'http://localhost:8000/api/v1/chat/stream',
        json={'message': message, 'language': 'vi'},
        stream=True
    )
    
    full_answer = ''
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                
                if data['type'] == 'answer_chunk':
                    chunk = data['content']
                    full_answer += chunk
                    print(chunk, end='', flush=True)
                elif data['type'] == 'done':
                    print('\n--- Completed ---')
                    break
    
    return full_answer

# Usage
answer = stream_chat('Điều kiện xét tuyển của trường là gì?')
```

## Testing

### Test với cURL

```bash
# Streaming endpoint
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Điều kiện xét tuyển của trường là gì?",
    "language": "vi"
  }'
```

### Test với Postman

1. Create new POST request: `http://localhost:8000/api/v1/chat/stream`
2. Set Headers: `Content-Type: application/json`
3. Set Body (JSON):
```json
{
  "message": "Điều kiện xét tuyển là gì?",
  "language": "vi"
}
```
4. Click "Send" và xem streaming response

## Performance Comparison

| Metric | Non-Streaming | Streaming |
|--------|---------------|-----------|
| Time to First Byte (TTFB) | ~25s | ~2-3s |
| User Perception | Slow ⏱️ | Fast ⚡ |
| Backend Load | All at once | Gradual |
| Network Efficiency | Single large payload | Multiple small chunks |
| User Experience | Wait → See all | See immediately |

## Deployment Notes

### Railway Configuration

Thêm vào `railway.toml` hoặc environment variables:

```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

# Important for streaming
[deploy.env]
TIMEOUT = "300"
```

### Nginx Configuration (nếu có)

```nginx
location /api/v1/chat/stream {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;  # Important for streaming
    proxy_cache off;
    proxy_read_timeout 300s;
}
```

## Troubleshooting

### Issue: Streaming không hoạt động

**Giải pháp:**
1. Kiểm tra `X-Accel-Buffering: no` header
2. Disable proxy buffering (nginx/cloudflare)
3. Kiểm tra firewall timeout settings

### Issue: Connection bị đứt giữa chừng

**Giải pháp:**
1. Tăng timeout settings
2. Kiểm tra network stability
3. Add keep-alive chunks

### Issue: Railway deployment streaming chậm

**Giải pháp:**
1. Kiểm tra Railway region (chọn gần user)
2. Upgrade Railway plan nếu cần
3. Monitor Railway logs

## Best Practices

1. **Fallback Strategy**: Luôn có non-streaming endpoint backup
2. **Error Handling**: Handle network errors gracefully
3. **Progress Indicators**: Show status messages cho user
4. **Timeout Management**: Set reasonable timeouts
5. **Testing**: Test với slow networks
6. **Monitoring**: Log streaming performance metrics

## Kết Quả Mong Đợi

- ✅ **User thấy response ngay lập tức** (~2-3s thay vì 25s)
- ✅ **Better UX** với progressive text display
- ✅ **Same accuracy** như non-streaming
- ✅ **Production ready** trên Railway
- ✅ **Mobile friendly** với SSE support

## Next Steps

1. Update frontend để sử dụng streaming endpoint
2. Test trên môi trường staging/Railway
3. Monitor performance metrics
4. Collect user feedback
5. Fine-tune chunk sizes nếu cần
