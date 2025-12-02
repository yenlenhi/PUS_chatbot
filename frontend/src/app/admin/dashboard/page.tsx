'use client';

import React from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import { Users, MessageSquare, FileText, TrendingUp, Activity, Clock } from 'lucide-react';

const DashboardPage = () => {
  const stats = [
    {
      title: 'Tổng số cuộc hội thoại',
      value: '1,234',
      change: '+12.5%',
      icon: MessageSquare,
      color: 'bg-blue-500',
      trend: 'up'
    },
    {
      title: 'Người dùng hoạt động',
      value: '856',
      change: '+8.2%',
      icon: Users,
      color: 'bg-green-500',
      trend: 'up'
    },
    {
      title: 'Tài liệu hệ thống',
      value: '342',
      change: '+3.1%',
      icon: FileText,
      color: 'bg-purple-500',
      trend: 'up'
    },
    {
      title: 'Thời gian phản hồi TB',
      value: '1.2s',
      change: '-15.3%',
      icon: Clock,
      color: 'bg-yellow-500',
      trend: 'down'
    }
  ];

  const recentActivities = [
    { time: '10 phút trước', action: 'Người dùng mới đặt câu hỏi về tuyển sinh', type: 'chat' },
    { time: '25 phút trước', action: 'Tài liệu "Quy chế đào tạo 2024" được cập nhật', type: 'document' },
    { time: '1 giờ trước', action: '5 cuộc hội thoại mới được khởi tạo', type: 'chat' },
    { time: '2 giờ trước', action: 'Hệ thống backup dữ liệu thành công', type: 'system' },
    { time: '3 giờ trước', action: 'Người dùng tìm kiếm thông tin về học phí', type: 'chat' }
  ];

  const popularQuestions = [
    { question: 'Điều kiện tuyển sinh năm 2025?', count: 156 },
    { question: 'Học phí của trường như thế nào?', count: 142 },
    { question: 'Các ngành đào tạo của trường?', count: 128 },
    { question: 'Thông tin về ký túc xá?', count: 98 },
    { question: 'Cơ hội việc làm sau tốt nghiệp?', count: 87 }
  ];

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="bg-white rounded-xl shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <span className={`text-sm font-medium ${stat.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {stat.change}
                  </span>
                </div>
                <h3 className="text-gray-600 text-sm mb-1">{stat.title}</h3>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            );
          })}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Activity Chart */}
          <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Hoạt động theo giờ</h3>
              <Activity className="w-5 h-5 text-gray-400" />
            </div>
            <div className="space-y-4">
              {[
                { hour: '08:00', value: 65 },
                { hour: '10:00', value: 85 },
                { hour: '12:00', value: 45 },
                { hour: '14:00', value: 75 },
                { hour: '16:00', value: 90 },
                { hour: '18:00', value: 55 }
              ].map((item, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <span className="text-sm text-gray-600 w-16">{item.hour}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-red-500 to-red-600 h-3 rounded-full transition-all duration-500"
                      style={{ width: `${item.value}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Popular Questions */}
          <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Câu hỏi phổ biến</h3>
              <TrendingUp className="w-5 h-5 text-gray-400" />
            </div>
            <div className="space-y-4">
              {popularQuestions.map((item, index) => (
                <div key={index} className="flex items-start space-x-3 pb-3 border-b border-gray-100 last:border-0">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-xs font-bold">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 line-clamp-2">{item.question}</p>
                    <p className="text-xs text-gray-500 mt-1">{item.count} lượt hỏi</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Hoạt động gần đây</h3>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <div key={index} className="flex items-start space-x-4 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                  activity.type === 'chat' ? 'bg-blue-500' :
                  activity.type === 'document' ? 'bg-green-500' : 'bg-gray-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};

export default DashboardPage;
