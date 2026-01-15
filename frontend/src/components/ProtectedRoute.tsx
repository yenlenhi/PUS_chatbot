/**
 * Protected Route Component
 * Wraps components that require authentication
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { checkSession, hasScope } from '@/utils/auth';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredScope?: string;
  fallbackUrl?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredScope = 'user',
  fallbackUrl = '/admin'
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const validateAccess = () => {
      const session = checkSession();
      
      // Check if authenticated
      if (!session.isAuthenticated) {
        console.log('Not authenticated, redirecting to login');
        router.push(fallbackUrl);
        return;
      }
      
      // Check if session is expired
      if (session.isExpired) {
        console.log('Session expired, redirecting to login');
        alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
        router.push(fallbackUrl);
        return;
      }
      
      // Check required scope
      if (requiredScope && !hasScope(requiredScope)) {
        console.log(`Missing required scope: ${requiredScope}`);
        router.push('/unauthorized');
        return;
      }
      
      // All checks passed
      setIsAuthorized(true);
      setIsLoading(false);
    };

    validateAccess();
    
    // Set up periodic session check (every 5 minutes)
    const interval = setInterval(validateAccess, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [router, requiredScope, fallbackUrl]);

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-red-600 mx-auto mb-4" />
          <p className="text-gray-600">Đang xác thực...</p>
        </div>
      </div>
    );
  }

  // Don't render anything if not authorized (redirect is happening)
  if (!isAuthorized) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-red-600 mx-auto mb-4" />
          <p className="text-gray-600">Đang chuyển hướng...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;