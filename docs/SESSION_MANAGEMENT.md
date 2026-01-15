# 4.2.2. Quản Lý Phiên Đăng Nhập (Session Management)

## 📋 Mục Lục
1. [Tổng Quan](#tổng-quan)
2. [Kiến Trúc Phiên Đăng Nhập](#kiến-trúc-phiên-đăng-nhập)
3. [JWT Token Management](#jwt-token-management)
4. [Frontend Session Storage](#frontend-session-storage)
5. [Token Lifecycle](#token-lifecycle)
6. [Session Validation](#session-validation)
7. [Logout và Session Cleanup](#logout-và-session-cleanup)
8. [Security Features](#security-features)
9. [Implementation Guide](#implementation-guide)
10. [Troubleshooting](#troubleshooting)

---

## Tổng Quan

Hệ thống quản lý phiên đăng nhập của University Chatbot sử dụng **JWT (JSON Web Tokens)** để duy trì trạng thái xác thực người dùng. Phương pháp này đảm bảo:

- ✅ **Stateless Authentication**: Backend không cần lưu session state
- ✅ **Scalability**: Dễ dàng scale horizontal
- ✅ **Security**: Token có thời gian hết hạn và signed
- ✅ **Performance**: Không cần query database mỗi request
- ✅ **Cross-Domain**: Hoạt động tốt với microservices

---

## Kiến Trúc Phiên Đăng Nhập

```
┌─────────────────────────────────────────┐
│          User Login Flow                │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│    Frontend (Next.js)                   │
│  ┌─────────────────────────────────────┐│
│  │ sessionStorage                      ││
│  │ - isAdminAuthenticated: 'true'      ││
│  │ - adminToken: 'eyJhbGci...'         ││
│  │ - username: 'admin'                 ││
│  │ - tokenExpiry: '2026-01-16T...'     ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
                    │ HTTP Request with Authorization header
                    ▼
┌─────────────────────────────────────────┐
│    Backend API (FastAPI)                │
│  ┌─────────────────────────────────────┐│
│  │ JWT Middleware                      ││
│  │ - Verify token signature            ││
│  │ - Check expiration                  ││
│  │ - Extract user info                 ││
│  │ - Validate scopes/roles             ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Protected Resources             │
│    (API Endpoints, Admin Dashboard)     │
└─────────────────────────────────────────┘
```

---

## JWT Token Management

### 1. Token Structure

```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "username": "admin",
  "user_id": "1",
  "scopes": ["admin"],
  "exp": 1642723200,  // Expiration timestamp
  "iat": 1642636800,  // Issued at timestamp
  "jti": "uuid-here"  // JWT ID (unique)
}

Signature:
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)
```

### 2. Token Generation (Backend)

**File:** `src/auth/jwt_handler.py`

```python
def create_token_for_user(
    username: str, 
    user_id: str, 
    scopes: List[str],
    expires_minutes: int = 1440  # 24 hours
) -> str:
    """
    Create JWT token for authenticated user
    
    Args:
        username: User's username
        user_id: User's database ID
        scopes: List of user roles/scopes
        expires_minutes: Token expiry in minutes
    
    Returns:
        JWT token string
    """
    # Set expiration time
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    
    # Create payload
    payload = {
        "username": username,
        "user_id": user_id,
        "scopes": scopes,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4())  # Unique token ID
    }
    
    # Generate token
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token
```

### 3. Token Validation

```python
def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        # Check if token is expired
        if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
            return None
            
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

---

## Frontend Session Storage

### 1. Login Process (Frontend)

**File:** `frontend/src/app/admin/page.tsx`

```typescript
const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault();
  setError('');
  setIsLoading(true);

  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        password,
      }),
    });

    if (!response.ok) {
      setError('Tên đăng nhập hoặc mật khẩu không đúng!');
      setIsLoading(false);
      return;
    }

    const data = await response.json();
    
    // Store session data
    const expiryTime = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours
    
    sessionStorage.setItem('isAdminAuthenticated', 'true');
    sessionStorage.setItem('adminToken', data.access_token);
    sessionStorage.setItem('username', username);
    sessionStorage.setItem('tokenExpiry', expiryTime.toISOString());
    sessionStorage.setItem('loginTime', new Date().toISOString());
    
    // Redirect to dashboard
    router.push('/admin/dashboard');
  } catch (err) {
    console.error('Login error:', err);
    setError('Lỗi kết nối đến máy chủ. Vui lòng thử lại!');
    setIsLoading(false);
  }
};
```

### 2. Session Check Utility

**File:** `frontend/src/utils/auth.ts`

```typescript
interface SessionData {
  isAuthenticated: boolean;
  token: string | null;
  username: string | null;
  isExpired: boolean;
  expiryTime: Date | null;
}

export const checkSession = (): SessionData => {
  const isAuth = sessionStorage.getItem('isAdminAuthenticated') === 'true';
  const token = sessionStorage.getItem('adminToken');
  const username = sessionStorage.getItem('username');
  const expiryString = sessionStorage.getItem('tokenExpiry');
  
  let isExpired = false;
  let expiryTime = null;
  
  if (expiryString) {
    expiryTime = new Date(expiryString);
    isExpired = new Date() > expiryTime;
  }
  
  // If expired, clear session
  if (isExpired) {
    clearSession();
    return {
      isAuthenticated: false,
      token: null,
      username: null,
      isExpired: true,
      expiryTime: null
    };
  }
  
  return {
    isAuthenticated: isAuth && !!token,
    token,
    username,
    isExpired,
    expiryTime
  };
};

export const clearSession = () => {
  sessionStorage.removeItem('isAdminAuthenticated');
  sessionStorage.removeItem('adminToken');
  sessionStorage.removeItem('username');
  sessionStorage.removeItem('tokenExpiry');
  sessionStorage.removeItem('loginTime');
};

export const getAuthHeader = (): { Authorization?: string } => {
  const { isAuthenticated, token } = checkSession();
  
  if (isAuthenticated && token) {
    return { Authorization: `Bearer ${token}` };
  }
  
  return {};
};
```

### 3. Protected Route Component

**File:** `frontend/src/components/ProtectedRoute.tsx`

```tsx
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { checkSession } from '@/utils/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole = 'user' 
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const session = checkSession();
    
    if (!session.isAuthenticated) {
      // Redirect to login
      router.push('/admin/login');
      return;
    }
    
    if (session.isExpired) {
      alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
      router.push('/admin/login');
      return;
    }
    
    // Check role if required
    if (requiredRole === 'admin') {
      // Verify admin role from token or API call
      verifyAdminRole(session.token).then(isAdmin => {
        if (isAdmin) {
          setIsAuthorized(true);
        } else {
          router.push('/unauthorized');
        }
        setIsLoading(false);
      });
    } else {
      setIsAuthorized(true);
      setIsLoading(false);
    }
  }, [router, requiredRole]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Đang xác thực...</p>
        </div>
      </div>
    );
  }

  if (!isAuthorized) {
    return null; // Will redirect
  }

  return <>{children}</>;
};

export default ProtectedRoute;
```

---

## Token Lifecycle

### 1. Session Timeline

```
Login Request
     │
     ▼
┌─────────────────────────────────────┐
│ Token Generated (24h expiry)        │
│ - iat: 2026-01-15 08:00:00         │
│ - exp: 2026-01-16 08:00:00         │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ Active Session Period               │
│ - All API calls include token       │
│ - Frontend checks expiry            │
│ - Auto-logout if expired           │
└─────────────────────────────────────┘
     │
     ▼ (after 24h or manual logout)
┌─────────────────────────────────────┐
│ Session Expired/Ended               │
│ - Token no longer valid             │
│ - Redirect to login                 │
│ - Clear session storage             │
└─────────────────────────────────────┘
```

### 2. Token Refresh Strategy

**Automatic Refresh (Not implemented yet)**

```typescript
// Future enhancement: Token refresh
const refreshToken = async (): Promise<string | null> => {
  try {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getCurrentToken()}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      sessionStorage.setItem('adminToken', data.access_token);
      return data.access_token;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }
  
  return null;
};
```

---

## Session Validation

### 1. Frontend Session Check

```typescript
// Check session on app start and route changes
useEffect(() => {
  const validateSession = () => {
    const session = checkSession();
    
    if (!session.isAuthenticated) {
      return false;
    }
    
    if (session.isExpired) {
      alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
      clearSession();
      router.push('/admin/login');
      return false;
    }
    
    return true;
  };
  
  // Check session every 5 minutes
  const interval = setInterval(validateSession, 5 * 60 * 1000);
  
  return () => clearInterval(interval);
}, [router]);
```

### 2. API Request Interceptor

```typescript
// Automatic token attachment for API calls
const apiClient = {
  async request(url: string, options: RequestInit = {}) {
    const session = checkSession();
    
    if (!session.isAuthenticated) {
      throw new Error('Not authenticated');
    }
    
    if (session.isExpired) {
      clearSession();
      window.location.href = '/admin/login';
      throw new Error('Session expired');
    }
    
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
      ...options.headers,
    };
    
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    // Handle 401 Unauthorized
    if (response.status === 401) {
      clearSession();
      window.location.href = '/admin/login';
      throw new Error('Authentication required');
    }
    
    return response;
  }
};
```

---

## Logout và Session Cleanup

### 1. Manual Logout

**File:** `frontend/src/components/admin/AdminHeader.tsx`

```typescript
const handleLogout = () => {
  // Confirm logout
  if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
    // Clear all session data
    clearSession();
    
    // Optional: Call backend logout endpoint
    logoutFromBackend();
    
    // Redirect to login
    router.push('/admin/login');
    
    // Show success message
    alert('Đã đăng xuất thành công!');
  }
};

const logoutFromBackend = async () => {
  try {
    const token = sessionStorage.getItem('adminToken');
    if (token) {
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    }
  } catch (error) {
    console.error('Backend logout failed:', error);
  }
};
```

### 2. Automatic Session Cleanup

```typescript
// Clean expired sessions on page load
window.addEventListener('load', () => {
  const session = checkSession();
  if (session.isExpired) {
    clearSession();
  }
});

// Clean sessions when tab becomes visible
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) {
    const session = checkSession();
    if (session.isExpired) {
      clearSession();
      window.location.href = '/admin/login';
    }
  }
});
```

---

## Security Features

### 1. Token Security

- ✅ **Strong Secret**: JWT signed với 64-character secret key
- ✅ **Expiration**: Token tự động hết hạn sau 24 giờ
- ✅ **HTTPS Only**: Token chỉ truyền qua HTTPS
- ✅ **No Local Storage**: Dùng sessionStorage thay vì localStorage
- ✅ **Auto Cleanup**: Xóa token khi hết hạn hoặc logout

### 2. CSRF Protection

```typescript
// CSRF token for sensitive operations
const performSensitiveOperation = async () => {
  const csrfToken = await getCsrfToken();
  
  const response = await apiClient.request('/api/admin/sensitive', {
    method: 'POST',
    headers: {
      'X-CSRF-Token': csrfToken
    },
    body: JSON.stringify(data)
  });
};
```

### 3. Rate Limiting (Planned)

```python
# Backend rate limiting for login attempts
@app.middleware("http")
async def rate_limit_login(request: Request, call_next):
    if request.url.path == "/api/v1/auth/login":
        client_ip = request.client.host
        
        # Check rate limit (5 attempts per minute)
        if is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many login attempts. Please try again later."}
            )
    
    response = await call_next(request)
    return response
```

---

## Implementation Guide

### 1. Frontend Integration

**In your admin component:**

```tsx
import ProtectedRoute from '@/components/ProtectedRoute';
import { checkSession, getAuthHeader } from '@/utils/auth';

const AdminDashboard = () => {
  const [userData, setUserData] = useState(null);
  
  useEffect(() => {
    const session = checkSession();
    if (session.isAuthenticated) {
      setUserData({
        username: session.username,
        expiryTime: session.expiryTime
      });
    }
  }, []);

  const handleApiCall = async () => {
    try {
      const response = await fetch('/api/v1/admin/data', {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader()
        }
      });
      
      const data = await response.json();
      // Process data
    } catch (error) {
      console.error('API call failed:', error);
    }
  };

  return (
    <ProtectedRoute requiredRole="admin">
      <div>
        <h1>Admin Dashboard</h1>
        <p>Chào mừng, {userData?.username}</p>
        <p>Phiên đăng nhập hết hạn: {userData?.expiryTime?.toLocaleString()}</p>
        
        <button onClick={handleApiCall}>
          Load Admin Data
        </button>
      </div>
    </ProtectedRoute>
  );
};
```

### 2. Backend Middleware

**File:** `src/middleware/auth_middleware.py`

```python
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.jwt_handler import verify_token

security = HTTPBearer()

async def verify_admin_token(credentials: HTTPAuthorizationCredentials):
    """Verify admin token and extract user info"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    if "admin" not in payload.get("scopes", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return payload

# Usage in routes
@app.get("/api/v1/admin/users")
async def get_users(current_user = Depends(verify_admin_token)):
    """Get all users - admin only"""
    # current_user contains decoded token data
    return {"users": get_all_users()}
```

---

## Troubleshooting

### 1. Session Issues

**Problem:** User bị logout liên tục

**Causes & Solutions:**
- Token hết hạn → Check expiry time, extend if needed
- Browser clock sai → Sync system time
- Token corrupted → Clear session and login again
- Backend secret changed → Regenerate all tokens

**Check Session Status:**
```typescript
console.log('Session Debug:', {
  isAuth: sessionStorage.getItem('isAdminAuthenticated'),
  hasToken: !!sessionStorage.getItem('adminToken'),
  expiry: sessionStorage.getItem('tokenExpiry'),
  now: new Date().toISOString()
});
```

### 2. Token Validation Errors

**Problem:** "Invalid token" errors

**Debug Steps:**
1. Verify token format in browser DevTools
2. Check if token is properly sent in request headers
3. Verify backend JWT secret is correct
4. Check token expiration time

**Token Debugging:**
```python
# Add to auth route for debugging
@app.get("/api/v1/auth/debug")
async def debug_token(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return {"error": "No authorization header"}
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, verify=False)  # Decode without verification
        return {
            "token_format": "valid",
            "payload": payload,
            "expired": datetime.utcnow() > datetime.fromtimestamp(payload.get('exp', 0))
        }
    except Exception as e:
        return {"error": str(e)}
```

### 3. CORS Issues

**Problem:** Authentication fails due to CORS

**Solution:** Update CORS settings
```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 4. Performance Issues

**Problem:** Slow authentication checks

**Optimization:**
- Cache decoded tokens (với caution về security)
- Optimize JWT verification
- Use shorter tokens
- Implement token refresh to avoid frequent logins

---

## Best Practices

### 1. Security
- ✅ Always use HTTPS in production
- ✅ Set reasonable token expiry times
- ✅ Clear tokens on logout
- ✅ Validate tokens on sensitive operations
- ✅ Implement rate limiting for login
- ✅ Monitor for suspicious activities

### 2. User Experience
- ✅ Show clear session status
- ✅ Warning before session expires
- ✅ Graceful handling of expired sessions
- ✅ Remember-me functionality (optional)
- ✅ Smooth login/logout transitions

### 3. Development
- ✅ Comprehensive error handling
- ✅ Proper logging of auth events
- ✅ Easy token debugging
- ✅ Consistent auth patterns
- ✅ Good test coverage

---

## References

- [JWT.io - JWT Introduction](https://jwt.io/introduction)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Next.js Authentication](https://nextjs.org/docs/authentication)
- [MDN Web Docs - Session Storage](https://developer.mozilla.org/en-US/docs/Web/API/Window/sessionStorage)

---

**Cập nhật lần cuối:** January 15, 2026  
**Phiên bản:** 1.0.0