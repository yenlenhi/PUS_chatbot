'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen, Info } from 'lucide-react';
import SourceCard from './SourceCard';
import type { Source } from '@/types';

interface SourceSectionProps {
  sources: Source[];
  confidence?: number;
  onDownloadSource?: (source: Source) => void;
  onViewSourceDetails?: (source: Source) => void;
  className?: string;
}

const SourceSection: React.FC<SourceSectionProps> = ({
  sources,
  confidence,
  onDownloadSource,
  onViewSourceDetails,
  className = ''
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Don't render if no sources
  if (!sources || sources.length === 0) {
    return null;
  }

  // Convert string sources to Source objects if needed
  const normalizedSources: Source[] = sources.map((source) => {
    if (typeof source === 'string') {
      return {
        title: source,
        filename: source,
        confidence: confidence
      };
    }
    return source;
  });

  const handleToggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`mt-4 ${className}`}>
      {/* Header */}
      <div 
        className="flex items-center justify-between p-3 bg-gray-50 rounded-t-lg border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors duration-200"
        onClick={handleToggleExpanded}
      >
        <div className="flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">
            Nguồn tham khảo
          </span>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
            {normalizedSources.length}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          {confidence && (
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <Info className="w-3 h-3" />
              <span>Độ tin cậy: {Math.round(confidence * 100)}%</span>
            </div>
          )}
          
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          )}
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="border-l border-r border-b border-gray-200 rounded-b-lg bg-white">
          {/* Info Text */}
          <div className="p-3 border-b border-gray-100 bg-blue-50">
            <p className="text-xs text-blue-700 flex items-start space-x-2">
              <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
              <span>
                Thông tin trên được tham khảo từ các tài liệu chính thức của trường. 
                Bạn có thể xem chi tiết hoặc tải xuống để kiểm tra thêm.
              </span>
            </p>
          </div>

          {/* Sources Grid */}
          <div className="p-4">
            <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-1">
              {normalizedSources.map((source, index) => (
                <SourceCard
                  key={`${source.filename || source.title}-${index}`}
                  source={source}
                  index={index}
                  onDownload={onDownloadSource}
                  onViewDetails={onViewSourceDetails}
                />
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="px-4 py-3 bg-gray-50 rounded-b-lg border-t border-gray-100">
            <p className="text-xs text-gray-500 text-center">
              Tất cả tài liệu đều được cập nhật theo thông tin chính thức mới nhất của trường
            </p>
          </div>
        </div>
      )}

      {/* Collapsed Preview */}
      {!isExpanded && normalizedSources.length > 0 && (
        <div className="border-l border-r border-b border-gray-200 rounded-b-lg bg-white p-3">
          <div className="flex items-center space-x-2 text-xs text-gray-600">
            <span>Bao gồm:</span>
            <div className="flex flex-wrap gap-1">
              {normalizedSources.slice(0, 2).map((source, index) => (
                <span 
                  key={index}
                  className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-700"
                >
                  {source.filename?.replace(/\.(pdf|doc|docx)$/i, '') || source.title}
                </span>
              ))}
              {normalizedSources.length > 2 && (
                <span className="text-gray-500">
                  +{normalizedSources.length - 2} khác
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SourceSection;
