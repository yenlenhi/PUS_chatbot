'use client';

import React, { useState } from 'react';
import {
  Book,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  FileText,
  Hash,
} from 'lucide-react';
import type { SourceReference } from '@/types';
import { getDocumentDisplayName } from '@/lib/documentNames';

interface SourceReferencesProps {
  sourceReferences: SourceReference[];
  onOpenDocument?: (filename: string, page?: number) => void;
  className?: string;
}

const SourceReferences: React.FC<SourceReferencesProps> = ({
  sourceReferences,
  onOpenDocument,
  className = '',
}) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (!sourceReferences || sourceReferences.length === 0) {
    return null;
  }

  const formatScore = (score: number) => Math.round(score * 100);

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'bg-green-100 text-green-800';
    if (score >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const handleDocumentClick = (ref: SourceReference) => {
    onOpenDocument?.(ref.filename, ref.page_number || undefined);
  };

  const toggleExpand = (index: number, event: React.MouseEvent) => {
    event.stopPropagation();
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className={`mt-4 ${className}`}>
      <div className="border-t border-gray-200 pt-3">
        <div className="mb-3 flex items-center justify-between">
          <p className="flex items-center gap-1 text-xs font-semibold text-gray-500">
            <Book className="h-3.5 w-3.5" />
            Nguon tham khao ({sourceReferences.length})
          </p>
        </div>

        <div className="space-y-2">
          {sourceReferences.map((ref, index) => (
            <div
              key={ref.chunk_id || index}
              className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:shadow-md"
            >
              <div
                onClick={() => handleDocumentClick(ref)}
                className="flex cursor-pointer items-start gap-3 p-3 transition-colors hover:bg-gray-50"
              >
                <div className="mt-0.5 flex-shrink-0">
                  <FileText className="h-5 w-5 text-red-500" />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="truncate text-sm font-medium text-gray-900">
                      {ref.display_name || getDocumentDisplayName(ref.filename)}
                    </p>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs ${getScoreColor(ref.relevance_score)}`}
                    >
                      {formatScore(ref.relevance_score)}% phu hop
                    </span>
                  </div>

                  <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                    {ref.page_number && (
                      <span className="flex items-center gap-1">
                        <Hash className="h-3 w-3" />
                        Trang {ref.page_number}
                      </span>
                    )}
                    {ref.heading && (
                      <span className="max-w-[200px] truncate" title={ref.heading}>
                        • {ref.heading}
                      </span>
                    )}
                    {ref.document_year && (
                      <span>Nam {ref.document_year}</span>
                    )}
                  </div>

                  <p className="mt-2 line-clamp-2 text-xs text-gray-600">
                    {ref.content_snippet}
                  </p>
                </div>

                <div className="flex flex-shrink-0 items-center gap-2">
                  <button
                    onClick={(event) => toggleExpand(index, event)}
                    className="rounded p-1 transition-colors hover:bg-gray-200"
                    title={expandedIndex === index ? 'Thu gon' : 'Xem them'}
                  >
                    {expandedIndex === index ? (
                      <ChevronUp className="h-4 w-4 text-gray-500" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-gray-500" />
                    )}
                  </button>
                  {ref.source_url ? (
                    <a
                      href={ref.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="rounded p-1 transition-colors hover:bg-gray-200"
                      onClick={(event) => event.stopPropagation()}
                      title="Nguon chinh thuc"
                    >
                      <ExternalLink className="h-4 w-4 text-gray-400" />
                    </a>
                  ) : (
                    <ExternalLink className="h-4 w-4 text-gray-400" />
                  )}
                </div>
              </div>

              {expandedIndex === index && (
                <div className="border-t border-gray-100 px-3 pb-3 pt-0">
                  <div className="mt-2 rounded bg-gray-50 p-3">
                    <p className="mb-2 text-xs font-medium text-gray-500">
                      Trich doan lien quan:
                    </p>
                    <p className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700">
                      {ref.content_snippet}
                    </p>
                  </div>

                  <div className="mt-3 flex gap-4 text-xs text-gray-500">
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
