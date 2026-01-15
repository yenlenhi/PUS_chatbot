# Hệ Thống Phân Quyền Người Dùng (User Authorization System)

## 📋 Mục Lục
1. [Giới Thiệu](#giới-thiệu)
2. [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
3. [Cấu Trúc Database](#cấu-trúc-database)
4. [Các Role và Quyền](#các-role-và-quyền)
5. [Authentication Flow](#authentication-flow)
6. [API Endpoints](#api-endpoints)
7. [Ví Dụ Sử Dụng](#ví-dụ-sử-dụng)
8. [Quản Lý Người Dùng](#quản-lý-người-dùng)
9. [Best Practices](#best-practices)

---

## Giới Thiệu

Hệ thống phân quyền người dùng cho phép quản lý quyền truy cập của các người dùng khác nhau đến các tính năng của ứng dụng. Hệ thống sử dụng:

- **JWT (JSON Web Tokens)** để xác thực người dùng
- **PostgreSQL** (Supabase) để lưu trữ dữ liệu người dùng
- **Bcrypt** để mã hóa mật khẩu
- **Role-Based Access Control (RBAC)** để quản lý quyền

---

## Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────┐
│         Frontend (Next.js)              │
│    - Admin Dashboard                    │
│    - User Management                    │
│    - Chat Interface                     │
└────────────────┬────────────────────────┘
                 │ HTTP/HTTPS
                 ▼
┌─────────────────────────────────────────┐
│     Backend API (FastAPI)               │
│    - /auth/login (Authentication)       │
│    - /api/users/* (User Management)     │
│    - /api/v1/auth/login (JSON)          │
└────────────────┬────────────────────────┘
                 │ PostgreSQL Query
                 ▼
┌─────────────────────────────────────────┐
│   Database (Supabase PostgreSQL)        │
│    - users table                        │
│    - user_roles table                   │
│    - role_permissions table (optional)  │
└─────────────────────────────────────────┘
```

---

## Cấu Trúc Database

### 1. Bảng `users` (Người Dùng)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Bcrypt hash
    email VARCHAR(100),
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**Các Trường:**
- `id`: ID duy nhất của người dùng (UUID)
- `username`: Tên đăng nhập (không trùng)
- `password_hash`: Hash mật khẩu (không lưu plaintext)
- `email`: Email người dùng
- `full_name`: Họ và tên
- `is_active`: Trạng thái hoạt động
- `created_at`: Ngày tạo
- `updated_at`: Lần cập nhật cuối
- `last_login`: Lần đăng nhập cuối

### 2. Bảng `user_roles` (Vai Trò)

```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_name VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, role_name)
);
```

**Các Trường:**
- `id`: ID duy nhất
- `user_id`: Tham chiếu đến bảng users
- `role_name`: Tên role (admin, user, moderator, etc.)
- `assigned_at`: Ngày gán role

### 3. Ví Dụ Dữ Liệu

**users table:**
```
id                                  | username | email           | full_name          | is_active
------------------------------------+----------+-----------------+--------------------+-----------
550e8400-e29b-41d4-a716-446655440000| admin    | admin@uni.edu   | Administrator      | true
550e8400-e29b-41d4-a716-446655440001| user     | user@uni.edu    | Regular User       | true
```

**user_roles table:**
```
id                                  | user_id                              | role_name
------------------------------------+--------------------------------------+-----------
550e8400-e29b-41d4-a716-446655440002| 550e8400-e29b-41d4-a716-446655440000| admin
550e8400-e29b-41d4-a716-446655440003| 550e8400-e29b-41d4-a716-446655440001| user
550e8400-e29b-41d4-a716-446655440004| 550e8400-e29b-41d4-a716-446655440001| moderator
```

---

## Các Role và Quyền

### Admin (Quản Trị Viên)
- ✅ Quản lý người dùng (tạo, sửa, xóa)
- ✅ Quản lý role và quyền
- ✅ Xem logs và analytics
- ✅ Upload tài liệu
- ✅ Xem tất cả tài liệu
- ✅ Cấu hình hệ thống
- ✅ Truy cập admin dashboard

**Credentials:** 
- Username: `admin`
- Password: `Admin123`

### User (Người Dùng Bình Thường)
- ✅ Xem tài liệu công khai
- ✅ Sử dụng chatbot
- ✅ Xem lịch sử chat của mình
- ❌ Không quản lý người dùng khác
- ❌ Không xem analytics

**Credentials:**
- Username: `user`
- Password: `User1234`

### Moderator (Kiểm Duyệt Viên) - Optional
- ✅ Xem tất cả content
- ✅ Xem feedback người dùng
- ✅ Báo cáo vấn đề
- ❌ Không quản lý người dùng
- ❌ Không cấu hình hệ thống

---

## Authentication Flow

### 1. Đăng Nhập

```
User Input: username + password
     ↓
Send to: POST /api/v1/auth/login
     ↓
Backend validate:
  - Check if user exists
  - Compare password with bcrypt hash
     ↓
Success? → Generate JWT Token
     ↓
Return: { access_token, token_type }
     ↓
Frontend store token in sessionStorage
```

### 2. JWT Token Structure

JWT Token bao gồm 3 phần:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJ1c2VybmFtZSI6ImFkbWluIiwidXNlcl9pZCI6IjEyMyIsInNjb3Blczo6WyJhZG1pbiJdLCJleHAiOjE2MzEwMDAwMDB9.
signature_hash_here
```

**Payload (phần 2):**
```json
{
  "username": "admin",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "scopes": ["admin"],
  "exp": 1631000000
}
```

### 3. Sử Dụng Token

Mỗi request đến API cần gửi token trong header:

```http
GET /api/v1/chat HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## API Endpoints

### Authentication

#### 1. Login (JSON)
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin123"
}
```

**Response (Success - 200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (Error - 401):**
```json
{
  "detail": "Incorrect username or password"
}
```

#### 2. Login (Form - OAuth2 Compatible)
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=Admin123
```

### User Management

#### 3. Lấy Danh Sách Người Dùng
```http
GET /api/users
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "email": "admin@uni.edu",
    "full_name": "Administrator",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "roles": ["admin"]
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "username": "user",
    "email": "user@uni.edu",
    "full_name": "Regular User",
    "is_active": true,
    "created_at": "2024-01-02T00:00:00Z",
    "roles": ["user", "moderator"]
  }
]
```

#### 4. Tạo Người Dùng Mới
```http
POST /api/users
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "username": "newuser",
  "password": "SecurePass123",
  "email": "newuser@uni.edu",
  "full_name": "New User"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "username": "newuser",
  "email": "newuser@uni.edu",
  "full_name": "New User",
  "is_active": true
}
```

#### 5. Cập Nhật Người Dùng
```http
PUT /api/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "updated@uni.edu",
  "full_name": "Updated Name"
}
```

#### 6. Xóa Người Dùng
```http
DELETE /api/users/{user_id}
Authorization: Bearer <admin_token>
```

#### 7. Gán Role Cho Người Dùng
```http
POST /api/users/{user_id}/roles
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "role_name": "moderator"
}
```

#### 8. Xóa Role Từ Người Dùng
```http
DELETE /api/users/{user_id}/roles/{role_name}
Authorization: Bearer <admin_token>
```

---

## Ví Dụ Sử Dụng

### JavaScript/TypeScript (Frontend)

```typescript
// 1. Đăng nhập
const loginResponse = await fetch('https://puschatbot-production.up.railway.app/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'Admin123',
  }),
});

const { access_token } = await loginResponse.json();

// Lưu token
sessionStorage.setItem('adminToken', access_token);

// 2. Sử dụng token để gọi API khác
const response = await fetch('https://puschatbot-production.up.railway.app/api/users', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${access_token}`,
  },
});

const users = await response.json();
console.log(users);
```

### Python (Backend)

```python
import requests

# 1. Đăng nhập
login_response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={
        'username': 'admin',
        'password': 'Admin123',
    }
)

token = login_response.json()['access_token']

# 2. Sử dụng token
headers = {'Authorization': f'Bearer {token}'}
users_response = requests.get(
    'http://localhost:8000/api/users',
    headers=headers
)

users = users_response.json()
print(users)
```

### cURL

```bash
# 1. Đăng nhập
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123"}'

# Response: {"access_token":"...","token_type":"bearer"}

# 2. Sử dụng token
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer <token_from_step_1>"
```

---

## Quản Lý Người Dùng

### Tạo Người Dùng Mới

**Qua Admin Dashboard:**
1. Đăng nhập với tài khoản admin
2. Vào mục "Quản Lý Người Dùng"
3. Nhấp "Tạo Người Dùng Mới"
4. Nhập thông tin (username, mật khẩu, email, họ tên)
5. Chọn role
6. Nhấp "Tạo"

**Qua API:**
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "lecturer1",
    "password": "Secure@Pass123",
    "email": "lecturer1@uni.edu",
    "full_name": "Lecturer One"
  }'
```

### Yêu Cầu Mật Khẩu

Mật khẩu phải:
- ✅ Dài tối thiểu **8 ký tự**
- ✅ Chứa **chữ hoa** (A-Z)
- ✅ Chứa **chữ thường** (a-z)
- ✅ Chứa **số** (0-9)
- ✅ Không chứa username

**Ví dụ hợp lệ:**
- `Admin123`
- `MyPassword@2024`
- `Secure_Pass_99`

**Ví dụ không hợp lệ:**
- `admin123` (không có chữ hoa)
- `Admin` (quá ngắn)
- `admin` (trùng username)

### Thay Đổi Mật Khẩu

```http
PUT /api/users/{user_id}/password
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "old_password": "Admin123",
  "new_password": "NewPassword@2024"
}
```

### Deactivate/Activate Người Dùng

```http
PATCH /api/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "is_active": false
}
```

---

## Best Practices

### 🔐 Bảo Mật

1. **Không Bao Giờ Lưu Plaintext Password**
   - Luôn sử dụng bcrypt để hash mật khẩu
   - Sử dụng salt để tăng bảo mật

2. **Bảo Vệ JWT Token**
   - Lưu token chỉ trong sessionStorage, không localStorage
   - Xóa token khi logout
   - Thiết lập expiry time hợp lý (ví dụ: 24 giờ)

3. **Enforce HTTPS**
   - Luôn sử dụng HTTPS khi truyền token
   - Sử dụng Secure flag cho cookies

4. **Validation Input**
   - Validate username/password format
   - Sanitize input để tránh SQL injection
   - Limit login attempts (rate limiting)

### 📋 Quản Lý Role

1. **Principle of Least Privilege (PoLP)**
   - Chỉ gán quyền cần thiết
   - Tránh gán quá nhiều role

2. **Audit Trail**
   - Ghi log tất cả thay đổi người dùng
   - Ghi log login/logout
   - Ghi log permission changes

3. **Regular Review**
   - Kiểm tra quyền người dùng định kỳ
   - Xóa role không cần thiết
   - Deactivate tài khoản không sử dụng

### 💾 Database

1. **Backup**
   - Backup users table định kỳ
   - Lưu trữ backup ở nơi an toàn

2. **Indexing**
   - Index trên `username` để query nhanh
   - Index trên `user_id` trong user_roles

3. **Constraints**
   - Đặt UNIQUE constraint trên username
   - Đặt FOREIGN KEY constraints

---

## Troubleshooting

### Lỗi: "Incorrect username or password"

**Nguyên Nhân:**
- Username hoặc password sai
- User không tồn tại
- User bị deactivate

**Giải Pháp:**
- Kiểm tra lại username (case-sensitive)
- Kiểm tra cap lock
- Liên hệ admin để reset password

### Lỗi: "Unauthorized - Missing token"

**Nguyên Nhân:**
- Không gửi Authorization header
- Token bị lỗi format
- Token hết hạn

**Giải Pháp:**
- Gửi `Authorization: Bearer <token>`
- Login lại để lấy token mới
- Kiểm tra format token

### Lỗi: "Forbidden - Insufficient permissions"

**Nguyên Nhân:**
- User không có role cần thiết
- Token không có scope đúng

**Giải Pháp:**
- Admin gán role phù hợp
- Logout và login lại

---

## Tài Liệu Liên Quan

- [Security Assessment](./SECURITY_ASSESSMENT.md)
- [API Documentation](./TECHNICAL_ARCHITECTURE.md)
- [Database Schema](./architecture/DATA_LAYER_README.md)
- [README Installation Guide](../README.md)

---

**Cập nhật lần cuối:** January 15, 2026  
**Phiên bản:** 1.0.0
