'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { Lock, User, Home, ArrowLeft, CheckCircle, Star } from 'lucide-react';

const AdminLoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const router = useRouter();

  // Check if already authenticated
  useEffect(() => {
    const auth = sessionStorage.getItem('isAdminAuthenticated');
    if (auth === 'true') {
      router.push('/admin/dashboard');
    } else {
      setIsChecking(false);
    }
  }, [router]);

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
        const errorData = await response.json();
        setError('Tên đăng nhập hoặc mật khẩu không đúng!');
        setIsLoading(false);
        return;
      }

      const data = await response.json();
      
      // Store authentication token
      sessionStorage.setItem('isAdminAuthenticated', 'true');
      sessionStorage.setItem('adminToken', data.access_token);
      sessionStorage.setItem('username', username);
      
      // Redirect to dashboard
      setTimeout(() => {
        router.push('/admin/dashboard');
      }, 500);
    } catch (err) {
      console.error('Login error:', err);
      setError('Lỗi kết nối đến máy chủ. Vui lòng thử lại!');
      setIsLoading(false);
    }
  };

  // Show loading while checking auth
  if (isChecking) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white">Đang kiểm tra...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-900 flex items-center justify-center p-4">
      {/* Back to Home - Fixed top left (Desktop only) */}
      <Link
        href="/"
        className="hidden md:flex fixed top-4 left-4 items-center gap-2 px-4 py-2 bg-white/90 hover:bg-white text-gray-700 rounded-lg transition-colors shadow-md border border-gray-200 text-sm font-medium z-20"
      >
        <ArrowLeft className="w-4 h-4" />
        <Home className="w-4 h-4" />
        <span>Trang chủ</span>
      </Link>

      {/* Main Container */}
      <div className="w-full max-w-5xl mx-auto relative z-10">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col lg:flex-row">
          
          {/* LEFT SIDE - Branding Section */}
          <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-red-600 to-red-700 p-12 flex-col justify-between relative overflow-hidden">
            {/* Decorative shapes */}
            <div className="absolute top-0 right-0 w-40 h-40 bg-white/10 rounded-full -mr-20 -mt-20"></div>
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/10 rounded-full -ml-16 -mb-16"></div>
            <div className="absolute bottom-10 right-10 w-24 h-24 bg-white/5 rounded-full"></div>
            
            {/* Decorative Stars */}
            <Star className="absolute top-20 right-20 w-10 h-10 text-yellow-300/40 fill-yellow-300/40" />
            <Star className="absolute top-40 right-40 w-6 h-6 text-yellow-300/30 fill-yellow-300/30" />
            <Star className="absolute bottom-40 left-20 w-8 h-8 text-yellow-300/30 fill-yellow-300/30" />
            <Star className="absolute bottom-20 right-32 w-5 h-5 text-yellow-300/25 fill-yellow-300/25" />
            <Star className="absolute top-1/2 right-1/4 w-7 h-7 text-yellow-300/20 fill-yellow-300/20" />

            <div className="relative z-10">
              {/* Logo and Title */}
              <div className="mb-8 flex items-center gap-4">
                <Image
                  src="/assests/logo-main.png"
                  alt="Logo Trường Đại học An ninh Nhân dân"
                  width={80}
                  height={80}
                  className="w-20 h-20 object-contain filter drop-shadow-lg"
                />
                <div>
                  <h1 className="text-white text-4xl font-bold mb-2">
                    HỆ THỐNG<br />QUẢN TRỊ
                  </h1>
                  <div className="w-16 h-1 bg-white rounded-full"></div>
                </div>
              </div>

              <div className="space-y-4">
                <h2 className="text-amber-300 text-xl font-semibold">Chào mừng đến với</h2>
                <p className="text-white/85 text-base leading-relaxed font-light">
                  Trường Đại học An ninh Nhân dân. Quản lý tài liệu, cuộc hội thoại, phản hồi và hơn thế nữa một cách dễ dàng.
                </p>

                <div className="pt-6 space-y-3">
                  <div className="flex items-center gap-3 text-white/95 font-medium">
                    <CheckCircle className="w-5 h-5 flex-shrink-0 text-amber-300" />
                    <span>Quản lý tài liệu hiệu quả</span>
                  </div>
                  <div className="flex items-center gap-3 text-white/95 font-medium">
                    <CheckCircle className="w-5 h-5 flex-shrink-0 text-amber-300" />
                    <span>Theo dõi lịch sử chat</span>
                  </div>
                  <div className="flex items-center gap-3 text-white/95 font-medium">
                    <CheckCircle className="w-5 h-5 flex-shrink-0 text-amber-300" />
                    <span>Quản lý phản hồi người dùng</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="relative z-10 pt-8 border-t border-white/20">
              <p className="text-white/80 text-sm">© 2026 Trường Đại học An ninh Nhân dân. All rights reserved.</p>
            </div>
          </div>

          {/* RIGHT SIDE - Login Form Section */}
          <div className="w-full lg:w-1/2 p-8 md:p-12 flex flex-col justify-center">
            {/* Logo for Mobile */}
            <div className="lg:hidden flex justify-center mb-6">
              <Image
                src="/assests/logo-main.png"
                alt="Logo"
                width={56}
                height={56}
                className="w-14 h-14 object-contain"
              />
            </div>

            {/* Login Heading */}
            <div className="mb-8">
              <h2 className="text-3xl md:text-4xl font-bold text-red-600 mb-2">
                Đăng nhập
              </h2>
              <p className="text-gray-600">
                Vui lòng nhập thông tin để truy cập hệ thống
              </p>
            </div>

            {/* Login Form */}
            <form onSubmit={handleLogin} className="space-y-5">
              {/* Username Input */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  Tên đăng nhập
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="block w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900 placeholder-gray-400 text-base transition-all"
                    placeholder="Nhập tên đăng nhập"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* Password Input */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Mật khẩu
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900 placeholder-gray-400 text-base transition-all"
                    placeholder="Nhập mật khẩu"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* Remember Me Checkbox */}
              <div className="flex items-center">
                <input
                  id="remember"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-5 h-5 text-red-600 border-gray-300 rounded cursor-pointer"
                  disabled={isLoading}
                />
                <label htmlFor="remember" className="ml-2 text-sm text-gray-600 cursor-pointer">
                  Ghi nhớ tôi
                </label>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-md hover:shadow-lg text-base"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Đang đăng nhập...
                  </span>
                ) : (
                  'ĐĂNG NHẬP'
                )}
              </button>
            </form>

            {/* Footer Links */}
            <div className="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between text-sm">
              <span className="text-gray-600">
                Người dùng mới? <a href="#" className="text-red-600 hover:text-red-700 font-medium">Đăng ký</a>
              </span>
              <a href="#" className="text-gray-600 hover:text-red-600">Quên mật khẩu?</a>
            </div>

            {/* Back to Home - Mobile only */}
            <div className="md:hidden mt-6 pt-6 border-t border-gray-200">
              <Link
                href="/"
                className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium"
              >
                <ArrowLeft className="w-4 h-4" />
                <Home className="w-4 h-4" />
                <span>Trang chủ</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginPage;
