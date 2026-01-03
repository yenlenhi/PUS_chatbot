'use client';

import React, { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
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
  
  // Image preview modal
  const [previewImage, setPreviewImage] = useState<string | null>(null);

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
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-4 xs:p-6">
          <div className="flex flex-col lg:flex-row gap-3 xs:gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 xs:w-5 xs:h-5" />
              <input
                type="text"
                placeholder="Tìm kiếm theo nội dung..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-9 xs:pl-10 pr-4 py-2.5 xs:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900 text-sm xs:text-base"
              />
            </div>

            {/* Filter Controls */}
            <div className="flex flex-col xs:flex-row items-stretch xs:items-center gap-2 xs:gap-3">
              <div className="flex items-center space-x-2 xs:space-x-3">
                <Filter className="w-4 h-4 xs:w-5 xs:h-5 text-gray-400 hidden xs:block" />
                <select
                  value={selectedFilter}
                  onChange={(e) => {
                    setSelectedFilter(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="flex-1 xs:flex-none px-3 xs:px-4 py-2.5 xs:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900 text-sm xs:text-base"
                >
                  {filters.map(filter => (
                    <option key={filter.value} value={filter.value}>
                      {filter.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-2 xs:gap-3">
                <button 
                  onClick={fetchConversations}
                  className="flex-1 xs:flex-none px-3 xs:px-4 py-2.5 xs:py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors flex items-center justify-center space-x-2 text-sm xs:text-base"
                  disabled={loading}
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                  <span className="xs:hidden">Làm mới</span>
                  <span className="hidden xs:inline">Làm mới</span>
                </button>

                <button 
                  onClick={handleExport}
                  className="flex-1 xs:flex-none px-3 xs:px-4 py-2.5 xs:py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center justify-center space-x-2 shadow-sm text-sm xs:text-base"
                  disabled={exporting}
                >
                  <Download className={`w-4 h-4 ${exporting ? 'animate-pulse' : ''}`} />
                  <span className="xs:hidden">{exporting ? 'Xuất...' : 'Export'}</span>
                  <span className="hidden xs:inline">{exporting ? 'Đang xuất...' : 'Export'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 xs:gap-4">
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 xs:p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs xs:text-sm text-gray-600">Tổng cuộc hội thoại</p>
                <p className="text-xl xs:text-2xl font-bold text-gray-900 mt-1">
                  {stats?.total_conversations || 0}
                </p>
              </div>
              <MessageSquare className="w-6 h-6 xs:w-8 xs:h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 xs:p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs xs:text-sm text-gray-600">Đang hoạt động</p>
                <p className="text-xl xs:text-2xl font-bold text-green-600 mt-1">
                  {stats?.active_conversations || 0}
                </p>
              </div>
              <User className="w-6 h-6 xs:w-8 xs:h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 xs:p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs xs:text-sm text-gray-600">Hôm nay</p>
                <p className="text-xl xs:text-2xl font-bold text-purple-600 mt-1">
                  {stats?.today_conversations || 0}
                </p>
              </div>
              <Calendar className="w-6 h-6 xs:w-8 xs:h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 xs:p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs xs:text-sm text-gray-600">Tổng tin nhắn</p>
                <p className="text-xl xs:text-2xl font-bold text-orange-600 mt-1">
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
          {/* Mobile Card View */}
          <div className="lg:hidden divide-y divide-gray-200">
            {loading ? (
              <div className="px-4 py-12 text-center">
                <RefreshCw className="w-8 h-8 text-gray-400 mx-auto mb-4 animate-spin" />
                <p className="text-gray-600">Đang tải...</p>
              </div>
            ) : conversations.length === 0 ? (
              <div className="px-4 py-12 text-center">
                <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Không tìm thấy cuộc hội thoại nào</p>
              </div>
            ) : (
              conversations.map((chat) => (
                <div key={chat.conversation_id} className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-500 font-mono truncate">
                        ID: {chat.conversation_id.substring(0, 8)}...
                      </p>
                      <h3 className="text-sm font-medium text-gray-900 mt-1 line-clamp-2">
                        {chat.first_query || 'Không có câu hỏi'}
                      </h3>
                    </div>
                    <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full shrink-0 ${
                      chat.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {chat.status === 'active' ? 'Hoạt động' : 'Hoàn thành'}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center text-sm text-gray-600">
                    <span>{chat.message_count} tin nhắn</span>
                    <span className="text-xs">
                      {formatDate(chat.last_message)}
                    </span>
                  </div>
                  
                  <div className="flex gap-2 pt-2">
                    <button 
                      onClick={() => handleViewDetail(chat.conversation_id)}
                      className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors text-sm"
                      title="Xem chi tiết"
                    >
                      <Eye className="w-4 h-4" />
                      <span>Xem</span>
                    </button>
                    <button 
                      onClick={() => handleDelete(chat.conversation_id)}
                      className="flex items-center justify-center px-3 py-2 text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
                      title="Xóa"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Desktop Table View */}
          <div className="hidden lg:block overflow-x-auto">
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
            <div className="bg-gray-50 px-4 xs:px-6 py-3 xs:py-4 border-t border-gray-200 flex flex-col xs:flex-row items-center justify-between gap-3 xs:gap-0">
              <p className="text-xs xs:text-sm text-gray-600 order-2 xs:order-1">
                <span className="hidden xs:inline">
                  Hiển thị {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, totalItems)} của {totalItems} kết quả
                </span>
                <span className="xs:hidden">
                  {((currentPage - 1) * itemsPerPage) + 1}-{Math.min(currentPage * itemsPerPage, totalItems)} / {totalItems}
                </span>
              </p>
              <div className="flex items-center space-x-2 order-1 xs:order-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg border border-gray-300 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4 xs:w-5 xs:h-5" />
                </button>
                <span className="px-3 xs:px-4 py-2 text-xs xs:text-sm text-gray-700">
                  <span className="hidden xs:inline">Trang </span>{currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-lg border border-gray-300 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4 xs:w-5 xs:h-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Detail Modal */}
        {showDetailModal && selectedConversation && (
          <div className="fixed inset-0 bg-gray-900 bg-opacity-75 z-50 flex items-center justify-center p-0">
            <div className="bg-white w-full h-full overflow-hidden flex flex-col">
              {/* Modal Header */}
              <div className="bg-gradient-to-r from-red-600 to-red-700 text-white px-4 xs:px-6 py-3 xs:py-4 flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <h3 className="text-base xs:text-lg font-semibold truncate">Chi tiết cuộc hội thoại</h3>
                  <p className="text-xs xs:text-sm text-red-100 font-mono truncate">
                    ID: {selectedConversation.conversation_id}
                  </p>
                </div>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-1.5 xs:p-2 hover:bg-red-800 rounded-lg transition-colors flex-shrink-0 ml-2"
                >
                  <X className="w-4 h-4 xs:w-5 xs:h-5" />
                </button>
              </div>

              {/* Modal Stats */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-4 xs:px-6 py-3 border-b border-gray-200">
                <div className="flex flex-col xs:flex-row xs:items-center gap-2 xs:gap-6 text-xs xs:text-sm">
                  <span className="text-gray-700 font-medium">
                    📊 <strong className="text-blue-600">{selectedConversation.message_count}</strong> tin nhắn
                  </span>
                  <span className="text-gray-700 font-medium">
                    🎯 Độ tin cậy TB: <strong className="text-green-600">{(selectedConversation.avg_confidence * 100).toFixed(0)}%</strong>
                  </span>
                  <span className="text-gray-700 font-medium">
                    ⚡ Thời gian xử lý: <strong className="text-purple-600">{selectedConversation.total_processing_time?.toFixed(2)}s</strong>
                  </span>
                </div>
              </div>

              {/* Modal Content - Messages */}
              <div className="flex-1 overflow-y-auto bg-gray-50 p-3 xs:p-6 space-y-4 xs:space-y-6">
                {loadingDetail ? (
                  <div className="text-center py-8 xs:py-12">
                    <RefreshCw className="w-6 h-6 xs:w-8 xs:h-8 text-gray-400 mx-auto mb-4 animate-spin" />
                    <p className="text-gray-600 text-sm xs:text-base">Đang tải...</p>
                  </div>
                ) : (
                  selectedConversation.messages.map((msg, index) => (
                    <div key={index} className="space-y-3 xs:space-y-4">
                      {/* User message */}
                      <div className="flex justify-end">
                        <div className="max-w-[90%] xs:max-w-[75%] bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-3 xs:p-4 shadow-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                              <User className="w-3 h-3" />
                            </div>
                            <p className="text-xs font-medium text-blue-100">Người dùng</p>
                          </div>
                          
                          {/* User text message */}
                          <p className="text-sm xs:text-base break-words leading-relaxed">{msg.user_message}</p>
                          
                          {/* User images if any */}
                          {msg.images && msg.images.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-2">
                              {msg.images.map((imageUrl: string, imgIndex: number) => (
                                <div 
                                  key={imgIndex} 
                                  className="bg-white bg-opacity-10 rounded-lg p-1 cursor-pointer hover:bg-opacity-20 transition-all"
                                  onClick={() => setPreviewImage(imageUrl)}
                                >
                                  <img 
                                    src={imageUrl} 
                                    alt={`Hình ảnh ${imgIndex + 1}`}
                                    className="w-16 h-16 xs:w-20 xs:h-20 object-cover rounded-md"
                                    onError={(e) => {
                                      const target = e.target as HTMLImageElement;
                                      target.style.display = 'none';
                                    }}
                                  />
                                </div>
                              ))}
                            </div>
                          )}
                          
                          <p className="text-xs text-blue-100 mt-2 opacity-75">{formatDate(msg.timestamp)}</p>
                        </div>
                      </div>
                      
                      {/* Assistant response */}
                      <div className="flex justify-start">
                        <div className="max-w-[90%] xs:max-w-[75%] bg-white rounded-2xl p-3 xs:p-4 shadow-lg border border-gray-200">
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 bg-gradient-to-br from-green-400 to-green-500 rounded-full flex items-center justify-center">
                              <MessageSquare className="w-3 h-3 text-white" />
                            </div>
                            <p className="text-xs font-medium text-green-600">Trợ lý AI</p>
                          </div>
                          <div className="text-sm xs:text-base text-gray-800 leading-relaxed prose prose-sm max-w-none markdown-content">
                            <ReactMarkdown
                              components={{
                                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                                ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                                ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                                li: ({ children }) => <li className="text-gray-800">{children}</li>,
                                strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                                em: ({ children }) => <em className="italic text-gray-700">{children}</em>,
                                code: ({ children }) => <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-gray-800">{children}</code>,
                                pre: ({ children }) => <pre className="bg-gray-100 p-3 rounded-lg overflow-x-auto mb-2">{children}</pre>,
                                blockquote: ({ children }) => <blockquote className="border-l-4 border-blue-400 pl-3 italic text-gray-700 mb-2">{children}</blockquote>
                              }}
                            >
                              {msg.assistant_response}
                            </ReactMarkdown>
                          </div>
                          <div className="flex flex-col xs:flex-row xs:items-center xs:justify-between mt-3 pt-3 border-t border-gray-100 gap-1 xs:gap-0">
                            <div className="flex items-center gap-1">
                              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                              <span className="text-xs text-gray-500">
                                Độ tin cậy: <span className="font-medium text-green-600">{(msg.confidence * 100).toFixed(0)}%</span>
                              </span>
                            </div>
                            {msg.sources && msg.sources.length > 0 && (
                              <div className="flex items-center gap-1">
                                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                                <span className="text-xs text-gray-500 truncate">
                                  Nguồn: <span className="font-medium text-blue-600">{msg.sources.join(', ')}</span>
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Modal Footer */}
              <div className="bg-white border-t border-gray-200 px-4 xs:px-6 py-3 xs:py-4 flex justify-end">
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-6 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors font-medium text-sm xs:text-base shadow-sm"
                >
                  Đóng
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Image Preview Modal */}
        {previewImage && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-90 z-[60] flex items-center justify-center p-4"
            onClick={() => setPreviewImage(null)}
          >
            <button
              onClick={() => setPreviewImage(null)}
              className="absolute top-4 right-4 p-2 text-white hover:text-gray-300 transition-colors"
            >
              <X className="w-8 h-8" />
            </button>
            <img 
              src={previewImage} 
              alt="Preview"
              className="max-w-full max-h-full object-contain rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default ChatHistoryPage;
