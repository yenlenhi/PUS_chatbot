'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, MessageSquare, FileText, ThumbsUp } from 'lucide-react';

interface AdminSidebarProps {
  onItemClick?: () => void;
}

const AdminSidebar = ({ onItemClick }: AdminSidebarProps) => {
  const pathname = usePathname();

  const menuItems = [
    {
      href: '/admin/dashboard',
      icon: LayoutDashboard,
      label: 'Dashboard',
      description: 'Tổng quan hệ thống'
    },
    {
      href: '/admin/chat-history',
      icon: MessageSquare,
      label: 'Lịch sử chat',
      description: 'Quản lý hội thoại'
    },
    {
      href: '/admin/feedback',
      icon: ThumbsUp,
      label: 'Phản hồi',
      description: 'Đánh giá & cải thiện'
    },
    {
      href: '/admin/documents',
      icon: FileText,
      label: 'Tài liệu',
      description: 'Quản lý tài liệu'
    }
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <div className="h-full flex flex-col py-6">
      <nav className="flex-1 px-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onItemClick}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                active
                  ? 'bg-red-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-red-50 hover:text-red-600'
              }`}
            >
              <Icon className={`w-5 h-5 ${active ? 'text-white' : 'text-gray-500'}`} />
              <div className="flex-1">
                <div className={`font-medium ${active ? 'text-white' : 'text-gray-900'}`}>
                  {item.label}
                </div>
                <div className={`text-xs ${active ? 'text-red-100' : 'text-gray-500'}`}>
                  {item.description}
                </div>
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="px-4 py-4 border-t border-gray-200">
        <div className="bg-gradient-to-r from-red-50 to-blue-50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-1">PSU ChatBot</h3>
          <p className="text-xs text-gray-600">Hệ thống quản trị phiên bản 1.0</p>
        </div>
      </div>
    </div>
  );
};

export default AdminSidebar;
