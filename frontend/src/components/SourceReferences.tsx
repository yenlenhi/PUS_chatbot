'use client';

import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, Book, Hash } from 'lucide-react';
import type { SourceReference } from '@/types';

interface SourceReferencesProps {
  sourceReferences: SourceReference[];
  onOpenDocument?: (filename: string, page?: number) => void;
  className?: string;
}

const SourceReferences: React.FC<SourceReferencesProps> = ({
  sourceReferences,
  onOpenDocument,
  className = ''
}) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (!sourceReferences || sourceReferences.length === 0) {
    return null;
  }

  const formatFileName = (filename: string) => {
    return filename
      .replace(/\.[^/.]+$/, '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatScore = (score: number) => {
    return Math.round(score * 100);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'bg-green-100 text-green-800';
    if (score >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const handleDocumentClick = (ref: SourceReference) => {
    if (onOpenDocument) {
      onOpenDocument(ref.filename, ref.page_number || undefined);
    }
  };

  const toggleExpand = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className={`mt-4 ${className}`}>
      <div className="border-t border-gray-200 pt-3">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs text-gray-500 font-semibold flex items-center gap-1">
            <Book className="w-3.5 h-3.5" />
            Nguồn tham khảo ({sourceReferences.length})
          </p>
        </div>
        
        <div className="space-y-2">
          {sourceReferences.map((ref, index) => (
            <div
              key={ref.chunk_id || index}
              className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-200"
            >
              {/* Header - Always visible */}
              <div
                onClick={() => handleDocumentClick(ref)}
                className="flex items-start gap-3 p-3 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div className="flex-shrink-0 mt-0.5">
                  <FileText className="w-5 h-5 text-red-500" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {formatFileName(ref.filename)}
                    </p>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getScoreColor(ref.relevance_score)}`}>
                      {formatScore(ref.relevance_score)}% phù hợp
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    {ref.page_number && (
                      <span className="flex items-center gap-1">
                        <Hash className="w-3 h-3" />
                        Trang {ref.page_number}
                      </span>
                    )}
                    {ref.heading && (
                      <span className="truncate max-w-[200px]" title={ref.heading}>
                        • {ref.heading}
                      </span>
                    )}
                  </div>
                  
                  {/* Snippet preview */}
                  <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                    {ref.content_snippet}
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={(e) => toggleExpand(index, e)}
                    className="p-1 hover:bg-gray-200 rounded transition-colors"
                    title={expandedIndex === index ? "Thu gọn" : "Xem thêm"}
                  >
                    {expandedIndex === index ? (
                      <ChevronUp className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    )}
                  </button>
                  <ExternalLink className="w-4 h-4 text-gray-400" />
                </div>
              </div>

              {/* Expanded content */}
              {expandedIndex === index && (
                <div className="px-3 pb-3 pt-0 border-t border-gray-100">
                  <div className="bg-gray-50 rounded p-3 mt-2">
                    <p className="text-xs text-gray-500 font-medium mb-2">Nội dung đầy đủ:</p>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {ref.full_content}
                    </p>
                  </div>
                  
                  {/* Score details */}
                  <div className="flex gap-4 mt-3 text-xs text-gray-500">
                    {ref.dense_score !== null && (
                      <span>Dense: {formatScore(ref.dense_score)}%</span>
                    )}
                    {ref.sparse_score !== null && (
                      <span>Sparse: {formatScore(ref.sparse_score)}%</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SourceReferences;

