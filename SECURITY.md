# Hướng Dẫn Bảo Mật Hệ Thống University Chatbot

## Tổng Quan

Hệ thống University Chatbot đã được tích hợp các tính năng bảo mật theo tiêu chuẩn:

1. **HTTPS/TLS 1.2+**: Mã hóa dữ liệu truyền tải
2. **JWT Authentication**: Xác thực người dùng
3. **Checksum Verification**: Kiểm tra toàn vẹn dữ liệu
4. **Security Headers**: Bảo vệ khỏi các tấn công web phổ biến

---

## 1. HTTPS và TLS 1.2+

### Cấu hình

Thêm vào file `.env`:

```env
# Bật HTTPS enforcement
HTTPS_ONLY=true

# Phiên bản TLS tối thiểu
TLS_MIN_VERSION=1.2
```

### Chạy với HTTPS

#### Sử dụng Self-Signed Certificate (Development)

```bash
# Tạo certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Chạy server với HTTPS
uvicorn main:app --host 0.0.0.0 --port 8443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

#### Sử dụng với Reverse Proxy (Production)

Cấu hình Nginx với Let's Encrypt:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Host $host;
    }
}
```

### Middleware Tự Động

- **HTTPSRedirectMiddleware**: Tự động redirect HTTP → HTTPS
- **SecurityHeadersMiddleware**: Thêm các security headers:
  - `Strict-Transport-Security`: Force HTTPS
  - `X-Content-Type-Options`: Ngăn MIME sniffing
  - `X-Frame-Options`: Chống clickjacking
  - `Content-Security-Policy`: Giới hạn nguồn tài nguyên

---

## 2. JWT Authentication

### Cấu hình

```env
# Secret key (sử dụng key mạnh trong production)
JWT_SECRET_KEY=your-super-secret-key-min-32-characters

# Thuật toán mã hóa
JWT_ALGORITHM=HS256

# Thời gian hết hạn token (phút)
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Tạo Secret Key An Toàn

```bash
# Sử dụng OpenSSL
openssl rand -hex 32

# Hoặc Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Đăng Nhập và Lấy Token

#### Endpoint 1: OAuth2 Form (cho Swagger UI)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

#### Endpoint 2: JSON Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Sử Dụng Token

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào"}'
```

### Tài Khoản Mặc Định

| Username | Password  | Scopes      |
|----------|-----------|-------------|
| admin    | admin123  | admin, user |
| user     | user123   | user        |

⚠️ **Thay đổi mật khẩu trong production!**

### Bảo Vệ Endpoints

Thêm dependency `get_current_user` vào các endpoints cần bảo vệ:

```python
from src.auth.jwt_handler import get_current_user

@router.post("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    # Xử lý logic
```

### Kiểm tra Quyền (Scopes)

```python
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user is None or "admin" not in current_user.scopes:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.delete("/admin/delete-document")
async def delete_document(
    admin_user: User = Depends(require_admin)
):
    # Chỉ admin mới có thể truy cập
    pass
```

---

## 3. Checksum Verification (Data Integrity)

### Cấu hình

```env
# Bật checksum verification
ENABLE_CHECKSUM_VERIFICATION=true

# Thuật toán (md5 hoặc sha256)
CHECKSUM_ALGORITHM=sha256
```

### Tính Checksum cho File Upload

#### Python Client

```python
import hashlib
import requests

def calculate_checksum(file_path, algorithm="sha256"):
    hasher = hashlib.sha256() if algorithm == "sha256" else hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# Upload file với checksum
file_path = "document.pdf"
checksum = calculate_checksum(file_path)

with open(file_path, "rb") as f:
    files = {"file": f}
    headers = {
        "X-Checksum": checksum,
        "X-Checksum-Algorithm": "sha256"
    }
    response = requests.post(
        "http://localhost:8000/api/v1/admin/upload",
        files=files,
        headers=headers
    )
```

#### cURL Example

```bash
# Tính checksum
CHECKSUM=$(sha256sum document.pdf | awk '{print $1}')

# Upload với checksum header
curl -X POST "http://localhost:8000/api/v1/admin/upload" \
  -H "X-Checksum: $CHECKSUM" \
  -H "X-Checksum-Algorithm: sha256" \
  -F "file=@document.pdf"
```

### Utility Functions

```python
from src.utils.checksum import (
    calculate_checksum,
    verify_checksum,
    calculate_file_checksum,
    verify_file_checksum
)

# Tính checksum cho string/bytes
checksum = calculate_checksum("Hello World", algorithm="sha256")

# Verify checksum
is_valid = verify_checksum("Hello World", expected_checksum, "sha256")

# Tính checksum cho file
file_checksum = calculate_file_checksum("document.pdf", "sha256")

# Verify file checksum
is_file_valid = verify_file_checksum("document.pdf", expected_checksum, "sha256")
```

---

## 4. CORS Configuration

### Cấu hình Origins

```env
# Development - cho phép mọi origin
ALLOWED_ORIGINS=*

# Production - chỉ định origins cụ thể
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## 5. Testing Security Features

### Test HTTPS Redirect

```bash
# Request HTTP khi HTTPS_ONLY=true
curl -L http://localhost:8000/api/v1/health
# Sẽ redirect tới https://localhost:8000/api/v1/health
```

### Test JWT Authentication

```bash
# Request không token
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
# → 401 Unauthorized (nếu endpoint được bảo vệ)

# Request với token hợp lệ
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
# → 200 OK
```

### Test Checksum Verification

```bash
# Upload với checksum sai
curl -X POST "http://localhost:8000/api/v1/admin/upload" \
  -H "X-Checksum: wrong_checksum" \
  -H "X-Checksum-Algorithm: sha256" \
  -F "file=@document.pdf"
# → 400 Bad Request: Checksum verification failed
```

---

## 6. Production Deployment Checklist

- [ ] Đổi `JWT_SECRET_KEY` thành key mạnh (min 32 characters)
- [ ] Đổi tất cả mật khẩu mặc định
- [ ] Bật `HTTPS_ONLY=true`
- [ ] Cấu hình TLS certificate hợp lệ
- [ ] Chỉ định `ALLOWED_ORIGINS` cụ thể
- [ ] Bật `ENABLE_CHECKSUM_VERIFICATION=true` cho upload endpoints
- [ ] Cấu hình rate limiting
- [ ] Thiết lập monitoring và logging
- [ ] Sử dụng database để quản lý users (thay vì FAKE_USERS_DB)
- [ ] Review và cập nhật Security Headers theo nhu cầu

---

## 7. Troubleshooting

### Lỗi "Could not validate credentials"

- Kiểm tra token có hợp lệ không
- Kiểm tra token đã hết hạn chưa
- Verify `JWT_SECRET_KEY` đúng với key dùng để tạo token

### Lỗi "Checksum verification failed"

- Kiểm tra thuật toán checksum đúng (md5 hoặc sha256)
- Tính toán lại checksum từ file gốc
- Đảm bảo header `X-Checksum` và `X-Checksum-Algorithm` được gửi đúng

### HTTPS Redirect không hoạt động

- Kiểm tra `HTTPS_ONLY=true` trong `.env`
- Nếu dùng reverse proxy, đảm bảo header `X-Forwarded-Proto` được set

---

## 8. Best Practices

### JWT Tokens

1. **Không lưu trong localStorage** (dễ bị XSS attack)
2. **Lưu trong httpOnly cookie** hoặc memory
3. **Implement refresh token** cho session dài hạn
4. **Token expiry ngắn** (15-30 phút)
5. **Invalidate tokens** khi user logout

### Passwords

1. **Minimum 8 characters**
2. **Password strength validation**
3. **Implement password reset flow**
4. **Two-factor authentication** (recommended)

### API Security

1. **Rate limiting** cho mọi endpoints
2. **Input validation** nghiêm ngặt
3. **Sanitize user input** trước khi xử lý
4. **Log security events**
5. **Regular security audits**

---

## 9. References

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [TLS Best Practices](https://wiki.mozilla.org/Security/Server_Side_TLS)

---

## Support

Nếu có câu hỏi về bảo mật, vui lòng liên hệ security team hoặc tạo issue trên repository.
