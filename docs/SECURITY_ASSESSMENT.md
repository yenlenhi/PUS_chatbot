# Đánh Giá Bảo Mật Hệ Thống University Chatbot

**Ngày đánh giá**: 15/01/2026  
**Phiên bản**: 1.0  
**Trạng thái**: Development → Production Readiness Assessment

---

## 📊 Tổng Quan Đánh Giá

Hệ thống University Chatbot đã được kiểm tra toàn diện về các khía cạnh bảo mật theo yêu cầu:

| # | Yêu Cầu Bảo Mật | Trạng Thái | Điểm | Mức Độ |
|---|-----------------|-----------|------|---------|
| 1 | Phân quyền người dùng | ⚠️ Cơ bản | 60/100 | MEDIUM |
| 2 | Mã hóa dữ liệu | ⚠️ Một phần | 50/100 | HIGH |
| 3 | Sao lưu dữ liệu | ❌ Thiếu | 30/100 | CRITICAL |
| 4 | Quản lý phiên đăng nhập | ⚠️ Cơ bản | 55/100 | MEDIUM |
| 5 | Biện pháp bảo mật khác | ✅ Tốt | 65/100 | LOW |

### **TỔNG ĐIỂM**: 52/100 ⚠️

**Kết luận**: Hệ thống có foundation bảo mật tốt nhưng **CHƯA PRODUCTION-READY**. Cần khắc phục các vấn đề CRITICAL và HIGH trước khi triển khai.

---

## 1️⃣ Phân Quyền Người Dùng (60/100) ⚠️

### ✅ Đã Có

#### **JWT Authentication**
```python
# File: src/auth/jwt_handler.py
- ✅ Token-based authentication với HS256
- ✅ Configurable token expiration (mặc định 30 phút)
- ✅ Token verification middleware
- ✅ OAuth2 compatible endpoints
```

**Environment Variables:**
```bash
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### **Role-Based Access Control (RBAC)**
```python
# File: src/auth/examples.py
- ✅ Hỗ trợ scopes: ["admin", "user", "documents:read", "documents:write"]
- ✅ require_admin() dependency cho admin endpoints
- ✅ require_scope() factory cho custom permissions
- ✅ get_current_user() cho optional/required auth
```

**Ví dụ sử dụng:**
```python
from src.auth import get_current_user, require_admin

# Protected endpoint
@router.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(401, "Authentication required")
    return {"message": f"Hello {user.username}"}

# Admin-only endpoint
@router.delete("/admin/data")
async def admin_route(admin: User = Depends(require_admin)):
    return {"message": "Admin action performed"}
```

#### **Authentication Endpoints**
```python
# File: src/api/auth_routes.py
POST /auth/token       # OAuth2 form login
POST /auth/login       # JSON login
```

### ❌ Thiếu / Hạn Chế

| Vấn Đề | Mức Độ | Mô Tả |
|--------|--------|-------|
| **Hardcoded Users** | 🔴 CRITICAL | Users lưu trong `FAKE_USERS_DB`, không có database |
| **No User CRUD** | 🔴 HIGH | Không có API tạo/sửa/xóa users |
| **No Password Reset** | 🟡 MEDIUM | Không có flow reset password |
| **No 2FA** | 🟢 LOW | Không có two-factor authentication |
| **No Session Tracking** | 🟡 MEDIUM | Không track active sessions |

### 📋 File Liên Quan

```
src/auth/
├── jwt_handler.py        # JWT token creation & verification
├── security.py           # Password hashing (bcrypt)
├── examples.py           # Usage examples
└── __init__.py

src/api/
└── auth_routes.py        # Login endpoints

config/
└── settings.py           # JWT_SECRET_KEY, ALGORITHM, EXPIRE_MINUTES
```

### 🛠️ Khuyến Nghị Cải Thiện

#### **Priority 1: User Database** 🔴
```sql
-- Tạo User table trong PostgreSQL
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, role)
);
```

#### **Priority 2: User Management API**
```python
POST   /api/admin/users          # Create user (admin only)
GET    /api/admin/users          # List users (admin only)
GET    /api/admin/users/{id}     # Get user details
PUT    /api/admin/users/{id}     # Update user
DELETE /api/admin/users/{id}     # Delete user
POST   /api/users/change-password  # Change own password
```

#### **Priority 3: Enhanced Security**
- Implement refresh tokens (Redis-based)
- Add password strength validation
- Implement account lockout after failed attempts
- Add email verification for new users

---

## 2️⃣ Mã Hóa Dữ Liệu (50/100) ⚠️

### ✅ Đã Có

#### **Encryption in Transit (HTTPS/TLS)**
```python
# File: src/middleware/https_middleware.py
- ✅ HTTPSRedirectMiddleware - redirect HTTP → HTTPS
- ✅ TLS 1.2+ enforcement
- ✅ Security headers middleware
```

**Cấu hình:**
```bash
HTTPS_ONLY=true
TLS_MIN_VERSION=1.2
```

**Security Headers tự động:**
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; ...
```

#### **Password Hashing**
```python
# File: src/auth/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqXc3rKHzC
- ✅ Bcrypt với cost factor 12
- ✅ Automatic salt generation
- ✅ Secure password verification
```

#### **Checksum Verification**
```python
# File: src/utils/checksum.py
- ✅ SHA256/MD5 checksums cho file uploads
- ✅ File integrity verification
- ✅ Middleware cho admin uploads
```

**Sử dụng:**
```bash
# Calculate checksum
CHECKSUM=$(sha256sum document.pdf | awk '{print $1}')

# Upload with checksum
curl -X POST "/api/admin/upload" \
  -H "X-Checksum: $CHECKSUM" \
  -H "X-Checksum-Algorithm: sha256" \
  -F "file=@document.pdf"
```

#### **Redis Authentication**
```python
# File: config/settings.py
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")  # Hỗ trợ authenticated Redis
```

### ❌ Thiếu / Hạn Chế

| Vấn Đề | Mức Độ | Mô Tả |
|--------|--------|-------|
| **No Encryption at Rest** | 🔴 HIGH | PostgreSQL data không mã hóa |
| **No Field Encryption** | 🟡 MEDIUM | Sensitive fields (email, phone) không encrypted |
| **No Key Management** | 🟡 MEDIUM | Không có key rotation strategy |
| **JWT Secret Weak** | 🔴 CRITICAL | Default secret key không an toàn |

### 📋 File Liên Quan

```
src/middleware/
├── https_middleware.py    # HTTPS redirect + Security headers
└── checksum_middleware.py # File integrity verification

src/auth/
└── security.py            # Password hashing

src/utils/
└── checksum.py            # SHA256/MD5 utilities

config/
└── settings.py            # HTTPS_ONLY, TLS_MIN_VERSION
```

### 🛠️ Khuyến Nghị Cải Thiện

#### **Priority 1: Strong JWT Secret** 🔴
```bash
# Generate strong secret key
openssl rand -hex 32

# Add to .env
JWT_SECRET_KEY=<generated-64-char-hex-string>
```

#### **Priority 2: Database Encryption at Rest** 🔴
```yaml
# Railway PostgreSQL - Enable encryption
# (Thường có sẵn, cần verify)

# Local PostgreSQL
postgresql.conf:
  ssl = on
  ssl_cert_file = '/path/to/server.crt'
  ssl_key_file = '/path/to/server.key'
```

#### **Priority 3: Field-Level Encryption** 🟡
```python
# Tạo encryption utility
from cryptography.fernet import Fernet

class FieldEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()

# Sử dụng cho sensitive fields
user.email = encrypt(user.email)
user.phone = encrypt(user.phone)
```

---

## 3️⃣ Sao Lưu Dữ Liệu (30/100) ❌

### ✅ Đã Có (Rất Hạn Chế)

#### **Manual Backups**
```
data/embeddings/backup/
├── chatbot.db.backup
└── database_pre_migration_20250709_103157.db
```

#### **Script-Based Backup**
```python
# File: scripts/process_incremental_pdfs.py
def create_backup():
    """Create backup of chunks file"""
    backup_file = f"backup_{timestamp}.json"
    shutil.copy(chunks_file, backup_file)
```

### ❌ Thiếu (Nghiêm Trọng)

| Vấn Đề | Mức Độ | Tác Động |
|--------|--------|----------|
| **No PostgreSQL Backup** | 🔴 CRITICAL | Mất toàn bộ data nếu DB crash |
| **No Automation** | 🔴 CRITICAL | Dựa vào manual intervention |
| **No Backup Schedule** | 🔴 HIGH | Không có backup định kỳ |
| **No Off-Site Storage** | 🔴 HIGH | Backup cùng server → mất cùng lúc |
| **No Retention Policy** | 🟡 MEDIUM | Không quản lý backup cũ |
| **No Restore Testing** | 🟡 MEDIUM | Không test khôi phục |
| **No Point-in-Time Recovery** | 🟡 MEDIUM | Không thể restore về thời điểm cụ thể |

### 🛠️ Khuyến Nghị Cải Thiện (Ưu Tiên Cao)

#### **Priority 1: PostgreSQL Automated Backup** 🔴

##### **Option A: Railway Automated Backups**
```bash
# Railway CLI
railway up --service database

# Enable automated backups trong Railway Dashboard:
# Database → Settings → Backups → Enable Daily Backups
```

##### **Option B: Custom Backup Script**
```bash
# File: scripts/backup_database.sh
#!/bin/bash

BACKUP_DIR="/data/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump $DATABASE_URL > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Upload to S3/Supabase Storage
aws s3 cp $BACKUP_FILE.gz s3://uni-bot-backups/

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

##### **Option C: Automated Cron Job**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /app/scripts/backup_database.sh

# Weekly full backup at Sunday 3 AM
0 3 * * 0 /app/scripts/backup_full.sh
```

#### **Priority 2: Redis Backup** 🟡
```bash
# File: scripts/backup_redis.sh
#!/bin/bash

BACKUP_DIR="/data/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# Trigger Redis BGSAVE
redis-cli BGSAVE

# Wait for completion
while [ $(redis-cli LASTSAVE) -eq $LASTSAVE ]; do
    sleep 1
done

# Copy RDB file
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"
gzip "$BACKUP_DIR/redis_$DATE.rdb"
```

#### **Priority 3: Backup Service** 🔴

**Tạo Backup Service:**
```python
# File: src/services/backup_service.py
import subprocess
import os
from datetime import datetime
from pathlib import Path
from src.utils.logger import log
from config.settings import DATABASE_URL, DATA_DIR

class BackupService:
    def __init__(self):
        self.backup_dir = DATA_DIR / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_postgres(self) -> str:
        """Backup PostgreSQL database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"postgres_{timestamp}.sql"
        
        try:
            # Run pg_dump
            result = subprocess.run(
                ["pg_dump", DATABASE_URL],
                stdout=open(backup_file, 'w'),
                stderr=subprocess.PIPE,
                check=True
            )
            
            # Compress
            subprocess.run(["gzip", backup_file], check=True)
            
            log.info(f"PostgreSQL backup created: {backup_file}.gz")
            return f"{backup_file}.gz"
        
        except Exception as e:
            log.error(f"Backup failed: {e}")
            raise
    
    def cleanup_old_backups(self, days: int = 30):
        """Remove backups older than specified days"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for backup in self.backup_dir.glob("*.sql.gz"):
            if backup.stat().st_mtime < cutoff:
                backup.unlink()
                log.info(f"Deleted old backup: {backup}")
```

**Tích hợp vào API:**
```python
# File: src/api/routes.py
from src.services.backup_service import BackupService

@router.post("/admin/backup", dependencies=[Depends(require_admin)])
async def trigger_backup():
    """Manually trigger database backup"""
    backup_service = BackupService()
    backup_file = backup_service.backup_postgres()
    return {"message": "Backup created", "file": backup_file}
```

#### **Priority 4: Backup Monitoring** 🟡

```python
# File: src/services/backup_monitor.py
from apscheduler.schedulers.background import BackgroundScheduler
from src.services.backup_service import BackupService

scheduler = BackgroundScheduler()
backup_service = BackupService()

# Schedule daily backup at 2 AM
scheduler.add_job(
    backup_service.backup_postgres,
    'cron',
    hour=2,
    minute=0
)

# Schedule cleanup weekly
scheduler.add_job(
    lambda: backup_service.cleanup_old_backups(days=30),
    'cron',
    day_of_week='sun',
    hour=3,
    minute=0
)

scheduler.start()
```

---

## 4️⃣ Quản Lý Phiên Đăng Nhập (55/100) ⚠️

### ✅ Đã Có

#### **JWT Token Sessions**
```python
# File: src/auth/jwt_handler.py
- ✅ Stateless JWT tokens
- ✅ Token expiration (30 minutes default)
- ✅ Token verification middleware
- ✅ User info embedded in token
```

**Token Structure:**
```json
{
  "sub": "username",
  "user_id": "user123",
  "scopes": ["admin", "user"],
  "exp": 1736950800,
  "iat": 1736949000
}
```

#### **OAuth2 Compatible**
```python
# File: src/api/auth_routes.py
POST /auth/token    # Form-based (Swagger UI compatible)
POST /auth/login    # JSON-based (Frontend friendly)
```

### ❌ Thiếu / Hạn Chế

| Vấn Đề | Mức Độ | Tác Động |
|--------|--------|----------|
| **No Refresh Tokens** | 🟡 HIGH | User phải login lại sau 30 phút |
| **No Token Revocation** | 🔴 HIGH | Không thu hồi token bị leak |
| **No Session Tracking** | 🟡 MEDIUM | Không biết user đang online |
| **No Device Management** | 🟢 LOW | Không quản lý devices |
| **No Concurrent Limits** | 🟢 LOW | User có thể login vô hạn |

### 🛠️ Khuyến Nghị Cải Thiện

#### **Priority 1: Token Revocation (Blacklist)** 🔴

```python
# File: src/services/token_blacklist_service.py
import redis
from datetime import timedelta
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

class TokenBlacklistService:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
    
    def revoke_token(self, token: str, expires_in: int):
        """Add token to blacklist"""
        self.redis.setex(
            f"blacklist:{token}",
            expires_in,
            "1"
        )
    
    def is_revoked(self, token: str) -> bool:
        """Check if token is revoked"""
        return self.redis.exists(f"blacklist:{token}") > 0
```

**Update JWT Handler:**
```python
# File: src/auth/jwt_handler.py
async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        return None
    
    # Check blacklist
    if blacklist_service.is_revoked(token):
        raise HTTPException(401, "Token has been revoked")
    
    token_data = verify_access_token(token)
    # ... rest of code
```

**Logout Endpoint:**
```python
@router.post("/auth/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    """Revoke current token"""
    # Get token expiry
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expires_in = payload['exp'] - int(time.time())
    
    # Add to blacklist
    blacklist_service.revoke_token(token, expires_in)
    
    return {"message": "Logged out successfully"}
```

#### **Priority 2: Refresh Token Mechanism** 🟡

```python
# File: src/auth/jwt_handler.py

def create_refresh_token(user_id: str) -> str:
    """Create long-lived refresh token"""
    token_data = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

# Store in Redis
def store_refresh_token(user_id: str, token: str):
    redis_client.setex(
        f"refresh:{user_id}:{token}",
        timedelta(days=30),
        "1"
    )
```

**Token Refresh Endpoint:**
```python
@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Exchange refresh token for new access token"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(400, "Invalid token type")
        
        user_id = payload.get("sub")
        
        # Verify refresh token exists in Redis
        if not redis_client.exists(f"refresh:{user_id}:{refresh_token}"):
            raise HTTPException(401, "Refresh token revoked")
        
        # Create new access token
        access_token = create_access_token({"sub": user_id})
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")
```

#### **Priority 3: Session Tracking** 🟡

```python
# File: src/services/session_service.py

class SessionService:
    def track_login(self, user_id: str, token: str, device_info: dict):
        """Track active session"""
        session_data = {
            "user_id": user_id,
            "token": token,
            "device": device_info,
            "login_at": datetime.now().isoformat()
        }
        
        redis_client.setex(
            f"session:{user_id}:{token[:16]}",
            timedelta(hours=24),
            json.dumps(session_data)
        )
    
    def get_active_sessions(self, user_id: str) -> list:
        """Get all active sessions for user"""
        pattern = f"session:{user_id}:*"
        sessions = []
        
        for key in redis_client.scan_iter(pattern):
            data = redis_client.get(key)
            if data:
                sessions.append(json.loads(data))
        
        return sessions
    
    def revoke_session(self, user_id: str, token_prefix: str):
        """Revoke specific session"""
        redis_client.delete(f"session:{user_id}:{token_prefix}")
```

**Session Management Endpoints:**
```python
@router.get("/auth/sessions")
async def list_sessions(current_user: User = Depends(get_current_user)):
    """List all active sessions"""
    sessions = session_service.get_active_sessions(current_user.user_id)
    return {"sessions": sessions}

@router.delete("/auth/sessions/{token_prefix}")
async def revoke_session(
    token_prefix: str,
    current_user: User = Depends(get_current_user)
):
    """Revoke specific session"""
    session_service.revoke_session(current_user.user_id, token_prefix)
    return {"message": "Session revoked"}
```

---

## 5️⃣ Các Biện Pháp Bảo Mật Khác (65/100) ✅

### ✅ Đã Có (Tốt)

#### **Security Headers** ✅
```python
# File: src/middleware/https_middleware.py
class SecurityHeadersMiddleware:
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Comprehensive security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; ..."
        
        return response
```

#### **CORS Configuration** ✅
```python
# File: main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Configurable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Configuration:**
```bash
# Development
ALLOWED_ORIGINS=*

# Production
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

#### **Input Validation** ✅
```python
# Pydantic models tự động validate
class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v
```

#### **File Upload Security** ✅
```python
# File: src/middleware/checksum_middleware.py
- ✅ Checksum verification (SHA256/MD5)
- ✅ File type validation
- ✅ Size limits
```

#### **Secure Defaults** ✅
```python
# .gitignore protects sensitive files
.env
*.log
data/
__pycache__/
*.db
```

### ❌ Thiếu / Cần Cải Thiện

| Vấn Đề | Mức Độ | Mô Tả |
|--------|--------|-------|
| **No Rate Limiting** | 🟡 HIGH | Config có nhưng chưa implement |
| **No API Throttling** | 🟡 MEDIUM | Dễ bị abuse |
| **No CSRF Protection** | 🟡 MEDIUM | Cho state-changing requests |
| **No Security Audit Logs** | 🟡 MEDIUM | Không track security events |
| **No Input Sanitization** | 🟡 MEDIUM | XSS/SQL injection risk |
| **No IP Whitelist** | 🟢 LOW | Cho admin endpoints |

### 🛠️ Khuyến Nghị Cải Thiện

#### **Priority 1: Rate Limiting Implementation** 🟡

```python
# File: src/middleware/rate_limit_middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from config.settings import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < RATE_LIMIT_WINDOW
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Add current request
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(
            RATE_LIMIT_REQUESTS - len(self.requests[client_ip])
        )
        
        return response
```

**Add to main.py:**
```python
from src.middleware.rate_limit_middleware import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)
```

#### **Priority 2: Redis-Based Rate Limiting** 🟡

```python
# File: src/services/rate_limiter.py
import redis
from datetime import timedelta

class RedisRateLimiter:
    def __init__(self):
        self.redis = redis.Redis(...)
    
    def is_rate_limited(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """
        Check if key has exceeded rate limit
        
        Args:
            key: Identifier (IP, user_id, etc)
            limit: Max requests allowed
            window: Time window in seconds
        
        Returns:
            True if rate limited, False otherwise
        """
        current = self.redis.get(f"rate:{key}")
        
        if current is None:
            self.redis.setex(f"rate:{key}", window, 1)
            return False
        
        if int(current) >= limit:
            return True
        
        self.redis.incr(f"rate:{key}")
        return False
```

**Usage in routes:**
```python
from fastapi import Request
from src.services.rate_limiter import RedisRateLimiter

rate_limiter = RedisRateLimiter()

@router.post("/chat")
async def chat(request: Request, data: ChatRequest):
    client_ip = request.client.host
    
    if rate_limiter.is_rate_limited(client_ip, limit=100, window=60):
        raise HTTPException(429, "Rate limit exceeded")
    
    # Process request...
```

#### **Priority 3: Security Audit Logging** 🟡

```python
# File: src/services/security_logger.py
import logging
from datetime import datetime
from src.services.postgres_database_service import PostgresDatabaseService

class SecurityLogger:
    def __init__(self):
        self.db = PostgresDatabaseService()
        self.logger = logging.getLogger("security")
    
    def log_event(
        self,
        event_type: str,
        user_id: str = None,
        ip_address: str = None,
        details: dict = None,
        severity: str = "INFO"
    ):
        """Log security event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details,
            "severity": severity
        }
        
        # Log to file
        self.logger.log(
            getattr(logging, severity),
            f"{event_type}: {details}"
        )
        
        # Store in database
        self._store_event(event)
    
    def _store_event(self, event: dict):
        """Store event in security_logs table"""
        # TODO: Implement database storage
        pass
```

**Usage:**
```python
from src.services.security_logger import SecurityLogger

security_logger = SecurityLogger()

# Log login attempts
@router.post("/auth/login")
async def login(request: Request, data: LoginRequest):
    client_ip = request.client.host
    
    user = authenticate_user(data.username, data.password)
    
    if not user:
        security_logger.log_event(
            "LOGIN_FAILED",
            user_id=data.username,
            ip_address=client_ip,
            details={"reason": "Invalid credentials"},
            severity="WARNING"
        )
        raise HTTPException(401, "Invalid credentials")
    
    security_logger.log_event(
        "LOGIN_SUCCESS",
        user_id=user.username,
        ip_address=client_ip,
        severity="INFO"
    )
    
    return create_token(user)
```

#### **Priority 4: Input Sanitization** 🟡

```python
# File: src/utils/sanitizer.py
import bleach
import re

class InputSanitizer:
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove potentially dangerous HTML"""
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        return bleach.clean(text, tags=allowed_tags, strip=True)
    
    @staticmethod
    def sanitize_sql(text: str) -> str:
        """Escape SQL special characters"""
        # Note: Use parameterized queries instead
        dangerous = ["'", '"', ';', '--', '/*', '*/']
        for char in dangerous:
            text = text.replace(char, '')
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove dangerous characters from filename"""
        # Remove path traversal attempts
        filename = filename.replace('../', '').replace('..\\', '')
        # Keep only alphanumeric, dash, underscore, dot
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        return filename
```

**Apply to inputs:**
```python
from src.utils.sanitizer import InputSanitizer

@router.post("/chat")
async def chat(data: ChatRequest):
    # Sanitize user input
    sanitized_query = InputSanitizer.sanitize_html(data.query)
    
    # Process sanitized input
    answer = rag_service.generate_answer(sanitized_query)
    return answer
```

---

## 🚨 Critical Issues Summary

### **MUST FIX BEFORE PRODUCTION** 🔴

| # | Issue | Impact | Priority | ETA |
|---|-------|--------|----------|-----|
| 1 | Hardcoded users (FAKE_USERS_DB) | Cannot manage users | CRITICAL | 2 days |
| 2 | Weak JWT secret key | Token compromise | CRITICAL | 1 hour |
| 3 | No PostgreSQL backup automation | Data loss risk | CRITICAL | 1 day |
| 4 | No token revocation | Cannot invalidate leaked tokens | HIGH | 1 day |
| 5 | No rate limiting implementation | DDoS vulnerability | HIGH | 4 hours |

### **Action Plan**

#### **Week 1: Critical Security**
- [ ] Day 1: Generate strong JWT secret key
- [ ] Day 1: Setup PostgreSQL automated backups
- [ ] Day 2-3: Implement User database + CRUD API
- [ ] Day 4: Implement token revocation (blacklist)
- [ ] Day 5: Implement rate limiting

#### **Week 2: Enhanced Security**
- [ ] Day 1-2: Refresh token mechanism
- [ ] Day 3: Session tracking
- [ ] Day 4: Security audit logging
- [ ] Day 5: Input sanitization

#### **Week 3: Production Hardening**
- [ ] Day 1: CSRF protection
- [ ] Day 2: Field-level encryption
- [ ] Day 3: Backup restore testing
- [ ] Day 4: Security testing
- [ ] Day 5: Documentation update

---

## 📚 Related Documentation

- [SECURITY.md](../SECURITY.md) - Detailed security guide
- [docs/OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md) - Operations guide
- [docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md](deployment/RAILWAY_DEPLOYMENT_GUIDE.md) - Railway deployment

---

## 🔗 Useful Resources

### Security Best Practices
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

### Backup & Recovery
- [PostgreSQL Backup Guide](https://www.postgresql.org/docs/current/backup.html)
- [Railway Backup Documentation](https://docs.railway.app/)

### Authentication
- [OAuth2 with Password Flow](https://oauth.net/2/grant-types/password/)
- [JWT.io](https://jwt.io/) - JWT debugger

---

## 📧 Contact & Support

Nếu có câu hỏi về bảo mật, vui lòng:
1. Review [SECURITY.md](../SECURITY.md) trước
2. Tạo issue với label `security`
3. Liên hệ security team

**Last Updated**: 15/01/2026  
**Next Review**: 15/02/2026
