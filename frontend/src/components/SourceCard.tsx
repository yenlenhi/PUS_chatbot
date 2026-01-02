'use client';

import React from 'react';
import { FileText, Download, ExternalLink, Star } from 'lucide-react';
import type { Source } from '@/types';
import { getDocumentUrl } from '@/lib/supabase';

interface SourceCardProps {
  source: Source;
  index: number;
  onDownload?: (source: Source) => void;
  onViewDetails?: (source: Source) => void;
}

const SourceCard: React.FC<SourceCardProps> = ({ 
  source, 
  index, 
  onDownload, 
  onViewDetails 
}) => {
  // Format filename to be more user-friendly
  const formatFilename = (filename: string): string => {
    // Remove file extension and replace underscores/hyphens with spaces
    return filename
      .replace(/\.(pdf|doc|docx|txt)$/i, '')
      .replace(/[_-]/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .trim()
      .replace(/\s+/g, ' ');
  };

  // Get confidence color based on score
  const getConfidenceColor = (confidence?: number): string => {
    if (!confidence) return 'bg-gray-100 text-gray-600';
    if (confidence >= 0.8) return 'bg-green-100 text-green-700';
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  // Get confidence text
  const getConfidenceText = (confidence?: number): string => {
    if (!confidence) return 'N/A';
    return `${Math.round(confidence * 100)}%`;
  };

  // Handle view document - open Supabase Storage URL
  const handleViewDocument = () => {
    const url = getDocumentUrl(source.filename || source.title);
    window.open(url, '_blank');
  };

  // Handle download document
  const handleDownloadDocument = () => {
    if (onDownload) {
      onDownload(source);
    } else {
      const url = getDocumentUrl(source.filename || source.title);
      window.open(url, '_blank');
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200 group">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2 flex-1 min-w-0">
          <div className="flex-shrink-0">
            <FileText className="w-5 h-5 text-red-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-medium text-gray-900 truncate">
              {formatFilename(source.filename || source.title)}
            </h4>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xs text-gray-500">
                Nguồn #{index + 1}
              </span>
              {source.page && (
                <>
                  <span className="text-xs text-gray-400">•</span>
                  <span className="text-xs text-gray-500">
                    Trang {source.page}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
        
        {/* Confidence Badge */}
        {source.confidence && (
          <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(source.confidence)}`}>
            <Star className="w-3 h-3" />
            <span>{getConfidenceText(source.confidence)}</span>
          </div>
        )}
      </div>

      {/* Content Preview */}
      {source.content && (
        <div className="mb-3">
          <p className="text-xs text-gray-600 line-clamp-2">
            {source.content.substring(0, 120)}...
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-2">
          <button
            onClick={onViewDetails ? () => onViewDetails(source) : handleViewDocument}
            className="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors duration-200"
          >
            <ExternalLink className="w-3 h-3" />
            <span>Xem chi tiết</span>
          </button>
          
          <button
            onClick={handleDownloadDocument}
            className="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors duration-200"
          >
            <Download className="w-3 h-3" />
            <span>Tải xuống</span>
          </button>
        </div>
        
        <div className="text-xs text-gray-400">
          {source.filename?.split('.').pop()?.toUpperCase() || 'PDF'}
        </div>
      </div>
    </div>
  );
};

export default SourceCard;
