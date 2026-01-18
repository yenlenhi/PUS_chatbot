'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  FileText, Upload, Trash2, Download, RefreshCw, Plus, X, Search,
  File as FileIcon, CheckCircle, AlertCircle, HardDrive, Filter,
  PieChart, BarChart3, Clock, MoreVertical, Edit2, Eye
} from 'lucide-react';
import { PieChart as RePieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

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
  created_at?: string;
  public_url?: string;
}

interface UploadItem {
  id: string;
  file: File;
  name: string;
  category: string;
  description: string;
  keywords: string;
  chunkIds: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  errorMessage?: string;
  progress?: number;
}

const CATEGORIES = ['Tuyển sinh', 'Đào tạo', 'Công tác sinh viên', 'Hành chính', 'Khác'];
const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#6366F1', '#EC4899'];
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AttachmentManager() {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');

  // Upload State
  const [uploadQueue, setUploadQueue] = useState<UploadItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  // --- Statistics Logic ---
  const stats = React.useMemo(() => {
    const totalFiles = attachments.length;
    const totalSize = attachments.reduce((acc, curr) => acc + (curr.file_size || 0), 0);
    const categoryCounts = attachments.reduce((acc, curr) => {
      const cat = curr.category || 'Khác';
      acc[cat] = (acc[cat] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const pieData = Object.entries(categoryCounts).map(([name, value]) => ({ name, value }));

    return { totalFiles, totalSize, pieData };
  }, [attachments]);

  // --- Upload Logic ---
  const handleFilesSelected = (files: FileList | null) => {
    if (!files) return;
    const newItems: UploadItem[] = Array.from(files).map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      category: 'Khác',
      description: '',
      keywords: file.name.split('.')[0].replace(/[-_]/g, ' '),
      chunkIds: '',
      status: 'pending'
    }));
    setUploadQueue(prev => [...prev, ...newItems]);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFilesSelected(e.dataTransfer.files);
  };

  const updateQueueItem = (id: string, field: keyof UploadItem, value: any) => {
    setUploadQueue(prev => prev.map(item => item.id === id ? { ...item, [field]: value } : item));
  };

  const removeQueueItem = (id: string) => {
    setUploadQueue(prev => prev.filter(item => item.id !== id));
  };

  const handleUploadAll = async () => {
    // Process strictly one by one to avoid overwhelming server or race conditions
    for (const item of uploadQueue) {
      if (item.status === 'success' || item.status === 'uploading') continue;

      updateQueueItem(item.id, 'status', 'uploading');

      try {
        const formData = new FormData();
        formData.append('file', item.file);
        // Use edited name if provided, otherwise original filename handled by backend
        // We might want to pass 'filename' if backend supports renaming on upload
        // Currently backend uses file.filename

        formData.append('description', item.description);
        formData.append('keywords', item.keywords);
        formData.append('chunk_ids', item.chunkIds);
        formData.append('category', item.category);

        const response = await fetch(`${API_BASE}/api/v1/attachments/upload`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          updateQueueItem(item.id, 'status', 'success');
        } else {
          const err = await response.json();
          updateQueueItem(item.id, 'status', 'error');
          updateQueueItem(item.id, 'errorMessage', err.detail || 'Failed');
        }
      } catch (error) {
        updateQueueItem(item.id, 'status', 'error');
        updateQueueItem(item.id, 'errorMessage', 'Network error');
      }
    }
    // Refresh list after all done
    await fetchAttachments();
  };

  const allSuccess = uploadQueue.length > 0 && uploadQueue.every(i => i.status === 'success');

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc chắn muốn xóa file này?')) return;
    try {
      const response = await fetch(`${API_BASE}/api/v1/attachments/${id}`, { method: 'DELETE' });
      if (response.ok) await fetchAttachments();
    } catch (error) {
      console.error('Error deleting attachment:', error);
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '0 B';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handlePreview = (file: Attachment) => {
    // Use public_url if available (preferred for Office Viewer), otherwise fallback to download_url
    const previewUrl = file.public_url || `${API_BASE}${file.download_url}`;

    // For Word/Excel/PowerPoint, use Microsoft Office Online Viewer
    if (file.file_name.match(/\.(doc|docx|xls|xlsx|ppt|pptx)$/i)) {
      // Office Viewer requires a publicly accessible URL
      if (file.public_url) {
        window.open(`https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(file.public_url)}`, '_blank');
      } else {
        // Warning: Localhost URLs won't work with Office Viewer
        console.warn('Cannot preview Office file without public_url (Localhost not supported by MS Office Viewer)');
        window.open(previewUrl, '_blank');
      }
    } else {
      // For PDF, Images, or others, try opening directly in browser
      window.open(previewUrl, '_blank');
    }
  };

  const filteredAttachments = attachments.filter(att => {
    const matchesSearch = att.file_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      att.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === 'All' || att.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quản lý Tài liệu</h1>
          <p className="text-gray-500 mt-1">Quản lý các file biểu mẫu và tài liệu tham khảo cho Chatbot</p>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <button
            onClick={fetchAttachments}
            className="p-2 text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            title="Làm mới"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-sm transition-all hover:shadow-md"
          >
            <Plus className="w-5 h-5" />
            <span>Upload Tài liệu</span>
          </button>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Card 1: Tổng quan */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">Tổng số tài liệu</p>
            <h3 className="text-3xl font-bold text-gray-900 mt-2">{stats.totalFiles}</h3>
            <p className="text-xs text-gray-400 mt-1">Tổng dung lượng: {formatFileSize(stats.totalSize)}</p>
          </div>
          <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center">
            <HardDrive className="w-6 h-6 text-blue-600" />
          </div>
        </div>

        {/* Card 2: Danh mục */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center">
          <p className="text-sm font-medium text-gray-500 mb-2">Phân bố danh mục</p>
          <div className="h-16 flex gap-1">
            {stats.pieData.map((entry, index) => (
              <div
                key={entry.name}
                className="h-full rounded-md relative group cursor-help"
                style={{
                  width: `${(entry.value / stats.totalFiles) * 100}%`,
                  backgroundColor: COLORS[index % COLORS.length]
                }}
              >
                <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                  {entry.name}: {entry.value}
                </div>
              </div>
            ))}
          </div>
          <div className="flex gap-4 mt-3 text-xs text-gray-500 overflow-x-auto">
            {stats.pieData.slice(0, 3).map((entry, index) => (
              <div key={entry.name} className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                <span>{entry.name} ({entry.value})</span>
              </div>
            ))}
          </div>
        </div>

        {/* Card 3: Hoạt động (Static placeholder for now) */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">Trạng thái hệ thống</p>
            <div className="flex items-center gap-2 mt-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-green-700">Supabase Connected</span>
            </div>
            <p className="text-xs text-gray-400 mt-2">Sẵn sàng phục vụ RAG</p>
          </div>
          <div className="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-green-600" />
          </div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Tìm kiếm theo tên file, mô tả..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          />
        </div>
        <div className="w-full sm:w-64">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full pl-10 pr-8 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none bg-white cursor-pointer"
            >
              <option value="All">Tất cả danh mục</option>
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* File Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredAttachments.map((file) => (
          <div key={file.id} className="group bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-300 flex flex-col h-full overflow-hidden">
            <div className="p-5 flex-1">
              <div className="flex justify-between items-start mb-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${file.file_name.endsWith('.pdf') ? 'bg-red-50 text-red-600' :
                  file.file_name.match(/\.(xls|xlsx)$/) ? 'bg-green-50 text-green-600' :
                    'bg-blue-50 text-blue-600'
                  }`}>
                  <FileText className="w-6 h-6" />
                </div>
                <div className="relative">
                  <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                    {file.category || 'Khác'}
                  </span>
                </div>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1 truncate" title={file.file_name}>
                {file.file_name}
              </h3>
              <p className="text-xs text-gray-500 mb-3">{formatFileSize(file.file_size)}</p>

              {file.description && (
                <p className="text-sm text-gray-600 line-clamp-2 mb-3 bg-gray-50 p-2 rounded-lg">
                  {file.description}
                </p>
              )}

              <div className="flex flex-wrap gap-1 mt-2">
                {file.keywords?.slice(0, 3).map((kw, i) => (
                  <span key={i} className="text-[10px] uppercase tracking-wider px-2 py-1 bg-gray-100 text-gray-500 rounded-md">
                    {kw}
                  </span>
                ))}
              </div>
            </div>

            <div className="px-5 py-4 bg-gray-50 border-t border-gray-100 flex gap-2 opacity-80 group-hover:opacity-100 transition-opacity">
              <a
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-blue-600 transition-colors"
              >
                <Download className="w-4 h-4" />
                Tải về
              </a>
              <button
                onClick={() => handlePreview(file)}
                className="p-2 bg-white border border-gray-200 rounded-lg text-gray-400 hover:text-blue-600 hover:border-blue-200 hover:bg-blue-50 transition-all"
                title="Xem online"
              >
                <Eye className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDelete(file.id)}
                className="p-2 bg-white border border-gray-200 rounded-lg text-gray-400 hover:text-red-600 hover:border-red-200 hover:bg-red-50 transition-all"
                title="Xóa"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredAttachments.length === 0 && !loading && (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-300">
          <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900">Không tìm thấy tài liệu nào</h3>
          <p className="text-gray-500 mt-2">Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
        </div>
      )}

      {/* Upload Modal with Multi-File Support */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Upload Tài liệu</h2>
                <p className="text-xs text-gray-500 mt-1">Hỗ trợ upload nhiều file cùng lúc</p>
              </div>
              <button onClick={() => setShowUploadModal(false)} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {/* Drag & Drop Area */}
              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer mb-6 ${isDragging ? 'border-blue-500 bg-blue-50 scale-[1.01]' : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                  }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  type="file"
                  multiple
                  className="hidden"
                  ref={fileInputRef}
                  onChange={(e) => handleFilesSelected(e.target.files)}
                  accept=".doc,.docx,.pdf,.xls,.xlsx"
                />
                <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">Kéo thả file vào đây hoặc click để chọn</h3>
                <p className="text-sm text-gray-500 mt-2">Hỗ trợ PDF, Word, Excel (Max 10MB/file)</p>
              </div>

              {/* Upload Queue List */}
              {uploadQueue.length > 0 && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                    <FileIcon className="w-4 h-4" />
                    Danh sách chờ ({uploadQueue.length})
                  </h3>

                  {uploadQueue.map((item, index) => (
                    <div key={item.id} className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:border-blue-200 transition-colors">
                      <div className="flex items-start gap-4">
                        {/* Status Icon */}
                        <div className="mt-1">
                          {item.status === 'success' && <CheckCircle className="w-6 h-6 text-green-500" />}
                          {item.status === 'error' && <AlertCircle className="w-6 h-6 text-red-500" />}
                          {item.status === 'uploading' && <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />}
                          {item.status === 'pending' && <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-xs font-bold text-gray-500">{index + 1}</div>}
                        </div>

                        {/* Form Fields */}
                        <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="col-span-full">
                            <div className="flex justify-between">
                              <p className="font-medium text-gray-900 truncate max-w-md" title={item.file.name}>{item.file.name}</p>
                              <span className="text-xs text-gray-500">{formatFileSize(item.file.size)}</span>
                            </div>
                          </div>

                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Mô tả</label>
                            <input
                              type="text"
                              className="w-full text-sm px-3 py-2 border border-gray-200 rounded-lg focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all"
                              placeholder="Mô tả nội dung file..."
                              value={item.description}
                              onChange={e => updateQueueItem(item.id, 'description', e.target.value)}
                              disabled={item.status === 'success' || item.status === 'uploading'}
                            />
                          </div>

                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Danh mục</label>
                            <select
                              className="w-full text-sm px-3 py-2 border border-gray-200 rounded-lg focus:ring-1 focus:ring-blue-500 focus:border-blue-500 bg-white"
                              value={item.category}
                              onChange={e => updateQueueItem(item.id, 'category', e.target.value)}
                              disabled={item.status === 'success' || item.status === 'uploading'}
                            >
                              {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                            </select>
                          </div>

                          <div className="md:col-span-2">
                            <label className="block text-xs font-medium text-gray-700 mb-1">Keywords</label>
                            <input
                              type="text"
                              className="w-full text-sm px-3 py-2 border border-gray-200 rounded-lg focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all"
                              placeholder="Từ khóa tìm kiếm (phân cách bằng dấu phẩy)..."
                              value={item.keywords}
                              onChange={e => updateQueueItem(item.id, 'keywords', e.target.value)}
                              disabled={item.status === 'success' || item.status === 'uploading'}
                            />
                          </div>

                          {item.status === 'error' && (
                            <div className="col-span-full text-xs text-red-600 bg-red-50 p-2 rounded-lg">
                              Lỗi: {item.errorMessage}
                            </div>
                          )}
                        </div>

                        {/* Action */}
                        <button
                          onClick={() => removeQueueItem(item.id)}
                          className="text-gray-400 hover:text-red-500 transition-colors p-1"
                          disabled={item.status === 'uploading'}
                        >
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-4 border-t border-gray-100 bg-gray-50 flex flex-col gap-3">
              {allSuccess && (
                <div className="flex items-center gap-2 text-green-600 bg-green-50 p-2 rounded-lg text-sm mb-1 animate-in fade-in slide-in-from-bottom-2">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Tất cả file đã được upload thành công!</span>
                </div>
              )}

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => {
                    setShowUploadModal(false);
                    setUploadQueue([]);
                  }}
                  className={`px-5 py-2.5 font-medium rounded-xl transition-colors ${allSuccess
                    ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-200 hover:shadow-xl'
                    : 'text-gray-700 hover:bg-gray-200'
                    }`}
                >
                  {allSuccess ? 'Hoàn tất & Đóng' : 'Đóng'}
                </button>

                {!allSuccess && (
                  <button
                    onClick={handleUploadAll}
                    disabled={uploadQueue.length === 0 || uploadQueue.every(i => i.status === 'success')}
                    className="px-6 py-2.5 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-200 hover:shadow-xl transition-all disabled:opacity-50 disabled:shadow-none"
                  >
                    {uploadQueue.some(i => i.status === 'uploading') ? 'Đang xử lý...' : 'Upload Tất cả'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

