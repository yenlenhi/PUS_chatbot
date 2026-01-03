'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, MessageSquare, FileText, ThumbsUp, FolderOpen } from 'lucide-react';
import { useLanguage } from '@/i18n/LanguageContext';

interface AdminSidebarProps {
  onItemClick?: () => void;
}

const AdminSidebar = ({ onItemClick }: AdminSidebarProps) => {
  const pathname = usePathname();
  const { t, language } = useLanguage();

  const menuItems = [
    {
      href: '/admin/dashboard',
      icon: LayoutDashboard,
      label: t('dashboard'),
      description: language === 'vi' ? 'Tổng quan hệ thống' : 'System Overview'
    },
    {
      href: '/admin/chat-history',
      icon: MessageSquare,
      label: t('chatHistory'),
      description: language === 'vi' ? 'Quản lý hội thoại' : 'Conversation Management'
    },
    {
      href: '/admin/feedback',
      icon: ThumbsUp,
      label: t('feedback'),
      description: language === 'vi' ? 'Đánh giá & cải thiện' : 'Feedback & Improvement'
    },
    {
      href: '/admin/documents',
      icon: FileText,
      label: t('documents'),
      description: language === 'vi' ? 'Quản lý tài liệu' : 'Document Management'
    },
    {
      href: '/admin/attachments',
      icon: FolderOpen,
      label: language === 'vi' ? 'File đính kèm' : 'Attachments',
      description: language === 'vi' ? 'Quản lý forms & templates' : 'Manage forms & templates'
    }
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <div className="h-full flex flex-col py-3 sm:py-6">
      <nav className="flex-1 px-2 sm:px-4 space-y-1 sm:space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onItemClick}
              className={`flex items-center space-x-2 sm:space-x-3 px-3 sm:px-4 py-2.5 sm:py-3 rounded-lg transition-all duration-200 ${
                active
                  ? 'bg-red-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-red-50 hover:text-red-600'
              }`}
            >
              <Icon className={`w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0 ${active ? 'text-white' : 'text-gray-500'}`} />
              <div className="flex-1 min-w-0">
                <div className={`font-medium text-sm sm:text-base truncate ${active ? 'text-white' : 'text-gray-900'}`}>
                  {item.label}
                </div>
                <div className={`text-xs truncate ${active ? 'text-red-100' : 'text-gray-500'}`}>
                  {item.description}
                </div>
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="px-2 sm:px-4 py-3 sm:py-4 border-t border-gray-200">
        <div className="bg-gradient-to-r from-red-50 to-blue-50 rounded-lg p-3 sm:p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-1">PSU ChatBot</h3>
          <p className="text-xs text-gray-600">
            {language === 'vi' ? 'Hệ thống quản trị phiên bản 1.0' : 'Admin System v1.0'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminSidebar;
