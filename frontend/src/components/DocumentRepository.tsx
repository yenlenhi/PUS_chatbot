'use client';

import React, { useState, useEffect } from 'react';
import { 
  X, 
  Search, 
  FileText, 
  Download, 
  Eye, 
  Loader2,
  FolderOpen,
  Calendar,
  HardDrive,
  RefreshCw
} from 'lucide-react';

interface Document {
  filename: string;
  size_bytes: number;
  modified_at: number;
  page_count?: number;
}

interface DocumentRepositoryProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenDocument: (filename: string) => void;
  backendUrl?: string;
}

const DocumentRepository: React.FC<DocumentRepositoryProps> = ({
  isOpen,
  onClose,
  onOpenDocument,
  backendUrl = 'http://localhost:8000'
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [filteredDocs, setFilteredDocs] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${backendUrl}/api/v1/documents`);
      if (!response.ok) throw new Error('Failed to fetch documents');
      const data = await response.json();
      setDocuments(data.documents || []);
      setFilteredDocs(data.documents || []);
    } catch (err) {
      setError('Không thể tải danh sách tài liệu');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDocuments();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredDocs(documents);
    } else {
      const query = searchQuery.toLowerCase();
      setFilteredDocs(
        documents.filter(doc => 
          doc.filename.toLowerCase().includes(query)
        )
      );
    }
  }, [searchQuery, documents]);

  const formatFileName = (filename: string) => {
    return filename.replace(/\.[^/.]+$/, '').replace(/_/g, ' ');
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleDownload = (filename: string) => {
    window.open(`${backendUrl}/api/v1/documents/${encodeURIComponent(filename)}`, '_blank');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      
      {/* Modal */}
      <div className="relative w-full max-w-4xl max-h-[85vh] mx-4 bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FolderOpen className="w-6 h-6" />
              <div>
                <h2 className="text-lg font-semibold">Kho tài liệu</h2>
                <p className="text-red-100 text-sm">{documents.length} tài liệu có sẵn</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchDocuments}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                title="Làm mới"
              >
                <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={onClose}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          {/* Search bar */}
          <div className="mt-4 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Tìm kiếm tài liệu..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30"
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-64">
              <Loader2 className="w-10 h-10 animate-spin text-red-600 mb-3" />
              <p className="text-gray-500">Đang tải tài liệu...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-64 text-red-500">
              <p>{error}</p>
              <button
                onClick={fetchDocuments}
                className="mt-3 px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
              >
                Thử lại
              </button>
            </div>
          ) : filteredDocs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-400">
              <FileText className="w-12 h-12 mb-3 opacity-50" />
              <p>{searchQuery ? 'Không tìm thấy tài liệu phù hợp' : 'Chưa có tài liệu nào'}</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredDocs.map((doc, index) => (
                <div
                  key={index}
                  className="flex items-center gap-4 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors group"
                >
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-red-600" />
                    </div>
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate" title={doc.filename}>
                      {formatFileName(doc.filename)}
                    </p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <HardDrive className="w-3 h-3" />
                        {formatFileSize(doc.size_bytes)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(doc.modified_at)}
                      </span>
                      {doc.page_count && (
                        <span>{doc.page_count} trang</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => onOpenDocument(doc.filename)}
                      className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Xem tài liệu"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDownload(doc.filename)}
                      className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Tải xuống"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 bg-gray-50 border-t text-xs text-gray-500 text-center">
          Nhấn vào tài liệu để xem chi tiết hoặc tải xuống
        </div>
      </div>
    </div>
  );
};

export default DocumentRepository;

