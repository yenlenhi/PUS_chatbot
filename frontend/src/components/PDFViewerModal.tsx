'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { X, Download, ExternalLink, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { getDocumentUrl } from '@/lib/supabase';

interface PDFViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  filename: string;
  initialPage?: number;
  backendUrl?: string;
  useSupabase?: boolean; // Flag to use Supabase Storage URLs
}

const PDFViewerModal: React.FC<PDFViewerModalProps> = ({
  isOpen,
  onClose,
  filename,
  initialPage = 1,
  backendUrl = 'http://localhost:8000',
  useSupabase = true // Default to Supabase Storage
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState<number | null>(null);

  // Use Supabase Storage URL or fallback to backend API
  const pdfUrl = useSupabase 
    ? getDocumentUrl(filename)
    : `${backendUrl}/api/v1/documents/${encodeURIComponent(filename)}`;

  const handlePrevPage = useCallback(() => {
    if (currentPage > 1) setCurrentPage(p => p - 1);
  }, [currentPage]);

  const handleNextPage = useCallback(() => {
    if (!totalPages || currentPage < totalPages) setCurrentPage(p => p + 1);
  }, [currentPage, totalPages]);

  useEffect(() => {
    if (isOpen) {
      setCurrentPage(initialPage);
      setIsLoading(true);
      setError(null);
      
      // Fetch document info for page count
      fetch(`${backendUrl}/api/v1/documents/${encodeURIComponent(filename)}/info`)
        .then(res => res.json())
        .then(data => {
          if (data.page_count) {
            setTotalPages(data.page_count);
          }
        })
        .catch(err => console.log('Could not fetch page count:', err));
    }
  }, [isOpen, filename, initialPage, backendUrl]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') handlePrevPage();
      if (e.key === 'ArrowRight') handleNextPage();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, handlePrevPage, handleNextPage]);

  const handleDownload = () => {
    window.open(pdfUrl, '_blank');
  };

  const handleOpenInNewTab = () => {
    const urlWithPage = `${pdfUrl}#page=${currentPage}`;
    window.open(urlWithPage, '_blank');
  };

  const formatFileName = (name: string) => {
    return name.replace(/\.[^/.]+$/, '').replace(/_/g, ' ');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-6xl h-[90vh] mx-4 bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold truncate max-w-md" title={filename}>
              {formatFileName(filename)}
            </h3>
            {initialPage && (
              <span className="text-sm bg-white/20 px-2 py-0.5 rounded">
                Trang {initialPage}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {/* Page navigation */}
            <div className="flex items-center gap-1 bg-white/20 rounded px-2 py-1">
              <button
                onClick={handlePrevPage}
                disabled={currentPage <= 1}
                className="p-1 hover:bg-white/20 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-sm min-w-[80px] text-center">
                {currentPage} {totalPages ? `/ ${totalPages}` : ''}
              </span>
              <button
                onClick={handleNextPage}
                disabled={totalPages !== null && currentPage >= totalPages}
                className="p-1 hover:bg-white/20 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
            
            {/* Actions */}
            <button
              onClick={handleOpenInNewTab}
              className="p-2 hover:bg-white/20 rounded transition-colors"
              title="Mở trong tab mới"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
            <button
              onClick={handleDownload}
              className="p-2 hover:bg-white/20 rounded transition-colors"
              title="Tải xuống"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded transition-colors"
              title="Đóng (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* PDF Content */}
        <div className="flex-1 relative bg-gray-100">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="w-8 h-8 animate-spin text-red-600" />
                <p className="text-gray-600">Đang tải tài liệu...</p>
              </div>
            </div>
          )}
          
          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
              <div className="text-center p-6">
                <p className="text-red-600 font-medium mb-2">Không thể tải tài liệu</p>
                <p className="text-gray-500 text-sm">{error}</p>
                <button
                  onClick={handleOpenInNewTab}
                  className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Mở trong tab mới
                </button>
              </div>
            </div>
          )}

          <iframe
            src={`${pdfUrl}#page=${currentPage}`}
            className="w-full h-full border-0"
            onLoad={() => setIsLoading(false)}
            onError={() => {
              setIsLoading(false);
              setError('Không thể hiển thị PDF trong trình duyệt');
            }}
            title={filename}
          />
        </div>

        {/* Footer with hint */}
        <div className="px-4 py-2 bg-gray-50 border-t text-xs text-gray-500 flex justify-between">
          <span>Sử dụng phím ← → để chuyển trang • Esc để đóng</span>
          <span>{filename}</span>
        </div>
      </div>
    </div>
  );
};

export default PDFViewerModal;

