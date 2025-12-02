'use client';

import React from 'react';
import Image from 'next/image';
import { Phone, Mail, Clock } from 'lucide-react';

const Header = () => {
  return (
    <header className="relative">
      {/* Top bar với thông tin liên hệ */}
      <div className="bg-red-800 text-white py-2">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap items-center justify-between text-sm">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Phone className="w-4 h-4" />
                <span>024.3854.2222</span>
              </div>
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4" />
                <span>info@psu.edu.vn</span>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span>Thứ 2 - Thứ 6: 7:30 - 17:00</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main header với background */}
      <div className="relative bg-gradient-to-r from-yellow-400 via-yellow-500 to-yellow-400 overflow-hidden">
        {/* Pattern overlay */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>

        <div className="container mx-auto px-4 py-4 relative z-10">
          <div className="flex items-center justify-between">
            {/* Logo và tên trường */}
            <div className="flex items-center space-x-4">
              {/* Logo Bộ Công An */}
              <div className="relative w-20 h-20 flex-shrink-0">
                <Image
                  src="/assests/Logo-Bo-Cong-An.webp"
                  alt="Logo Bộ Công An"
                  fill
                  className="object-contain drop-shadow-lg"
                  priority
                />
              </div>
              
              {/* Tên trường */}
              <div className="text-left">
                <div className="text-xs text-red-700 font-semibold uppercase tracking-wider mb-1">
                  Bộ Công An - Việt Nam
                </div>
                <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-red-700 leading-tight drop-shadow-sm">
                  TRƯỜNG ĐẠI HỌC AN NINH NHÂN DÂN
                </h1>
                <h2 className="text-sm md:text-base lg:text-lg font-semibold text-green-700 mt-1">
                  PEOPLE&apos;S SECURITY UNIVERSITY
                </h2>
                <div className="flex items-center mt-1 space-x-2">
                  <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
                  <span className="text-xs text-red-600 font-medium">Trực tuyến</span>
                </div>
              </div>
            </div>
            
            {/* Logo chính của trường */}
            <div className="hidden lg:flex items-center space-x-4">
              <div className="relative w-24 h-24 flex-shrink-0 bg-white rounded-full p-2 shadow-xl">
                <Image
                  src="/assests/logo-main.png"
                  alt="Logo Trường Đại học An ninh Nhân dân"
                  fill
                  className="object-contain"
                  priority
                />
              </div>
            </div>
          </div>
        </div>

        {/* Decorative bottom wave */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg className="w-full h-4" viewBox="0 0 1200 10" preserveAspectRatio="none">
            <path d="M0,10 L1200,10 L1200,0 Q600,10 0,0 Z" fill="#dc2626" />
          </svg>
        </div>
      </div>
    </header>
  );
};

export default Header;
