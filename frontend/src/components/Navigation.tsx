'use client';

import React, { useState } from 'react';
import { Search, Menu, X } from 'lucide-react';
import { MENU_ITEMS } from '@/data/constants';

const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <nav className="bg-green-700 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          {/* Desktop Menu */}
          <div className="hidden lg:flex items-center space-x-1">
            {MENU_ITEMS.map((item, index) => (
              <a
                key={index}
                href={item.href}
                className="px-3 py-2 text-white text-sm font-medium hover:bg-green-600 transition-colors duration-200 rounded"
              >
                {item.title}
              </a>
            ))}
          </div>

          {/* Search Box */}
          <div className="flex items-center space-x-4">
            <div className="relative">
              <input
                type="text"
                placeholder="TÌM KIẾM"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-48 px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <Search className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="lg:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-white hover:text-gray-200 focus:outline-none"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="lg:hidden bg-green-800 border-t border-green-600">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {MENU_ITEMS.map((item, index) => (
                <a
                  key={index}
                  href={item.href}
                  className="block px-3 py-2 text-white text-sm font-medium hover:bg-green-600 transition-colors duration-200 rounded"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.title}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
