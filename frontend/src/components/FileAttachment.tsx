'use client';

import React from 'react';
import { FileText, ExternalLink } from 'lucide-react';
import type { Source } from '@/types';

interface FileAttachmentProps {
  sources: Source[];
  className?: string;
}

const FileAttachment: React.FC<FileAttachmentProps> = ({ sources, className = '' }) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  const handleFileClick = (source: Source) => {
    // Create a more user-friendly notification
    const fileName = formatFileName(source.filename);

    // Show a notification that the file would be opened
    if (typeof window !== 'undefined') {
      // Create a temporary notification
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-300';
      notification.textContent = `Đang mở tài liệu: ${fileName}`;
      document.body.appendChild(notification);

      // Remove notification after 3 seconds
      setTimeout(() => {
        notification.remove();
      }, 3000);
    }

    // In a production environment, you would implement:
    // 1. File serving endpoint: window.open(`/api/files/${source.filename}`, '_blank');
    // 2. PDF viewer integration
    // 3. File download functionality
    console.log('File clicked:', source.filename);
  };

  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'pdf':
        return <FileText className="w-5 h-5 text-red-500" />;
      case 'doc':
      case 'docx':
        return <FileText className="w-5 h-5 text-blue-500" />;
      case 'txt':
        return <FileText className="w-5 h-5 text-gray-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  const formatFileName = (filename: string) => {
    // Remove file extension and replace underscores with spaces
    return filename
      .replace(/\.[^/.]+$/, '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  const getFileType = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();

    switch (extension) {
      case 'pdf':
        return 'PDF';
      case 'doc':
        return 'DOC';
      case 'docx':
        return 'DOCX';
      case 'txt':
        return 'TXT';
      default:
        return 'FILE';
    }
  };

  return (
    <div className={`mt-4 ${className}`}>
      <div className="border-t border-gray-200 pt-3">
        <p className="text-xs text-gray-500 mb-2 font-medium">Tài liệu tham khảo:</p>
        <div className="space-y-2">
          {sources.map((source, index) => (
            <div
              key={index}
              onClick={() => handleFileClick(source)}
              className="flex items-center space-x-3 p-2 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 cursor-pointer transition-all duration-200 hover:shadow-sm group"
            >
              <div className="flex-shrink-0">
                {getFileIcon(source.filename)}
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {formatFileName(source.filename)}
                </p>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-xs text-gray-500">
                    {getFileType(source.filename)}
                  </span>
                  {source.page && (
                    <>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-500">
                        Trang {source.page}
                      </span>
                    </>
                  )}
                  {source.confidence && (
                    <>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-xs text-gray-500">
                        {Math.round(source.confidence * 100)}% liên quan
                      </span>
                    </>
                  )}
                </div>
              </div>
              
              <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <ExternalLink className="w-4 h-4 text-gray-400" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FileAttachment;
