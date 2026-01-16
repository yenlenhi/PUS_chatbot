'use client';

import React, { useState, useEffect, useCallback } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import UploadModal from '@/components/admin/UploadModal';
import BatchUploadModal from '@/components/admin/BatchUploadModal';
import QuickStats from '@/components/admin/QuickStats';
import Toast, { ToastType } from '@/components/ui/Toast';
import ConfirmModal from '@/components/ui/ConfirmModal';
import { documentsAPI } from '@/services/api';
import { Document } from '@/types/api';
import { 
  Search, Upload, Download, FileText, Eye, Trash2, 
  Plus, Filter, RefreshCw, AlertCircle, Loader2,
  Database, HardDrive, LayoutGrid, List, Power, PowerOff,
  ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Check,
  Archive, FolderOpen, Zap, Clock, BarChart3
} from 'lucide-react';
import { getDocumentUrl } from '@/lib/supabase';

type ViewMode = 'grid' | 'list';
type UploadMode = 'single' | 'batch';

const ITEMS_PER_PAGE_GRID = 9;  // 3x3 grid
const ITEMS_PER_PAGE_LIST = 10;

// Confirm modal state type
interface ConfirmState {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText: string;
  type: 'danger' | 'warning' | 'info';
  icon: 'power' | 'powerOff' | 'delete' | 'warning';
  onConfirm: () => void;
}

const DocumentsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [categories, setCategories] = useState<string[]>(['Tất cả']);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isBatchUploadModalOpen, setIsBatchUploadModalOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [togglingId, setTogglingId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [uploadMode, setUploadMode] = useState<UploadMode>('single');
  const [showStats, setShowStats] = useState(false);
  
  // Real-time processing data
  const [processingQueue, setProcessingQueue] = useState(0);
  const [recentUploads, setRecentUploads] = useState(0);
  const [averageProcessingTime, setAverageProcessingTime] = useState(0);
  
  // Toast state
  const [toast, setToast] = useState<{ message: string; type: ToastType; isVisible: boolean }>({
    message: '',
    type: 'info',
    isVisible: false,
  });

  // Confirm modal state
  const [confirmModal, setConfirmModal] = useState<ConfirmState>({
    isOpen: false,
    title: '',
    message: '',
    confirmText: 'Xác nhận',
    type: 'warning',
    icon: 'warning',
    onConfirm: () => {},
  });

  const showToast = (message: string, type: ToastType) => {
    setToast({ message, type, isVisible: true });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  const showConfirm = (config: Omit<ConfirmState, 'isOpen'>) => {
    setConfirmModal({ ...config, isOpen: true });
  };

  const hideConfirm = () => {
    setConfirmModal(prev => ({ ...prev, isOpen: false }));
  };
  
  // Selection state
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);

  // Fetch documents from API
  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await documentsAPI.getDocuments();
      setDocuments(response.documents || []);
      if (response.categories) {
        setCategories(['all', ...response.categories.filter(c => c !== 'Tất cả')]);
      }
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError(err instanceof Error ? err.message : 'Không thể tải danh sách tài liệu');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Filter documents
  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Pagination - different items per page for grid vs list
  const itemsPerPage = viewMode === 'grid' ? ITEMS_PER_PAGE_GRID : ITEMS_PER_PAGE_LIST;
  const totalPages = Math.ceil(filteredDocuments.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedDocuments = filteredDocuments.slice(startIndex, endIndex);

  // Reset to page 1 when filter or view mode changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, selectedCategory, viewMode]);

  // Selection handlers
  const handleSelectAll = () => {
    if (selectedIds.size === paginatedDocuments.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(paginatedDocuments.map(doc => doc.name)));
    }
  };

  const handleSelectOne = (docName: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(docName)) {
      newSelected.delete(docName);
    } else {
      newSelected.add(docName);
    }
    setSelectedIds(newSelected);
  };

  const clearSelection = () => {
    setSelectedIds(new Set());
  };

  // Handle delete
  const handleDelete = (filename: string) => {
    showConfirm({
      title: 'Xóa tài liệu',
      message: `Bạn có chắc muốn xóa tài liệu "${filename}"?\n\nHành động này sẽ xóa cả file và dữ liệu embedding liên quan.`,
      confirmText: 'Xóa',
      type: 'danger',
      icon: 'delete',
      onConfirm: async () => {
        hideConfirm();
        setDeletingId(filename);
        try {
          await documentsAPI.deleteDocument(filename);
          selectedIds.delete(filename);
          setSelectedIds(new Set(selectedIds));
          await fetchDocuments();
          showToast('Đã xóa tài liệu thành công', 'success');
        } catch (err) {
          console.error('Error deleting document:', err);
          showToast(err instanceof Error ? err.message : 'Không thể xóa tài liệu', 'error');
        } finally {
          setDeletingId(null);
        }
      },
    });
  };

  // Handle bulk delete
  const handleBulkDelete = () => {
    if (selectedIds.size === 0) return;
    
    showConfirm({
      title: 'Xóa nhiều tài liệu',
      message: `Bạn có chắc muốn xóa ${selectedIds.size} tài liệu đã chọn?\n\nHành động này sẽ xóa cả file và dữ liệu embedding liên quan.`,
      confirmText: 'Xóa tất cả',
      type: 'danger',
      icon: 'delete',
      onConfirm: async () => {
        hideConfirm();
        for (const filename of selectedIds) {
          setDeletingId(filename);
          try {
            await documentsAPI.deleteDocument(filename);
          } catch (err) {
            console.error(`Error deleting ${filename}:`, err);
          }
        }
        setDeletingId(null);
        setSelectedIds(new Set());
        await fetchDocuments();
        showToast(`Đã xóa ${selectedIds.size} tài liệu`, 'success');
      },
    });
  };

  // Handle bulk toggle
  const handleBulkToggle = (activate: boolean) => {
    if (selectedIds.size === 0) return;
    
    const action = activate ? 'bật' : 'tắt';
    showConfirm({
      title: activate ? 'Bật nhiều tài liệu' : 'Tắt nhiều tài liệu',
      message: `Bạn có chắc muốn ${action} ${selectedIds.size} tài liệu đã chọn?`,
      confirmText: activate ? 'Bật tất cả' : 'Tắt tất cả',
      type: activate ? 'info' : 'warning',
      icon: activate ? 'power' : 'powerOff',
      onConfirm: async () => {
        hideConfirm();
        let count = 0;
        for (const filename of selectedIds) {
          const doc = documents.find(d => d.name === filename);
          if (doc && doc.is_active !== null && doc.is_active !== activate) {
            setTogglingId(filename);
            try {
              await documentsAPI.toggleActive(filename);
              count++;
            } catch (err) {
              console.error(`Error toggling ${filename}:`, err);
            }
          }
        }
        setTogglingId(null);
        setSelectedIds(new Set());
        await fetchDocuments();
        showToast(`Đã ${action} ${count} tài liệu`, 'success');
      },
    });
  };

  // Handle toggle active
  const handleToggleActive = (filename: string, currentStatus: boolean | null) => {
    if (currentStatus === null) {
      showToast('Tài liệu này chưa được xử lý. Vui lòng đợi xử lý hoàn tất.', 'warning');
      return;
    }
    
    const action = currentStatus ? 'tắt' : 'bật';
    const isDeactivating = currentStatus === true;
    
    showConfirm({
      title: isDeactivating ? 'Tắt tài liệu' : 'Bật tài liệu',
      message: isDeactivating 
        ? `Bạn có chắc muốn tắt tài liệu "${filename}"?\n\nLLM sẽ không thể truy xuất nội dung từ tài liệu này.`
        : `Bạn có chắc muốn bật tài liệu "${filename}"?\n\nLLM sẽ có thể truy xuất nội dung từ tài liệu này.`,
      confirmText: isDeactivating ? 'Tắt' : 'Bật',
      type: isDeactivating ? 'warning' : 'info',
      icon: isDeactivating ? 'powerOff' : 'power',
      onConfirm: async () => {
        hideConfirm();
        setTogglingId(filename);
        try {
          const response = await documentsAPI.toggleActive(filename);
          if (response.success) {
            await fetchDocuments();
            showToast(response.message, 'success');
          }
        } catch (err) {
          console.error('Error toggling document:', err);
          showToast(err instanceof Error ? err.message : 'Không thể thay đổi trạng thái tài liệu', 'error');
        } finally {
          setTogglingId(null);
        }
      },
    });
  };

  // Handle download - Use Supabase Storage URL
  const handleDownload = (filename: string) => {
    const url = getDocumentUrl(filename);
    window.open(url, '_blank');
  };

  // Handle view - Use Supabase Storage URL
  const handleView = (filename: string) => {
    const url = getDocumentUrl(filename);
    window.open(url, '_blank');
  };

  // Calculate statistics
  const stats = {
    total: documents.length,
    active: documents.filter(d => d.status === 'active').length,
    inactive: documents.filter(d => d.status === 'inactive').length,
    totalChunks: documents.reduce((sum, doc) => sum + (doc.chunks || 0), 0),
    totalSize: documents.reduce((sum, doc) => sum + doc.size, 0),
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getCategoryLabel = (value: string) => {
    if (value === 'all') return 'Tất cả';
    return value;
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Enhanced Action Bar with Upload Options */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-5 md:p-6">
          {/* Top Section: Search */}
          <div className="mb-4">
            <div className="relative w-full">
              <div className="absolute left-0 top-0 bottom-0 flex items-center pl-4 pointer-events-none">
                <Search className="text-gray-400 w-5 h-5" />
              </div>
              <input
                type="text"
                placeholder="Tìm kiếm tài liệu theo tên hoặc nội dung..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full h-12 pl-12 pr-4 border border-gray-200 rounded-lg text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent hover:border-gray-300 transition-all"
              />
            </div>
          </div>

          {/* Bottom Section: Filters & Controls */}
          <div className="flex flex-col lg:flex-row gap-3 items-stretch lg:items-center">
            {/* Left Side: Filters */}
            <div className="flex flex-col sm:flex-row gap-3 flex-1">
              {/* Category Filter */}
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="h-10 pl-9 pr-3 border border-gray-200 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent hover:border-gray-300 cursor-pointer transition-all appearance-none bg-white min-w-[120px]"
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>
                      {getCategoryLabel(cat)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Upload Mode Selector */}
              <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
                <button
                  onClick={() => setUploadMode('single')}
                  className={`h-10 px-3 text-sm font-medium transition-all flex items-center gap-2 ${
                    uploadMode === 'single' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                  title="Upload đơn lẻ"
                >
                  <FileText className="w-4 h-4" />
                  <span className="hidden sm:inline">Đơn lẻ</span>
                </button>
                <button
                  onClick={() => setUploadMode('batch')}
                  className={`h-10 px-3 text-sm font-medium transition-all flex items-center gap-2 ${
                    uploadMode === 'batch' 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                  title="Upload hàng loạt"
                >
                  <Archive className="w-4 h-4" />
                  <span className="hidden sm:inline">Hàng loạt</span>
                </button>
              </div>
            </div>

            {/* Right Side: Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => setShowStats(!showStats)}
                className={`h-10 px-3 rounded-lg transition-all flex items-center gap-2 text-sm font-medium ${
                  showStats 
                    ? 'bg-green-600 text-white shadow-md' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
                title={showStats ? 'Ẩn thống kê' : 'Hiện thống kê'}
              >
                <BarChart3 className="w-4 h-4" />
                <span className="hidden lg:inline">
                  {showStats ? 'Ẩn thống kê' : 'Thống kê'}
                </span>
              </button>
              
              <button
                onClick={fetchDocuments}
                disabled={isLoading}
                className="h-10 px-3 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:cursor-not-allowed text-gray-700 rounded-lg transition-all flex items-center gap-2 text-sm font-medium"
                title="Làm mới"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span className="hidden md:inline">Làm mới</span>
              </button>

              {/* View Toggle */}
              <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`h-10 px-3 transition-all ${
                    viewMode === 'grid' 
                      ? 'bg-red-600 text-white' 
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                  title="Hiển thị dạng lưới"
                >
                  <LayoutGrid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`h-10 px-3 transition-all ${
                    viewMode === 'list' 
                      ? 'bg-red-600 text-white' 
                      : 'bg-white text-gray-600 hover:bg-gray-50'
                  }`}
                  title="Hiển thị dạng danh sách"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>

              {/* Upload Button */}
              <button 
                onClick={() => {
                  if (uploadMode === 'single') {
                    setIsUploadModalOpen(true);
                  } else {
                    setIsBatchUploadModalOpen(true);
                  }
                }}
                className={`h-10 px-4 rounded-lg transition-all flex items-center gap-2 shadow-sm text-sm font-medium ${
                  uploadMode === 'single'
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                }`}
              >
                {uploadMode === 'single' ? (
                  <>
                    <Plus className="w-4 h-4" />
                    <span className="hidden sm:inline">Thêm mới</span>
                    <span className="sm:hidden">Thêm</span>
                  </>
                ) : (
                  <>
                    <Archive className="w-4 h-4" />
                    <span className="hidden sm:inline">Upload nhiều</span>
                    <span className="sm:hidden">Nhiều</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Quick Stats Dashboard */}
        {showStats && (
          <QuickStats
            totalDocuments={stats.total}
            activeDocuments={stats.active}
            totalChunks={stats.totalChunks}
            totalSize={stats.totalSize}
            recentUploads={recentUploads}
            processingQueue={processingQueue}
            averageProcessingTime={averageProcessingTime}
            uploadSuccess={stats.active}
            className="animate-in slide-in-from-top-4 duration-300"
          />
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-red-800">{error}</p>
            <button
              onClick={fetchDocuments}
              className="ml-auto text-red-600 hover:text-red-800 underline text-sm"
            >
              Thử lại
            </button>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 xs:gap-4">
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 xs:p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs xs:text-sm text-gray-600">Tổng tài liệu</p>
                <p className="text-xl xs:text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
              </div>
              <FileText className="w-6 h-6 xs:w-8 xs:h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 xs:p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs xs:text-sm text-gray-600">Đang hoạt động</p>
                <p className="text-xl xs:text-2xl font-bold text-green-600 mt-1">{stats.active}</p>
              </div>
              <div className="w-2 h-2 xs:w-3 xs:h-3 bg-green-500 rounded-full animate-pulse" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 xs:p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs xs:text-sm text-gray-600">Tổng chunks</p>
                <p className="text-xl xs:text-2xl font-bold text-gray-900 mt-1">{stats.totalChunks}</p>
              </div>
              <Database className="w-6 h-6 xs:w-8 xs:h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 xs:p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs xs:text-sm text-gray-600">Dung lượng</p>
                <p className="text-lg xs:text-2xl font-bold text-gray-900 mt-1">
                  {formatFileSize(stats.totalSize)}
                </p>
              </div>
              <HardDrive className="w-6 h-6 xs:w-8 xs:h-8 text-yellow-500" />
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-red-600 animate-spin" />
            <span className="ml-3 text-gray-600">Đang tải danh sách tài liệu...</span>
          </div>
        )}

        {/* Documents View */}
        {!isLoading && filteredDocuments.length > 0 && (
          <>
            {/* Grid View */}
            {viewMode === 'grid' && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 xs:gap-6">
                  {paginatedDocuments.map((doc) => (
                    <div 
                      key={doc.id} 
                      className="bg-white rounded-lg xs:rounded-xl shadow-md border border-gray-200 p-4 xs:p-6 hover:shadow-lg transition-all"
                    >
                      <div className="flex items-start justify-between mb-3 xs:mb-4">
                        <div className="w-10 h-10 xs:w-12 xs:h-12 bg-red-100 rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 xs:w-6 xs:h-6 text-red-600" />
                        </div>
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          doc.status === 'active'
                            ? 'bg-green-100 text-green-800'
                          : doc.status === 'processing'
                          ? 'bg-yellow-100 text-yellow-800'
                          : doc.status === 'pending'
                          ? 'bg-orange-100 text-orange-800'
                          : doc.status === 'inactive'
                          ? 'bg-gray-100 text-gray-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {doc.status === 'active' ? 'Hoạt động' : 
                         doc.status === 'processing' ? 'Đang xử lý' : 
                         doc.status === 'pending' ? 'Chưa xử lý' :
                         doc.status === 'inactive' ? 'Đã tắt' : 'Lỗi'}
                      </span>
                    </div>

                    <h3 className="text-base xs:text-lg font-semibold text-gray-900 mb-2 line-clamp-2" title={doc.name}>
                      {doc.name}
                    </h3>

                    <div className="space-y-1.5 xs:space-y-2 mb-3 xs:mb-4">
                      <div className="flex items-center justify-between text-xs xs:text-sm">
                        <span className="text-gray-600">Danh mục:</span>
                        <span className="font-medium text-gray-900 truncate ml-2">{doc.category}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs xs:text-sm">
                        <span className="text-gray-600">Dung lượng:</span>
                        <span className="font-medium text-gray-900">{doc.size_formatted}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs xs:text-sm">
                        <span className="text-gray-600">Chunks:</span>
                        <span className="font-medium text-gray-900">{doc.chunks || 0}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs xs:text-sm">
                        <span className="text-gray-600">Ngày tải lên:</span>
                        <span className="font-medium text-gray-900 text-xs">{doc.uploadDate}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-3 xs:pt-4 border-t border-gray-200">
                      {/* Toggle Active Button */}
                      <button 
                        onClick={() => handleToggleActive(doc.name, doc.is_active)}
                        disabled={togglingId === doc.name || doc.status === 'pending'}
                        className={`p-1.5 xs:p-2 rounded-lg transition-colors disabled:opacity-50 ${
                          doc.is_active === false 
                            ? 'text-gray-500 hover:bg-gray-100' 
                            : 'text-green-600 hover:bg-green-50'
                        }`}
                        title={doc.is_active === false ? 'Bật tài liệu' : 'Tắt tài liệu'}
                      >
                        {togglingId === doc.name ? (
                          <Loader2 className="w-4 h-4 xs:w-5 xs:h-5 animate-spin" />
                        ) : doc.is_active === false ? (
                          <PowerOff className="w-4 h-4 xs:w-5 xs:h-5" />
                        ) : (
                          <Power className="w-4 h-4 xs:w-5 xs:h-5" />
                        )}
                      </button>
                      <button 
                        onClick={() => handleView(doc.name)}
                        className="p-1.5 xs:p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" 
                        title="Xem"
                      >
                        <Eye className="w-4 h-4 xs:w-5 xs:h-5" />
                      </button>
                      <button 
                        onClick={() => handleDownload(doc.name)}
                        className="p-1.5 xs:p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors" 
                        title="Tải xuống"
                      >
                        <Download className="w-4 h-4 xs:w-5 xs:h-5" />
                      </button>
                      <button 
                        onClick={() => handleDelete(doc.name)}
                        disabled={deletingId === doc.name}
                        className="p-1.5 xs:p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50" 
                        title="Xóa"
                      >
                        {deletingId === doc.name ? (
                          <Loader2 className="w-4 h-4 xs:w-5 xs:h-5 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4 xs:w-5 xs:h-5" />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Grid View Pagination */}
              {totalPages > 1 && (
                <div className="mt-4 xs:mt-6 bg-white rounded-xl shadow-md border border-gray-200 px-4 xs:px-6 py-3 xs:py-4 flex flex-col xs:flex-row items-center justify-between gap-3 xs:gap-0">
                  <p className="text-xs xs:text-sm text-gray-600 order-2 xs:order-1">
                    <span className="hidden sm:inline">
                      Hiển thị {startIndex + 1} - {Math.min(endIndex, filteredDocuments.length)} trong tổng số {filteredDocuments.length} tài liệu
                    </span>
                    <span className="sm:hidden">
                      {startIndex + 1}-{Math.min(endIndex, filteredDocuments.length)} / {filteredDocuments.length}
                    </span>
                  </p>
                  <div className="flex items-center gap-1 order-1 xs:order-2">
                    <button
                      onClick={() => setCurrentPage(1)}
                      disabled={currentPage === 1}
                      className="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Trang đầu"
                    >
                      <ChevronsLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Trang trước"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    
                    {/* Page Numbers - Hidden on mobile */}
                    <div className="hidden sm:flex items-center gap-1">
                      {Array.from({ length: totalPages }, (_, i) => i + 1)
                        .filter(page => {
                          if (totalPages <= 5) return true;
                          if (page === 1 || page === totalPages) return true;
                          if (Math.abs(page - currentPage) <= 1) return true;
                          return false;
                        })
                        .map((page, index, arr) => (
                          <React.Fragment key={page}>
                            {index > 0 && arr[index - 1] !== page - 1 && (
                              <span className="px-2 text-gray-400">...</span>
                            )}
                            <button
                              onClick={() => setCurrentPage(page)}
                              className={`min-w-[36px] h-9 px-3 rounded-lg transition-colors ${
                                currentPage === page
                                  ? 'bg-red-600 text-white'
                                  : 'text-gray-600 hover:bg-gray-200'
                              }`}
                            >
                              {page}
                            </button>
                          </React.Fragment>
                        ))}
                    </div>
                    
                    {/* Current Page Indicator - Mobile only */}
                    <div className="sm:hidden px-3 py-2 text-xs text-gray-700 bg-gray-100 rounded-lg border">
                      {currentPage} / {totalPages}
                    </div>
                    
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Trang sau"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setCurrentPage(totalPages)}
                      disabled={currentPage === totalPages}
                      className="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Trang cuối"
                    >
                      <ChevronsRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
              </>
            )}

            {/* List View */}
            {viewMode === 'list' && (
              <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
                {/* Bulk Actions Bar */}
                {selectedIds.size > 0 && (
                  <div className="bg-red-50 border-b border-red-200 px-4 xs:px-6 py-3 flex flex-col xs:flex-row xs:items-center justify-between gap-3 xs:gap-0">
                    <span className="text-sm font-medium text-red-800">
                      Đã chọn {selectedIds.size} tài liệu
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleBulkToggle(true)}
                        className="flex-1 xs:flex-none px-3 py-1.5 text-sm bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center justify-center gap-1"
                      >
                        <Power className="w-3 h-3 xs:w-4 xs:h-4" />
                        <span>Bật</span>
                      </button>
                      <button
                        onClick={() => handleBulkToggle(false)}
                        className="flex-1 xs:flex-none px-3 py-1.5 text-sm bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors flex items-center justify-center gap-1"
                      >
                        <PowerOff className="w-3 h-3 xs:w-4 xs:h-4" />
                        <span>Tắt</span>
                      </button>
                      <button
                        onClick={handleBulkDelete}
                        className="flex-1 xs:flex-none px-3 py-1.5 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center justify-center gap-1"
                      >
                        <Trash2 className="w-3 h-3 xs:w-4 xs:h-4" />
                        <span>Xóa</span>
                      </button>
                      <button
                        onClick={clearSelection}
                        className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
                      >
                        <span className="hidden xs:inline">Bỏ chọn</span>
                        <span className="xs:hidden">Bỏ</span>
                      </button>
                    </div>
                  </div>
                )}
                
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-4 text-left">
                        <button
                          onClick={handleSelectAll}
                          className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                            selectedIds.size === paginatedDocuments.length && paginatedDocuments.length > 0
                              ? 'bg-red-600 border-red-600 text-white'
                              : selectedIds.size > 0
                              ? 'bg-red-200 border-red-400'
                              : 'border-gray-300 hover:border-red-400'
                          }`}
                        >
                          {selectedIds.size === paginatedDocuments.length && paginatedDocuments.length > 0 && (
                            <Check className="w-3 h-3" />
                          )}
                        </button>
                      </th>
                      <th className="px-4 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Tên tài liệu
                      </th>
                      <th className="px-4 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Danh mục
                      </th>
                      <th className="px-4 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Dung lượng
                      </th>
                      <th className="px-4 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Chunks
                      </th>
                      <th className="px-4 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Trạng thái
                      </th>
                      <th className="px-4 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Ngày tải lên
                      </th>
                      <th className="px-4 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Thao tác
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {paginatedDocuments.map((doc) => (
                      <tr 
                        key={doc.id} 
                        className={`hover:bg-gray-50 transition-colors ${selectedIds.has(doc.name) ? 'bg-red-50' : ''}`}
                      >
                        <td className="px-4 py-4">
                          <button
                            onClick={() => handleSelectOne(doc.name)}
                            className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                              selectedIds.has(doc.name)
                                ? 'bg-red-600 border-red-600 text-white'
                                : 'border-gray-300 hover:border-red-400'
                            }`}
                          >
                            {selectedIds.has(doc.name) && <Check className="w-3 h-3" />}
                          </button>
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
                              <FileText className="w-5 h-5 text-red-600" />
                            </div>
                            <span className="font-medium text-gray-900 truncate max-w-[200px]" title={doc.name}>
                              {doc.name}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-600">
                          {doc.category}
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-600">
                          {doc.size_formatted}
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-600">
                          {doc.chunks || 0}
                        </td>
                        <td className="px-4 py-4">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            doc.status === 'active'
                              ? 'bg-green-100 text-green-800'
                              : doc.status === 'processing'
                              ? 'bg-yellow-100 text-yellow-800'
                              : doc.status === 'pending'
                              ? 'bg-orange-100 text-orange-800'
                              : doc.status === 'inactive'
                              ? 'bg-gray-100 text-gray-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {doc.status === 'active' ? 'Hoạt động' : 
                             doc.status === 'processing' ? 'Đang xử lý' : 
                             doc.status === 'pending' ? 'Chưa xử lý' :
                             doc.status === 'inactive' ? 'Đã tắt' : 'Lỗi'}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-600">
                          {doc.uploadDate}
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-center justify-end gap-1">
                            <button 
                              onClick={() => handleToggleActive(doc.name, doc.is_active)}
                              disabled={togglingId === doc.name || doc.status === 'pending'}
                              className={`p-2 rounded-lg transition-colors disabled:opacity-50 ${
                                doc.is_active === false 
                                  ? 'text-gray-500 hover:bg-gray-100' 
                                  : 'text-green-600 hover:bg-green-50'
                              }`}
                              title={doc.is_active === false ? 'Bật tài liệu' : 'Tắt tài liệu'}
                            >
                              {togglingId === doc.name ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : doc.is_active === false ? (
                                <PowerOff className="w-4 h-4" />
                              ) : (
                                <Power className="w-4 h-4" />
                              )}
                            </button>
                            <button 
                              onClick={() => handleView(doc.name)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" 
                              title="Xem"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={() => handleDownload(doc.name)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors" 
                              title="Tải xuống"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={() => handleDelete(doc.name)}
                              disabled={deletingId === doc.name}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50" 
                              title="Xóa"
                            >
                              {deletingId === doc.name ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <Trash2 className="w-4 h-4" />
                              )}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="bg-gray-50 border-t border-gray-200 px-4 xs:px-6 py-3 xs:py-4 flex flex-col xs:flex-row items-center justify-between gap-3 xs:gap-0">
                    <p className="text-xs xs:text-sm text-gray-600 order-2 xs:order-1">
                      <span className="hidden sm:inline">
                        Hiển thị {startIndex + 1} - {Math.min(endIndex, filteredDocuments.length)} trong tổng số {filteredDocuments.length} tài liệu
                      </span>
                      <span className="sm:hidden">
                        {startIndex + 1}-{Math.min(endIndex, filteredDocuments.length)} / {filteredDocuments.length}
                      </span>
                    </p>
                    <div className="flex items-center gap-1 order-1 xs:order-2">
                      <button
                        onClick={() => setCurrentPage(1)}
                        disabled={currentPage === 1}
                        className="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Trang đầu"
                      >
                        <ChevronsLeft className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                        className="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Trang trước"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      
                      {/* Page Numbers - Hidden on mobile */}
                      <div className="hidden sm:flex items-center gap-1">
                        {Array.from({ length: totalPages }, (_, i) => i + 1)
                          .filter(page => {
                            if (totalPages <= 5) return true;
                            if (page === 1 || page === totalPages) return true;
                            if (Math.abs(page - currentPage) <= 1) return true;
                            return false;
                          })
                          .map((page, index, arr) => (
                            <React.Fragment key={page}>
                              {index > 0 && arr[index - 1] !== page - 1 && (
                                <span className="px-2 text-gray-400">...</span>
                              )}
                              <button
                                onClick={() => setCurrentPage(page)}
                                className={`min-w-[36px] h-9 px-3 rounded-lg transition-colors ${
                                  currentPage === page
                                    ? 'bg-red-600 text-white'
                                    : 'text-gray-600 hover:bg-gray-200'
                                }`}
                              >
                                {page}
                              </button>
                            </React.Fragment>
                          ))}
                      </div>
                      
                      {/* Current Page Indicator - Mobile only */}
                      <div className="sm:hidden px-3 py-2 text-xs text-gray-700 bg-white rounded-lg border">
                        {currentPage} / {totalPages}
                      </div>
                      
                      <button
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                        className="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Trang sau"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setCurrentPage(totalPages)}
                        disabled={currentPage === totalPages}
                        className="p-2 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Trang cuối"
                      >
                        <ChevronsRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!isLoading && filteredDocuments.length === 0 && !error && (
          <div className="bg-white rounded-lg xs:rounded-xl shadow-md border border-gray-200 p-8 xs:p-12 text-center">
            <FileText className="w-12 h-12 xs:w-16 xs:h-16 text-gray-400 mx-auto mb-3 xs:mb-4" />
            <p className="text-gray-600 text-base xs:text-lg mb-2">
              {documents.length === 0 
                ? 'Chưa có tài liệu nào'
                : 'Không tìm thấy tài liệu nào'}
            </p>
            <p className="text-gray-500 text-sm mt-2">
              {documents.length === 0 
                ? 'Bắt đầu bằng cách upload tài liệu PDF mới'
                : 'Thử thay đổi từ khóa tìm kiếm hoặc bộ lọc'}
            </p>
            {documents.length === 0 && (
              <button
                onClick={() => setIsUploadModalOpen(true)}
                className="mt-4 px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors inline-flex items-center gap-2"
              >
                <Upload className="w-4 h-4" />
                Upload tài liệu đầu tiên
              </button>
            )}
          </div>
        )}
      </div>

      {/* Enhanced Upload Modals */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={fetchDocuments}
      />

      <BatchUploadModal
        isOpen={isBatchUploadModalOpen}
        onClose={() => setIsBatchUploadModalOpen(false)}
        onUploadSuccess={fetchDocuments}
      />

      {/* Confirm Modal */}
      <ConfirmModal
        isOpen={confirmModal.isOpen}
        onClose={hideConfirm}
        onConfirm={confirmModal.onConfirm}
        title={confirmModal.title}
        message={confirmModal.message}
        confirmText={confirmModal.confirmText}
        type={confirmModal.type}
        icon={confirmModal.icon}
      />

      {/* Toast Notification */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
      />
    </AdminLayout>
  );
};

export default DocumentsPage;
