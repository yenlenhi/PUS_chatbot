'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  FileText, Upload, Trash2, Download, RefreshCw, Plus, X, Search,
  File as FileIcon, CheckCircle, AlertCircle, HardDrive, Filter,
  PieChart, BarChart3, Clock, MoreVertical, Edit2, Eye,
  ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight
} from 'lucide-react';
import { PieChart as RePieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { AttachmentTable } from './attachments/AttachmentTable';
import { AttachmentMobileList } from './attachments/AttachmentMobileList';

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

  // Pagination State
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalItems, setTotalItems] = useState(0);

  // Upload State
  const [uploadQueue, setUploadQueue] = useState<UploadItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchAttachments();
  }, [page, pageSize, searchQuery, filterCategory]);

  const fetchAttachments = async () => {
    try {
      setLoading(true);

      const skip = (page - 1) * pageSize;
      const queryParams = new URLSearchParams({
        skip: skip.toString(),
        limit: pageSize.toString(),
      });

      if (searchQuery) queryParams.append('search', searchQuery);
      if (filterCategory && filterCategory !== 'All') queryParams.append('category', filterCategory);

      const response = await fetch(`${API_BASE}/api/v1/attachments?${queryParams.toString()}`);
      if (response.ok) {
        const data = await response.json();
        // Check if response is paginated (has items and total) or list
        if (data.items) {
          setAttachments(data.items);
          setTotalItems(data.total);
        } else if (Array.isArray(data)) {
          // Fallback for old API style
          setAttachments(data);
          setTotalItems(data.length);
        }
      }
    } catch (error) {
      console.error('Error fetching attachments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setPage(1); // Reset to first page
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterCategory(e.target.value);
    setPage(1); // Reset to first page
  };

  // --- Statistics Logic ---
  const stats = React.useMemo(() => {
    const totalFiles = totalItems; // Use total from backend
    const totalSize = attachments.reduce((acc, curr) => acc + (curr.file_size || 0), 0);

    const categoryCounts = attachments.reduce((acc, curr) => {
      const cat = curr.category || 'Khác';
      acc[cat] = (acc[cat] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const pieData = Object.entries(categoryCounts).map(([name, value]) => ({ name, value }));

    return { totalFiles, totalSize, pieData };
  }, [attachments, totalItems]);

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
    setShowUploadModal(true);
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

  const removeUploadItem = (id: string) => {
    setUploadQueue(prev => prev.filter(item => item.id !== id));
  };

  const updateUploadItem = (id: string, field: keyof UploadItem, value: any) => {
    setUploadQueue(prev => prev.map(item =>
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  const handleUploadAll = async () => {
    const pendingItems = uploadQueue.filter(item => item.status === 'pending');

    for (const item of pendingItems) {
      updateUploadItem(item.id, 'status', 'uploading');

      try {
        const formData = new FormData();
        formData.append('file', item.file);
        formData.append('description', item.description);
        formData.append('keywords', item.keywords);
        formData.append('category', item.category);

        if (item.chunkIds) {
          formData.append('chunk_ids', item.chunkIds);
        }

        const response = await fetch(`${API_BASE}/api/v1/attachments/upload`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          updateUploadItem(item.id, 'status', 'success');
        } else {
          updateUploadItem(item.id, 'status', 'error');
          updateUploadItem(item.id, 'errorMessage', 'Upload failed');
        }
      } catch (error) {
        updateUploadItem(item.id, 'status', 'error');
        updateUploadItem(item.id, 'errorMessage', 'Network error');
      }
    }

    fetchAttachments();
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this file?')) return;
    try {
      const response = await fetch(`${API_BASE}/api/v1/attachments/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchAttachments();
      }
    } catch (error) {
      console.error('Error deleting attachment:', error);
    }
  };

  const handlePreview = (file: Attachment) => {
    const previewUrl = file.public_url || `${API_BASE}${file.download_url}`;

    if (file.file_name.match(/\.(doc|docx|xls|xlsx|ppt|pptx)$/i)) {
      if (file.public_url) {
        window.open(`https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(file.public_url)}`, '_blank');
      } else {
        console.warn('Cannot preview Office file without public_url (Localhost not supported by MS Office Viewer)');
        window.open(previewUrl, '_blank');
      }
    } else {
      window.open(previewUrl, '_blank');
    }
  };

  const totalPages = Math.ceil(totalItems / pageSize);

  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
            <HardDrive size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Tổng số file</p>
            <h3 className="text-2xl font-bold">{stats.totalFiles}</h3>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-purple-50 text-purple-600 rounded-lg">
            {/* Using BarChart3 as placeholder for size icon */}
            <BarChart3 size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Tổng dung lượng (trang này)</p>
            <h3 className="text-2xl font-bold">{(stats.totalSize / 1024 / 1024).toFixed(2)} MB</h3>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-green-50 text-green-600 rounded-lg">
            <PieChart size={24} />
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-500">Phân loại (trang này)</p>
            <div className="h-10 w-full mt-1 flex gap-1">
              {stats.pieData.map((entry, index) => (
                <div
                  key={index}
                  style={{ width: `${(entry.value / attachments.length) * 100}%`, backgroundColor: COLORS[index % COLORS.length] }}
                  className="h-full rounded-sm"
                  title={`${entry.name}: ${entry.value}`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col min-h-[600px]">
        {/* Toolbar */}
        <div className="p-4 border-b flex flex-col sm:flex-row gap-4 justify-between items-center bg-gray-50/50">
          <div className="flex gap-2 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Tìm kiếm tài liệu..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <select
              value={filterCategory}
              onChange={handleCategoryChange}
              className="px-4 py-2 border rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option value="All">Tất cả danh mục</option>
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div className="flex gap-2">
            <button
              onClick={fetchAttachments}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw size={20} />
            </button>
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
            >
              <Plus size={20} />
              <span>Thêm tài liệu</span>
            </button>
          </div>
        </div>

        {/* File List */}
        <div className="flex-1 overflow-auto p-4">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : attachments.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-400">
              <HardDrive size={48} className="mb-4 opacity-50" />
              <p>Không tìm thấy tài liệu nào</p>
            </div>
          ) : (
            <>
              {/* Desktop View */}
              <div className="hidden md:block">
                <AttachmentTable
                  attachments={attachments}
                  onPreview={handlePreview}
                  onDelete={handleDelete}
                />
              </div>

              {/* Mobile View */}
              <div className="block md:hidden">
                <AttachmentMobileList
                  attachments={attachments}
                  onPreview={handlePreview}
                  onDelete={handleDelete}
                />
              </div>
            </>
          )}
        </div>

        {/* Pagination Controls */}
        <div className="p-4 border-t bg-gray-50 flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Hiển thị {attachments.length} / {totalItems} tài liệu
          </div>

          <div className="flex items-center gap-2">
            <button
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              className="p-2 border rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={16} />
            </button>

            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let p = i + 1;
              if (totalPages > 5) {
                // Adjust start page to keep current page visible
                let start = Math.max(1, page - 2);
                if (start + 4 > totalPages) {
                  start = Math.max(1, totalPages - 4);
                }
                p = start + i;
              }

              // Safe check
              if (p > totalPages) return null;

              return (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${page === p
                    ? 'bg-blue-600 text-white'
                    : 'hover:bg-gray-100 text-gray-600'
                    }`}
                >
                  {p}
                </button>
              );
            })}

            <button
              disabled={page >= totalPages}
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              className="p-2 border rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-[800px] max-h-[90vh] flex flex-col shadow-2xl">
            <div className="p-6 border-b flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-800">Tải lên tài liệu</h2>
              <button onClick={() => setShowUploadModal(false)} className="p-2 hover:bg-gray-100 rounded-full">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 flex-1 overflow-y-auto">
              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-400'
                  }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload size={32} />
                </div>
                <h3 className="text-lg font-semibold mb-2">Kéo thả file vào đây</h3>
                <p className="text-gray-500 mb-4">hoặc</p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Chọn file từ máy tính
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  multiple
                  onChange={(e) => handleFilesSelected(e.target.files)}
                />
              </div>

              {uploadQueue.length > 0 && (
                <div className="mt-6 space-y-4">
                  {uploadQueue.map(item => (
                    <div key={item.id} className="bg-gray-50 rounded-xl p-4 border block">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-3">
                          <FileText className="text-blue-600" size={20} />
                          <div>
                            <p className="font-medium">{item.name}</p>
                            <p className="text-xs text-gray-500">{(item.file.size / 1024).toFixed(1)} KB</p>
                          </div>
                        </div>
                        <button onClick={() => removeUploadItem(item.id)} className="text-gray-400 hover:text-red-500">
                          <X size={16} />
                        </button>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-3">
                        <div>
                          <label className="text-xs font-medium text-gray-700 block mb-1">Danh mục</label>
                          <select
                            value={item.category}
                            onChange={(e) => updateUploadItem(item.id, 'category', e.target.value)}
                            className="w-full text-sm border rounded-lg p-2"
                          >
                            {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                          </select>
                        </div>
                        <div>
                          <label className="text-xs font-medium text-gray-700 block mb-1">Mô tả</label>
                          <input
                            type="text"
                            value={item.description}
                            onChange={(e) => updateUploadItem(item.id, 'description', e.target.value)}
                            className="w-full text-sm border rounded-lg p-2"
                            placeholder="Mô tả ngắn..."
                          />
                        </div>
                      </div>

                      {item.status === 'error' && (
                        <div className="text-xs text-red-500 flex items-center gap-1 mt-2">
                          <AlertCircle size={12} /> {item.errorMessage}
                        </div>
                      )}
                      {item.status === 'success' && (
                        <div className="text-xs text-green-600 flex items-center gap-1 mt-2">
                          <CheckCircle size={12} /> Đã tải lên thành công
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6 border-t bg-gray-50 rounded-b-2xl flex justify-between items-center">
              <span className="text-sm text-gray-500">
                {uploadQueue.length} file đã chọn
              </span>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  Hủy bỏ
                </button>
                <button
                  onClick={handleUploadAll}
                  disabled={uploadQueue.length === 0 || uploadQueue.some(i => i.status === 'uploading')}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {uploadQueue.some(i => i.status === 'uploading') ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Đang tải lên...</span>
                    </>
                  ) : (
                    <span>Tải lên tất cả</span>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
