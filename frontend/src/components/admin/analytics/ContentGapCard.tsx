'use client';

import React from 'react';
import { AlertCircle, FileText, ArrowRight } from 'lucide-react';

interface ContentGap {
  topic: string;
  query_count: number;
  document_coverage: number;
  suggested_action: string;
}

interface ContentGapCardProps {
  gaps: ContentGap[];
  className?: string;
}

const ContentGapCard: React.FC<ContentGapCardProps> = ({ gaps, className = '' }) => {
  const getCoverageColor = (coverage: number) => {
    if (coverage >= 0.7) return 'bg-green-500';
    if (coverage >= 0.4) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getCoverageLabel = (coverage: number) => {
    if (coverage >= 0.7) return 'Tốt';
    if (coverage >= 0.4) return 'Trung bình';
    return 'Thiếu';
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {gaps.map((gap, index) => (
        <div
          key={index}
          className="border border-gray-200 rounded-lg p-4 hover:border-red-300 hover:bg-red-50/50 transition-colors"
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-orange-500" />
              <h4 className="font-medium text-gray-900">{gap.topic}</h4>
            </div>
            <span className="text-sm text-gray-500">
              {gap.query_count} lượt hỏi
            </span>
          </div>

          <div className="mb-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-600">Độ phủ tài liệu</span>
              <span className={`text-xs px-2 py-0.5 rounded-full text-white ${getCoverageColor(gap.document_coverage)}`}>
                {getCoverageLabel(gap.document_coverage)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${getCoverageColor(gap.document_coverage)}`}
                style={{ width: `${gap.document_coverage * 100}%` }}
              />
            </div>
          </div>

          <div className="flex items-start space-x-2 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
            <FileText className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <span className="font-medium text-gray-700">Đề xuất: </span>
              {gap.suggested_action}
            </div>
            <ArrowRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
          </div>
        </div>
      ))}
    </div>
  );
};

export default ContentGapCard;
