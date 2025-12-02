'use client';

import React, { useState, useEffect, useCallback } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import { Search, Filter, Download, Eye, Calendar, User, MessageSquare, RefreshCw, Trash2, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { chatHistoryAPI } from '@/services/api';
import { ConversationSummary, ConversationDetail, ChatHistoryStats } from '@/types/api';

const ChatHistoryPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [stats, setStats] = useState<ChatHistoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 10;
  
  // Modal states
  const [selectedConversation, setSelectedConversation] = useState<ConversationDetail | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  
  // Export states
  const [exporting, setExporting] = useState(false);

  const filters = [
    { value: 'all', label: 'Tất cả' },
    { value: 'active', label: 'Đang hoạt động' },
    { value: 'completed', label: 'Đã hoàn thành' }
  ];

  // Fetch conversations
  const fetchConversations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const offset = (currentPage - 1) * itemsPerPage;
      const response = await chatHistoryAPI.getConversations(
        itemsPerPage,
        offset,
        searchTerm || undefined,
        selectedFilter !== 'all' ? selectedFilter : undefined
      );
      
      setConversations(response.conversations || []);
      setTotalItems(response.total || 0);
      
      // Update stats from response
      if (response.stats) {
        setStats({
          total_conversations: response.stats.total_conversations,
          total_messages: response.stats.total_messages,
          today_conversations: response.stats.today_conversations,
          active_conversations: response.stats.active_conversations,
          avg_confidence: 0,
          avg_processing_time: 0,
          popular_topics: []
        });
      }
    } catch (err) {
      console.error('Error fetching conversations:', err);
      setError('Không thể tải lịch sử chat. Vui lòng thử lại sau.');
      setConversations([]);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, selectedFilter]);

  // Initial fetch
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  // View conversation detail
  const handleViewDetail = async (conversationId: string) => {
    setLoadingDetail(true);
    try {
      const detail = await chatHistoryAPI.getConversationDetail(conversationId);
      setSelectedConversation(detail);
      setShowDetailModal(true);
    } catch (err) {
      console.error('Error fetching conversation detail:', err);
      alert('Không thể tải chi tiết cuộc hội thoại');
    } finally {
      setLoadingDetail(false);
    }
  };

  // Delete conversation
  const handleDelete = async (conversationId: string) => {
    if (!confirm('Bạn có chắc chắn muốn xóa cuộc hội thoại này?')) return;
    
    try {
      await chatHistoryAPI.deleteConversation(conversationId);
      fetchConversations(); // Refresh list
    } catch (err) {
      console.error('Error deleting conversation:', err);
      alert('Không thể xóa cuộc hội thoại');
    }
  };

  // Export conversations
  const handleExport = async () => {
    setExporting(true);
    try {
      const data = await chatHistoryAPI.exportConversations();
      
      // Download as JSON
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting:', err);
      alert('Không thể xuất dữ liệu');
    } finally {
      setExporting(false);
    }
  };

  // Format date
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Calculate total pages
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Search and Filter Bar */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Tìm kiếm theo nội dung tin nhắn..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900"
              />
            </div>

            {/* Filter */}
            <div className="flex items-center space-x-3">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={selectedFilter}
                onChange={(e) => {
                  setSelectedFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900"
              >
                {filters.map(filter => (
                  <option key={filter.value} value={filter.value}>
                    {filter.label}
                  </option>
                ))}
              </select>

              <button 
                onClick={fetchConversations}
                className="px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors flex items-center space-x-2"
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Làm mới</span>
              </button>

              <button 
                onClick={handleExport}
                className="px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center space-x-2 shadow-sm"
                disabled={exporting}
              >
                <Download className={`w-4 h-4 ${exporting ? 'animate-pulse' : ''}`} />
                <span className="hidden sm:inline">{exporting ? 'Đang xuất...' : 'Export'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Tổng cuộc hội thoại</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats?.total_conversations || 0}
                </p>
              </div>
              <MessageSquare className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Đang hoạt động</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {stats?.active_conversations || 0}
                </p>
              </div>
              <User className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Hôm nay</p>
                <p className="text-2xl font-bold text-purple-600 mt-1">
                  {stats?.today_conversations || 0}
                </p>
              </div>
              <Calendar className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Tổng tin nhắn</p>
                <p className="text-2xl font-bold text-orange-600 mt-1">
                  {stats?.total_messages || 0}
                </p>
              </div>
              <MessageSquare className="w-8 h-8 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        )}

        {/* Chat History Table */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID Cuộc hội thoại
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Câu hỏi đầu tiên
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Số tin nhắn
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Thời gian
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trạng thái
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Hành động
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <RefreshCw className="w-8 h-8 text-gray-400 mx-auto mb-4 animate-spin" />
                      <p className="text-gray-600">Đang tải...</p>
                    </td>
                  </tr>
                ) : conversations.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">Không tìm thấy cuộc hội thoại nào</p>
                    </td>
                  </tr>
                ) : (
                  conversations.map((chat) => (
                    <tr key={chat.conversation_id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-mono text-gray-900">
                          {chat.conversation_id.substring(0, 8)}...
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-gray-900 line-clamp-2">
                          {chat.first_query || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">{chat.message_count} tin nhắn</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatDate(chat.last_message)}</div>
                        <div className="text-xs text-gray-500">
                          {chat.total_processing_time ? `${chat.total_processing_time.toFixed(1)}s` : '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          chat.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {chat.status === 'active' ? 'Đang hoạt động' : 'Đã hoàn thành'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <button 
                            onClick={() => handleViewDetail(chat.conversation_id)}
                            className="text-blue-600 hover:text-blue-800 transition-colors p-1"
                            title="Xem chi tiết"
                          >
                            <Eye className="w-5 h-5" />
                          </button>
                          <button 
                            onClick={() => handleDelete(chat.conversation_id)}
                            className="text-red-600 hover:text-red-800 transition-colors p-1"
                            title="Xóa"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Hiển thị {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, totalItems)} của {totalItems} kết quả
              </p>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg border border-gray-300 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="px-4 py-2 text-sm text-gray-700">
                  Trang {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-lg border border-gray-300 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Detail Modal */}
        {showDetailModal && selectedConversation && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
              {/* Modal Header */}
              <div className="bg-red-600 text-white px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">Chi tiết cuộc hội thoại</h3>
                  <p className="text-sm text-red-100">
                    ID: {selectedConversation.conversation_id}
                  </p>
                </div>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-2 hover:bg-red-700 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Stats */}
              <div className="bg-gray-50 px-6 py-3 border-b flex items-center space-x-6 text-sm">
                <span className="text-gray-600">
                  <strong>{selectedConversation.message_count}</strong> tin nhắn
                </span>
                <span className="text-gray-600">
                  Độ tin cậy TB: <strong>{(selectedConversation.avg_confidence * 100).toFixed(0)}%</strong>
                </span>
                <span className="text-gray-600">
                  Thời gian xử lý: <strong>{selectedConversation.total_processing_time?.toFixed(2)}s</strong>
                </span>
              </div>

              {/* Modal Content - Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {loadingDetail ? (
                  <div className="text-center py-12">
                    <RefreshCw className="w-8 h-8 text-gray-400 mx-auto mb-4 animate-spin" />
                    <p className="text-gray-600">Đang tải...</p>
                  </div>
                ) : (
                  selectedConversation.messages.map((msg, index) => (
                    <div key={index} className="space-y-3">
                      {/* User message */}
                      <div className="flex justify-end">
                        <div className="max-w-[80%] bg-red-100 rounded-lg p-4">
                          <p className="text-xs text-red-600 font-medium mb-1">Người dùng</p>
                          <p className="text-gray-800">{msg.user_message}</p>
                          <p className="text-xs text-gray-500 mt-2">{formatDate(msg.timestamp)}</p>
                        </div>
                      </div>
                      
                      {/* Assistant response */}
                      <div className="flex justify-start">
                        <div className="max-w-[80%] bg-gray-100 rounded-lg p-4">
                          <p className="text-xs text-blue-600 font-medium mb-1">Trợ lý AI</p>
                          <p className="text-gray-800 whitespace-pre-wrap">{msg.assistant_response}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-gray-500">
                              Độ tin cậy: {(msg.confidence * 100).toFixed(0)}%
                            </span>
                            {msg.sources && msg.sources.length > 0 && (
                              <span className="text-xs text-gray-500">
                                Nguồn: {msg.sources.join(', ')}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Modal Footer */}
              <div className="bg-gray-50 px-6 py-4 border-t flex justify-end">
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg transition-colors"
                >
                  Đóng
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default ChatHistoryPage;
