/**
 * Authentication utilities for frontend
 * Handles JWT tokens, session management, and auth state
 */

interface SessionData {
  isAuthenticated: boolean;
  token: string | null;
  username: string | null;
  isExpired: boolean;
  expiryTime: Date | null;
  loginTime: Date | null;
}

interface TokenPayload {
  username: string;
  user_id: string;
  scopes: string[];
  exp: number;
  iat: number;
  jti?: string;
}

/**
 * Check current session status
 */
export const checkSession = (): SessionData => {
  try {
    const isAuth = sessionStorage.getItem('isAdminAuthenticated') === 'true';
    const token = sessionStorage.getItem('adminToken');
    const username = sessionStorage.getItem('username');
    const expiryString = sessionStorage.getItem('tokenExpiry');
    const loginTimeString = sessionStorage.getItem('loginTime');
    
    let isExpired = false;
    let expiryTime = null;
    let loginTime = null;
    
    if (expiryString) {
      expiryTime = new Date(expiryString);
      isExpired = new Date() > expiryTime;
    }
    
    if (loginTimeString) {
      loginTime = new Date(loginTimeString);
    }
    
    // If expired, clear session
    if (isExpired) {
      clearSession();
      return {
        isAuthenticated: false,
        token: null,
        username: null,
        isExpired: true,
        expiryTime: null,
        loginTime: null
      };
    }
    
    return {
      isAuthenticated: isAuth && !!token && !isExpired,
      token,
      username,
      isExpired,
      expiryTime,
      loginTime
    };
  } catch (error) {
    console.error('Session check error:', error);
    clearSession();
    return {
      isAuthenticated: false,
      token: null,
      username: null,
      isExpired: true,
      expiryTime: null,
      loginTime: null
    };
  }
};

/**
 * Clear all session data
 */
export const clearSession = () => {
  sessionStorage.removeItem('isAdminAuthenticated');
  sessionStorage.removeItem('adminToken');
  sessionStorage.removeItem('username');
  sessionStorage.removeItem('tokenExpiry');
  sessionStorage.removeItem('loginTime');
};

/**
 * Get authorization header for API requests
 */
export const getAuthHeader = (): { Authorization?: string } => {
  const { isAuthenticated, token } = checkSession();
  
  if (isAuthenticated && token) {
    return { Authorization: `Bearer ${token}` };
  }
  
  return {};
};

/**
 * Decode JWT token payload (without verification)
 * Use only for client-side display purposes
 */
export const decodeTokenPayload = (token: string): TokenPayload | null => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }
    
    const payload = parts[1];
    // Add padding if needed
    const paddedPayload = payload + '='.repeat((4 - (payload.length % 4)) % 4);
    const decoded = JSON.parse(atob(paddedPayload));
    
    return decoded as TokenPayload;
  } catch (error) {
    console.error('Token decode error:', error);
    return null;
  }
};

/**
 * Check if user has specific scope/role
 */
export const hasScope = (requiredScope: string): boolean => {
  const { token } = checkSession();
  if (!token) return false;
  
  const payload = decodeTokenPayload(token);
  if (!payload || !payload.scopes) return false;
  
  return payload.scopes.includes(requiredScope);
};

/**
 * Check if user is admin
 */
export const isAdmin = (): boolean => {
  return hasScope('admin');
};

/**
 * Get token expiry time
 */
export const getTokenExpiry = (): Date | null => {
  const { token } = checkSession();
  if (!token) return null;
  
  const payload = decodeTokenPayload(token);
  if (!payload || !payload.exp) return null;
  
  return new Date(payload.exp * 1000); // Convert Unix timestamp to Date
};

/**
 * Get time remaining until token expires
 */
export const getTimeToExpiry = (): number => {
  const expiry = getTokenExpiry();
  if (!expiry) return 0;
  
  return Math.max(0, expiry.getTime() - Date.now());
};

/**
 * Check if token expires within specified minutes
 */
export const isTokenExpiringSoon = (minutes: number = 30): boolean => {
  const timeToExpiry = getTimeToExpiry();
  return timeToExpiry > 0 && timeToExpiry < (minutes * 60 * 1000);
};

/**
 * API client with automatic auth header injection
 */
export const apiClient = {
  async request(url: string, options: RequestInit = {}) {
    const session = checkSession();
    
    if (!session.isAuthenticated) {
      throw new Error('Not authenticated');
    }
    
    if (session.isExpired) {
      clearSession();
      window.location.href = '/admin';
      throw new Error('Session expired');
    }
    
    // Add auth header
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
      console.warn('Received 401, clearing session');
      clearSession();
      window.location.href = '/admin';
      throw new Error('Authentication required');
    }
    
    return response;
  },

  async get(url: string) {
    return this.request(url, { method: 'GET' });
  },

  async post(url: string, data?: any) {
    return this.request(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  async put(url: string, data?: any) {
    return this.request(url, {
      method: 'PUT', 
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  async delete(url: string) {
    return this.request(url, { method: 'DELETE' });
  }
};

/**
 * Hook for auth state management
 */
export const useAuth = () => {
  const session = checkSession();
  
  return {
    ...session,
    hasScope,
    isAdmin: isAdmin(),
    clearSession,
    apiClient,
    timeToExpiry: getTimeToExpiry(),
    isExpiringSoon: isTokenExpiringSoon(),
  };
};

/**
 * Session debug helper
 */
export const debugSession = () => {
  const session = checkSession();
  const token = session.token;
  let payload = null;
  
  if (token) {
    payload = decodeTokenPayload(token);
  }
  
  console.log('Session Debug:', {
    session,
    tokenPayload: payload,
    timeToExpiry: getTimeToExpiry(),
    isExpiringSoon: isTokenExpiringSoon(),
    hasAdminScope: isAdmin()
  });
  
  return { session, payload };
};