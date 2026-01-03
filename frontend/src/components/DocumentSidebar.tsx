'use client';

import React, { useState } from 'react';
import { 
  FileText, 
  ChevronRight, 
  ChevronLeft, 
  Eye, 
  Copy, 
  Check, 
  X, 
  Book,
  ChevronDown,
  ChevronUp,
  Hash
} from 'lucide-react';
import type { SourceReference } from '@/types';

interface DocumentSidebarProps {
  sourceReferences: SourceReference[];
  isOpen: boolean;
  onToggle: () => void;
  onOpenDocument: (filename: string, page?: number) => void;
  onClear: () => void;
}

const DocumentSidebar: React.FC<DocumentSidebarProps> = ({
  sourceReferences,
  isOpen,
  onToggle,
  onOpenDocument,
  onClear
}) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const formatFileName = (filename: string) => {
    return filename
      .replace(/\.[^/.]+$/, '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatScore = (score: number) => Math.round(score * 100);

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'bg-green-100 text-green-700 border-green-200';
    if (score >= 0.5) return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    return 'bg-gray-100 text-gray-600 border-gray-200';
  };

  const getScoreBadgeColor = (score: number) => {
    if (score >= 0.7) return 'bg-green-500';
    if (score >= 0.5) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  const handleCopyReference = async (ref: SourceReference, index: number) => {
    const citation = `${formatFileName(ref.filename)}${ref.page_number ? `, trang ${ref.page_number}` : ''}`;
    try {
      await navigator.clipboard.writeText(citation);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <>
      {/* Toggle Button - Always visible */}
      <button
        onClick={onToggle}
        className={`fixed top-1/2 -translate-y-1/2 z-40 bg-red-600 text-white p-1.5 sm:p-2 rounded-l-lg shadow-lg hover:bg-red-700 transition-all duration-300 ${
          isOpen ? 'right-[calc(100vw-2rem)] sm:right-80 md:right-96' : 'right-0'
        }`}
        title={isOpen ? 'Ẩn tài liệu' : 'Hiện tài liệu'}
      >
        {isOpen ? <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5" /> : <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />}
        {!isOpen && sourceReferences.length > 0 && (
          <span className="absolute -top-1 sm:-top-2 -left-1 sm:-left-2 bg-yellow-500 text-white text-xs rounded-full w-4 h-4 sm:w-5 sm:h-5 flex items-center justify-center">
            {sourceReferences.length}
          </span>
        )}
      </button>

      {/* Sidebar Panel */}
      <div
        className={`fixed top-0 right-0 h-full bg-white shadow-2xl z-30 transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        } w-[calc(100vw-2rem)] max-w-sm sm:w-80 md:w-96`}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white p-3 sm:p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Book className="w-4 h-4 sm:w-5 sm:h-5" />
              <h3 className="font-semibold text-sm sm:text-base">Tài liệu tham khảo</h3>
            </div>
            <div className="flex items-center gap-2">
              {sourceReferences.length > 0 && (
                <span className="text-xs bg-white/20 px-2 py-1 rounded">
                  {sourceReferences.length} tài liệu
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="h-[calc(100%-120px)] overflow-y-auto p-2 sm:p-3">
          {sourceReferences.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <FileText className="w-12 h-12 mb-3 opacity-50" />
              <p className="text-sm text-center">
                Chưa có tài liệu tham khảo.<br />
                Hãy đặt câu hỏi để xem nguồn tài liệu.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {sourceReferences.map((ref, index) => (
                <div
                  key={ref.chunk_id || index}
                  className="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
                >
                  {/* Card Header */}
                  <div className="p-3">
                    <div className="flex items-start gap-2">
                      {/* Score indicator */}
                      <div className={`w-2 h-2 rounded-full mt-2 ${getScoreBadgeColor(ref.relevance_score)}`} />
                      
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate" title={formatFileName(ref.filename)}>
                          {formatFileName(ref.filename)}
                        </p>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          <span className={`text-xs px-1.5 py-0.5 rounded border ${getScoreColor(ref.relevance_score)}`}>
                            {formatScore(ref.relevance_score)}%
                          </span>
                          {ref.page_number && (
                            <span className="text-xs text-gray-500 flex items-center gap-0.5">
                              <Hash className="w-3 h-3" />
                              Trang {ref.page_number}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Snippet */}
                    <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                      {ref.content_snippet}
                    </p>

                    {/* Expand button */}
                    <button
                      onClick={() => toggleExpand(index)}
                      className="text-xs text-red-600 hover:text-red-700 mt-2 flex items-center gap-1"
                    >
                      {expandedIndex === index ? (
                        <>Thu gọn <ChevronUp className="w-3 h-3" /></>
                      ) : (
                        <>Xem thêm <ChevronDown className="w-3 h-3" /></>
                      )}
                    </button>
                  </div>

                  {/* Expanded content */}
                  {expandedIndex === index && (
                    <div className="px-3 pb-3 border-t border-gray-200 bg-white">
                      <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-700 max-h-40 overflow-y-auto">
                        {ref.full_content}
                      </div>
                      {ref.heading && (
                        <p className="text-xs text-gray-500 mt-2">
                          <strong>Mục:</strong> {ref.heading}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="flex border-t border-gray-200 divide-x divide-gray-200">
                    <button
                      onClick={() => onOpenDocument(ref.filename, ref.page_number || undefined)}
                      className="flex-1 py-2 text-xs text-gray-600 hover:bg-red-50 hover:text-red-600 flex items-center justify-center gap-1 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Xem PDF
                    </button>
                    <button
                      onClick={() => handleCopyReference(ref, index)}
                      className="flex-1 py-2 text-xs text-gray-600 hover:bg-blue-50 hover:text-blue-600 flex items-center justify-center gap-1 transition-colors"
                    >
                      {copiedIndex === index ? (
                        <><Check className="w-3.5 h-3.5 text-green-600" /> Đã sao chép</>
                      ) : (
                        <><Copy className="w-3.5 h-3.5" /> Sao chép</>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {sourceReferences.length > 0 && (
          <div className="absolute bottom-0 left-0 right-0 p-3 bg-gray-50 border-t">
            <button
              onClick={onClear}
              className="w-full py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg border border-gray-200 flex items-center justify-center gap-2 transition-colors"
            >
              <X className="w-4 h-4" />
              Xóa tài liệu tham khảo
            </button>
          </div>
        )}
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-20 md:hidden"
          onClick={onToggle}
        />
      )}
    </>
  );
};

export default DocumentSidebar;

