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
  BookOpen,
  ChevronDown,
  ChevronUp,
  FileSearch,
} from 'lucide-react';
import type { SourceReference } from '@/types';
import { getDocumentDisplayName } from '@/lib/documentNames';

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
  onClear,
}) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const formatScore = (score: number) => Math.round(score * 100);

  const getScoreStyle = (score: number): { bar: string; text: string; bg: string } => {
    if (score >= 0.7) return { bar: 'bg-emerald-500', text: 'text-emerald-700', bg: 'bg-emerald-50' };
    if (score >= 0.5) return { bar: 'bg-amber-400', text: 'text-amber-700', bg: 'bg-amber-50' };
    return { bar: 'bg-slate-400', text: 'text-slate-600', bg: 'bg-slate-50' };
  };

  const handleCopyReference = async (ref: SourceReference, index: number) => {
    const citation = `${getDocumentDisplayName(ref.filename)}${ref.page_number ? `, trang ${ref.page_number}` : ''}`;
    try {
      await navigator.clipboard.writeText(citation);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch {
      // clipboard unavailable
    }
  };

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={onToggle}
        className={`fixed top-1/2 -translate-y-1/2 z-40 bg-red-600 text-white p-1.5 sm:p-2 rounded-l-lg shadow-lg hover:bg-red-700 transition-all duration-300 ${
          isOpen ? 'right-[calc(100vw-2rem)] sm:right-80 md:right-96' : 'right-0'
        }`}
        title={isOpen ? 'Ẩn tài liệu' : 'Hiện tài liệu'}
      >
        {isOpen ? (
          <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5" />
        ) : (
          <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />
        )}
        {!isOpen && sourceReferences.length > 0 && (
          <span className="absolute -top-2 -left-2 bg-amber-400 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center shadow-sm">
            {sourceReferences.length}
          </span>
        )}
      </button>

      {/* Sidebar panel */}
      <div
        className={`fixed top-0 right-0 h-full bg-white z-30 flex flex-col transition-transform duration-300 ease-in-out shadow-2xl border-l border-gray-200 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        } w-[calc(100vw-2rem)] max-w-sm sm:w-80 md:w-96`}
      >
        {/* Header */}
        <div className="flex-shrink-0 bg-white border-b border-gray-100 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-red-50 rounded-md p-1.5">
                <BookOpen className="w-4 h-4 text-red-600" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-800 leading-none">Tài liệu tham khảo</h3>
                {sourceReferences.length > 0 && (
                  <p className="text-xs text-gray-400 mt-0.5">{sourceReferences.length} tài liệu liên quan</p>
                )}
              </div>
            </div>
            <button
              onClick={onToggle}
              className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
          {sourceReferences.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-300 py-16">
              <FileSearch className="w-10 h-10 mb-3" />
              <p className="text-sm text-center text-gray-400">
                Chưa có tài liệu tham khảo.
              </p>
              <p className="text-xs text-center text-gray-300 mt-1">
                Hãy đặt câu hỏi để xem nguồn tài liệu.
              </p>
            </div>
          ) : (
            sourceReferences.map((ref, index) => {
              const scoreStyle = getScoreStyle(ref.relevance_score);
              const isExpanded = expandedIndex === index;
              const isCopied = copiedIndex === index;

              return (
                <div
                  key={ref.chunk_id || index}
                  className="group bg-white border border-gray-200 rounded-xl overflow-hidden hover:border-gray-300 hover:shadow-sm transition-all duration-200"
                >
                  {/* Relevance bar */}
                  <div className={`h-0.5 ${scoreStyle.bar}`} style={{ width: `${formatScore(ref.relevance_score)}%` }} />

                  {/* Card body */}
                  <div className="p-3">
                    <div className="flex items-start gap-2.5">
                      <div className={`flex-shrink-0 rounded-lg p-1.5 mt-0.5 ${scoreStyle.bg}`}>
                        <FileText className={`w-3.5 h-3.5 ${scoreStyle.text}`} />
                      </div>

                      <div className="flex-1 min-w-0">
                        <p
                          className="text-xs font-semibold text-gray-800 leading-snug line-clamp-2"
                          title={getDocumentDisplayName(ref.filename)}
                        >
                          {getDocumentDisplayName(ref.filename)}
                        </p>

                        <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                          <span className={`inline-flex items-center text-xs font-medium px-1.5 py-0.5 rounded-md ${scoreStyle.bg} ${scoreStyle.text}`}>
                            {formatScore(ref.relevance_score)}%
                          </span>
                          {ref.page_number && (
                            <span className="inline-flex items-center text-xs text-gray-400 bg-gray-50 px-1.5 py-0.5 rounded-md border border-gray-100">
                              Trang {ref.page_number}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Quick actions */}
                      <div className="flex-shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => onOpenDocument(ref.filename, ref.page_number || undefined)}
                          className="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                          title="Xem PDF"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleCopyReference(ref, index)}
                          className="p-1.5 rounded-md text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                          title="Sao chép trích dẫn"
                        >
                          {isCopied ? (
                            <Check className="w-3.5 h-3.5 text-emerald-500" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Snippet */}
                    {ref.content_snippet && (
                      <p className="text-xs text-gray-500 mt-2 leading-relaxed line-clamp-2">
                        {ref.content_snippet}
                      </p>
                    )}

                    {/* Expand toggle */}
                    {(ref.full_content || ref.heading) && (
                      <button
                        onClick={() => toggleExpand(index)}
                        className="mt-2 flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        {isExpanded ? (
                          <>
                            <ChevronUp className="w-3 h-3" />
                            Thu gọn
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-3 h-3" />
                            Xem thêm
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Expanded content */}
                  {isExpanded && (
                    <div className="border-t border-gray-100 bg-gray-50 px-3 py-3">
                      {ref.heading && (
                        <p className="text-xs font-medium text-gray-500 mb-2">
                          Mục: <span className="text-gray-700">{ref.heading}</span>
                        </p>
                      )}
                      <p className="text-xs text-gray-600 leading-relaxed max-h-36 overflow-y-auto whitespace-pre-wrap">
                        {ref.full_content}
                      </p>
                      {/* Action row inside expanded */}
                      <div className="flex items-center gap-2 mt-3">
                        <button
                          onClick={() => onOpenDocument(ref.filename, ref.page_number || undefined)}
                          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-white bg-red-600 hover:bg-red-700 transition-colors"
                        >
                          <Eye className="w-3 h-3" />
                          Xem PDF
                        </button>
                        <button
                          onClick={() => handleCopyReference(ref, index)}
                          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-gray-600 bg-white border border-gray-200 hover:border-gray-300 hover:bg-gray-100 transition-colors"
                        >
                          {isCopied ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-500" />
                              Đã sao chép
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              Sao chép
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        {sourceReferences.length > 0 && (
          <div className="flex-shrink-0 px-3 py-3 border-t border-gray-100 bg-white">
            <button
              onClick={onClear}
              className="w-full py-2 text-xs font-medium text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg border border-gray-200 flex items-center justify-center gap-1.5 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
              Xóa tài liệu tham khảo
            </button>
          </div>
        )}
      </div>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-[1px] z-20 md:hidden"
          onClick={onToggle}
        />
      )}
    </>
  );
};

export default DocumentSidebar;

