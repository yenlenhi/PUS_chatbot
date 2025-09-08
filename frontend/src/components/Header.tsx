import React from 'react';
import Image from 'next/image';

const Header = () => {
  return (
    <header className="bg-gradient-to-r from-yellow-400 to-yellow-500">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo và tên trường */}
          <div className="flex items-center space-x-4">
            {/* Logo */}
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg">
              <div className="w-16 h-16 bg-gradient-to-br from-red-600 to-red-700 rounded-full flex items-center justify-center relative">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center relative">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-yellow-400 text-lg font-bold">★</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Tên trường */}
            <div className="text-left">
              <h1 className="text-2xl font-bold text-red-700 leading-tight">
                TRƯỜNG ĐẠI HỌC AN NINH NHÂN DÂN
              </h1>
              <h2 className="text-lg font-semibold text-green-700 mt-1">
                PEOPLE'S SECURITY UNIVERSITY
              </h2>
            </div>
          </div>
          
          {/* Hình ảnh tòa nhà */}
          <div className="hidden lg:block">
            <div className="w-48 h-20 bg-gradient-to-r from-orange-200 to-orange-300 rounded-lg shadow-lg flex items-center justify-center">
              <div className="text-orange-800 text-sm font-medium text-center">
                Hình ảnh tòa nhà<br />trường học
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
