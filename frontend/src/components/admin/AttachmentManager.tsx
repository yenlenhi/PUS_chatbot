'use client';

import React, { useState, useEffect } from 'react';
import { FileText, Upload, Trash2, Download, RefreshCw, Plus, X, Search } from 'lucide-react';

interface Attachment {
  id: number;
  file_name: string;
  file_type: string;
  file_path: string;
  file_size?: number;
  description?: string;
  keywords?: string[];
  download_url: string;
  category?: string;
  is_active: boolean;
}

const CATEGORIES = ['Tuyển sinh', 'Đào tạo', 'Công tác sinh viên', 'Hành chính', 'Khác'];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AttachmentManager() {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');

  // Upload form state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const [keywords, setKeywords] = useState('');
  const [chunkIds, setChunkIds] = useState('');
  const [category, setCategory] = useState('Khác');

  useEffect(() => {
    fetchAttachments();
  }, []);

  const fetchAttachments = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/v1/attachments`);
      if (response.ok) {
        const data = await response.json();
        setAttachments(data);
      }
    } catch (error) {
      console.error('Error fetching attachments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (description) formData.append('description', description);
      if (keywords) formData.append('keywords', keywords);
      if (chunkIds) formData.append('chunk_ids', chunkIds);
      if (category) formData.append('category', category);

      const response = await fetch(`${API_BASE}/api/v1/attachments/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        await fetchAttachments();
        setShowUploadModal(false);
        resetForm();
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc chắn muốn xóa file này?')) return;

    try {
      const response = await fetch(`${API_BASE}/api/v1/attachments/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await fetchAttachments();
      }
    } catch (error) {
      console.error('Error deleting attachment:', error);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setDescription('');
    setKeywords('');
    setChunkIds('');
    setCategory('Khác');
  };

  const filteredAttachments = attachments.filter(att => {
    const matchesSearch = att.file_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      att.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === 'All' || att.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    return (bytes / 1024).toFixed(1) + ' KB';
  };

  return (
    <div className="p-4 xs:p-6">
      <div className="mb-4 xs:mb-6">
        <h1 className="text-xl xs:text-2xl font-bold text-gray-900 mb-2">Quản lý File Đính kèm</h1>
        <p className="text-sm xs:text-base text-gray-600">Quản lý các file mẫu (forms, templates) để chatbot đính kèm trong câu trả lời</p>
      </div>

      {/* Actions Bar */}
      <div className="flex flex-col xs:flex-row gap-3 xs:gap-4 mb-4 xs:mb-6">
        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center justify-center gap-2 px-4 py-2.5 xs:py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors order-2 xs:order-1"
        >
          <Plus className="w-4 h-4" />
          <span>Upload File Mới</span>
        </button>

        <button
          onClick={fetchAttachments}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-2.5 xs:py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 order-3 xs:order-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span className="xs:hidden">Làm mới</span>
          <span className="hidden xs:inline">Làm mới</span>
        </button>

        <div className="flex-1 max-w-md order-1 xs:order-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Tìm kiếm file..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 xs:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm xs:text-base"
            />
          </div>
        </div>

        <div className="w-full xs:w-48 order-4 xs:order-4">
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="w-full px-3 py-2.5 xs:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm xs:text-base"
          >
            <option value="All">Tất cả danh mục</option>
            {CATEGORIES.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Attachments List */}
      {loading ? (
        <div className="text-center py-8 xs:py-12">
          <RefreshCw className="w-6 h-6 xs:w-8 xs:h-8 animate-spin mx-auto text-blue-600 mb-2" />
          <p className="text-gray-600 text-sm xs:text-base">Đang tải...</p>
        </div>
      ) : filteredAttachments.length === 0 ? (
        <div className="text-center py-8 xs:py-12 bg-gray-50 rounded-lg">
          <FileText className="w-10 h-10 xs:w-12 xs:h-12 mx-auto text-gray-400 mb-2" />
          <p className="text-gray-600 text-sm xs:text-base">
            {searchQuery ? 'Không tìm thấy file nào' : 'Chưa có file nào được upload'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 xs:gap-4">
          {filteredAttachments.map((attachment) => (
            <div
              key={attachment.id}
              className="bg-white border border-gray-200 rounded-lg p-3 xs:p-4 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2 xs:gap-3 min-w-0 flex-1">
                  <div className="w-8 h-8 xs:w-10 xs:h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <FileText className="w-4 h-4 xs:w-5 xs:h-5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 text-sm xs:text-base truncate">
                      {attachment.file_name}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {attachment.file_type.toUpperCase()} • {formatFileSize(attachment.file_size)}
                    </p>
                    {attachment.category && (
                      <span className="inline-block mt-1 px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">
                        {attachment.category}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {attachment.description && (
                <p className="text-xs xs:text-sm text-gray-600 mb-3 line-clamp-2">
                  {attachment.description}
                </p>
              )}

              {attachment.keywords && attachment.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {attachment.keywords.slice(0, 3).map((keyword, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full"
                    >
                      {keyword}
                    </span>
                  ))}
                  {attachment.keywords.length > 3 && (
                    <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
                      +{attachment.keywords.length - 3}
                    </span>
                  )}
                </div>
              )}

              <div className="flex gap-2">
                <a
                  href={`${API_BASE}${attachment.download_url}`}
                  download
                  className="flex-1 flex items-center justify-center gap-1 xs:gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-xs xs:text-sm"
                >
                  <Download className="w-3 h-3 xs:w-4 xs:h-4" />
                  <span className="hidden xs:inline">Tải về</span>
                  <span className="xs:hidden">Tải</span>
                </a>
                <button
                  onClick={() => handleDelete(attachment.id)}
                  className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                  title="Xóa"
                >
                  <Trash2 className="w-3 h-3 xs:w-4 xs:h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 xs:p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-4 xs:p-6 max-h-[95vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-3 xs:mb-4">
              <h2 className="text-lg xs:text-xl font-bold text-gray-900">Upload File Mới</h2>
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  resetForm();
                }}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpload} className="space-y-3 xs:space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  File *
                </label>
                <input
                  type="file"
                  accept=".doc,.docx,.xlsx,.xls,.pdf"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Cho phép: .doc, .docx, .xlsx, .xls, .pdf (Tối đa 10MB)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mô tả
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="Mô tả ngắn về file này..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Danh mục
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Keywords (phân cách bằng dấu phẩy)
                </label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="form, đơn, nghỉ học, ..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chunk IDs (tùy chọn, phân cách bằng dấu phẩy)
                </label>
                <input
                  type="text"
                  value={chunkIds}
                  onChange={(e) => setChunkIds(e.target.value)}
                  placeholder="1, 5, 10, ..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Link file với các chunks cụ thể (để chatbot biết khi nào đính kèm)
                </p>
              </div>

              <div className="flex gap-3 pt-3 xs:pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowUploadModal(false);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={!selectedFile || uploading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm"
                >
                  {uploading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Đang upload...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      <span>Upload</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
