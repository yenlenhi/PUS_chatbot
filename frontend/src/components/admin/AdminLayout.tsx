'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import AdminSidebar from './AdminSidebar';
import Image from 'next/image';
import { LogOut, Menu, X, Home, Loader2, Star, Clock } from 'lucide-react';
import { useLanguage } from '@/i18n/LanguageContext';
import LanguageSwitcher from '@/i18n/LanguageSwitcher';
import { checkSession, clearSession, isTokenExpiringSoon, getTimeToExpiry } from '@/utils/auth';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout = ({ children }: AdminLayoutProps) => {
  const router = useRouter();
  const pathname = usePathname();
  const { t } = useLanguage();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [sessionWarning, setSessionWarning] = useState(false);
  const [timeToExpiry, setTimeToExpiry] = useState(0);

  useEffect(() => {
    const validateSession = () => {
      const session = checkSession();
      
      if (session.isAuthenticated) {
        setIsAuthenticated(true);
        
        // Check if session is expiring soon
        const expiringSoon = isTokenExpiringSoon(30); // 30 minutes warning
        setSessionWarning(expiringSoon);
        setTimeToExpiry(getTimeToExpiry());
      } else {
        setIsAuthenticated(false);
        router.push('/admin');
      }
    };

    validateSession();
    setIsLoading(false);

    // Check session every minute
    const interval = setInterval(validateSession, 60 * 1000);
    
    return () => clearInterval(interval);
  }, [router]);

  const handleLogout = () => {
    if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
      clearSession();
      router.push('/admin');
    }
  };

  const formatTimeRemaining = (ms: number): string => {
    const minutes = Math.floor(ms / 60000);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    }
    return `${minutes}m`;
  };

  const getPageTitle = () => {
    if (pathname?.includes('dashboard')) return t('dashboard');
    if (pathname?.includes('chat-history')) return t('chatHistory');
    if (pathname?.includes('documents')) return t('documents');
    if (pathname?.includes('feedback')) return t('feedback');
    return t('admin');
  };

  // Show loading spinner
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-yellow-400 mx-auto mb-4" />
          <p className="text-yellow-200">{t('loading')}</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-900">
      {/* Decorative Background Elements */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-red-600/20 rounded-full blur-3xl"></div>
        {/* Stars decoration */}
        <Star className="absolute top-20 right-20 w-16 h-16 text-yellow-400/40 fill-yellow-400/40" />
        <Star className="absolute top-40 right-40 w-8 h-8 text-yellow-400/30 fill-yellow-400/30" />
        <Star className="absolute bottom-40 left-20 w-12 h-12 text-yellow-400/30 fill-yellow-400/30" />
      </div>
      {/* Top Header */}
      <header className="bg-gradient-to-r from-red-900/95 via-red-800/95 to-red-900/95 backdrop-blur-md shadow-xl border-b border-yellow-500/30 fixed top-0 left-0 right-0 z-30">
        <div className="flex items-center justify-between h-14 sm:h-16 px-2 sm:px-4">
          <div className="flex items-center space-x-2 sm:space-x-4 min-w-0 flex-1">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="hidden lg:block p-1.5 sm:p-2 hover:bg-yellow-500/20 rounded-lg transition-colors"
            >
              <Menu className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-200" />
            </button>
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-1.5 sm:p-2 hover:bg-yellow-500/20 rounded-lg transition-colors flex-shrink-0"
            >
              {isMobileMenuOpen ? (
                <X className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-200" />
              ) : (
                <Menu className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-200" />
              )}
            </button>
            <div className="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
              <Image
                src="/assests/logo-main.png"
                alt="Logo"
                width={32}
                height={32}
                className="w-8 h-8 sm:w-10 sm:h-10 object-contain flex-shrink-0"
              />
              <div className="min-w-0 flex-1">
                <h1 className="text-sm sm:text-lg font-bold text-white truncate">Quản trị hệ thống</h1>
                <p className="text-xs text-yellow-200/80 hidden md:block truncate">Trường ĐH An ninh Nhân dân</p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-1 sm:space-x-2 md:space-x-4 flex-shrink-0">
            {/* Session Warning */}
            {sessionWarning && (
              <div className="flex items-center space-x-1 px-2 py-1 bg-yellow-500/20 text-yellow-200 rounded-lg text-xs border border-yellow-500/30">
                <Clock className="w-3 h-3" />
                <span className="hidden sm:inline">Còn {formatTimeRemaining(timeToExpiry)}</span>
              </div>
            )}
            <div className="hidden md:block text-right">
              <p className="text-sm font-medium text-white">Admin</p>
              <p className="text-xs text-yellow-200/80">Quản trị viên</p>
            </div>
            <div className="hidden sm:block">
              <LanguageSwitcher />
            </div>
            <Link
              href="/"
              className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              title={t('backToHome')}
            >
              <Home className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden md:inline text-sm">{t('backToHome')}</span>
            </Link>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-1.5 sm:py-2 bg-yellow-500 hover:bg-yellow-600 text-red-900 rounded-lg transition-colors shadow-sm font-medium"
            >
              <LogOut className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline text-sm">{t('logout')}</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex pt-14 sm:pt-16 min-h-screen">
        {/* Sidebar - Desktop */}
        <aside
          className={`hidden lg:block fixed left-0 top-14 sm:top-16 bottom-0 bg-white shadow-lg border-r border-gray-200 transition-all duration-300 z-20 ${
            isSidebarOpen ? 'w-64' : 'w-0 overflow-hidden'
          }`}
        >
          <AdminSidebar />
        </aside>

        {/* Mobile Menu Overlay */}
        {isMobileMenuOpen && (
          <div 
            className="lg:hidden fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}

        {/* Sidebar - Mobile */}
        <aside 
          className={`lg:hidden fixed left-0 top-14 sm:top-16 bottom-0 w-[280px] max-w-[80vw] bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out ${
            isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <AdminSidebar onItemClick={() => setIsMobileMenuOpen(false)} />
        </aside>

        {/* Main Content */}
        <main
          className={`flex-1 min-h-[calc(100vh-3.5rem)] sm:min-h-[calc(100vh-4rem)] transition-all duration-300 ${
            isSidebarOpen ? 'lg:ml-64' : 'lg:ml-0'
          }`}
        >
          <div className="p-2 sm:p-4 md:p-6 lg:p-8 min-h-full">
            <div className="mb-4 sm:mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-white">{getPageTitle()}</h2>
              <p className="text-yellow-200/80 mt-1 text-sm sm:text-base">{t('overview')}</p>
            </div>
            <div className="bg-white/95 backdrop-blur-md rounded-lg sm:rounded-xl p-3 sm:p-4 min-h-[200px] shadow-xl border border-white/20">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
